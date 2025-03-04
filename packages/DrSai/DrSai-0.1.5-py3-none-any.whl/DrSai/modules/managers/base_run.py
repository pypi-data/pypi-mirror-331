from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
import time
import json
import queue
import uuid
from .base_assistant import BaseObject
# from .base_thread import Thread
from ...utils import Logger
from DrSai.configs import CONST
from .base_run_step import ThreadRunStep
from DrSai.utils import EventCollector
logger = Logger.get_logger("base_run.py")



@dataclass
class Tool:
    type: str

    def to_dict(self):
        return self.__dict__

@dataclass
class Usage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    def to_dict(self):
        return self.__dict__

@dataclass
class TruncationStrategy:
    type: str
    last_messages: Optional[Any] = None  # 根据实际情况，这里可能需要调整类型

    def to_dict(self):
        return self.__dict__

@dataclass
class ThreadRun(BaseObject):
    id: str
    object: str
    created_at: int
    assistant_id: Union[str, List[str]]
    thread_id: str
    status: str
    started_at: int
    expires_at: Optional[int]
    cancelled_at: Optional[int]
    failed_at: Optional[int]
    completed_at: int
    last_error: Optional[Any]
    model: str
    instructions: Optional[Any]
    incomplete_details: Optional[Any]
    tools: List[Tool]
    metadata: Dict[str, Any]
    usage: Optional[Usage]
    temperature: float
    top_p: float
    max_prompt_tokens: int
    max_completion_tokens: int
    truncation_strategy: TruncationStrategy
    response_format: str
    tool_choice: str

    username: str = field(default=None)

    steps: List = field(default_factory=list)

    def __post_init__(self):
        super(ThreadRun, self).__post_init__()
        self._thread = None
        self._assistants: List = None

    @property
    def thread(self):
        if self._thread is None:
            from DrSai import THREADS_MGR
            self._thread = THREADS_MGR.retrieve_thread(self.thread_id, username=self.username)
        return self._thread
    
    @thread.setter
    def thread(self, thread):
        self._thread = thread
    
    @property
    def assistants(self):
        if self._assistants is None:
            from DrSai import ASSISTANTS_MGR
            if isinstance(self.assistant_id, str):
                assistant_ids = [self.assistant_id]
            else:
                assistant_ids = self.assistant_id
            # 获取所有的assistants
            self._assistants = [
                ASSISTANTS_MGR.retrieve_assistant(x, username=self.username)
                for x in assistant_ids]
        return self._assistants
    
    @assistants.setter
    def assistants(self, value):
        self._assistants = value
        
    @property
    def output_keys(self):
        """
        不包含thread和assistants字段
        """
        return ["id", "object", "created_at", "assistant_id", "thread_id", "status", "started_at", "expires_at",
                "cancelled_at", "failed_at", "completed_at", "last_error", "model", "instructions", "incomplete_details",
                "tools", "metadata", "usage", "temperature", "top_p", "max_prompt_tokens", "max_completion_tokens",
                "truncation_strategy", "response_format", "tool_choice", "username"]

    def start(self, run_func, **kwargs):
        self.status = "in_progress"
        self.started_at = int(time.time())
        self.thread.start(run_func, run=self, **kwargs)

    def to_dict(self, only_output_keys=True):
        new_dict = dict()
        for k, v in self.__dict__.items():
            if only_output_keys and k not in self.output_keys:
                continue
            if k == "tools" and v:
                v = [x.to_dict() for x in v]
            elif k == "usage" and v:
                v = v.to_dict()
            elif k == "truncation_strategy" and v:
                v = v.to_dict()
            new_dict[k] = v
        return new_dict
    
    # def event_generator(self, debug=True):
    #     """
    #     Run的事件生成器，用于流式输出run的事件对象
    #     """
    #     end_status = ["completed", "failed", "incomplete", "cancelled", "expired"]
    #     interval = CONST.EVENT_INTERVAL
    #     timeout = CONST.EVENT_TIMEOUT
    #     ctime = time.time()
    #     while True:
    #         ### 有事件时，直接返回
    #         if not self.queue.empty():
    #             yield self._queue.get()
    #             time.sleep(0.5)
    #             continue
    #         # 没有事件，看是否已经结束
    #         if self.status in end_status:
    #             break
    #         # 等待事件
    #         waited_time = time.time() - ctime
    #         if waited_time > timeout:
    #             break
    #         time.sleep(interval)
    #         if debug:
    #             logger.debug(f"Run {self.id} is waiting for event, {waited_time:.2f}s")     
    
    def construct_status_event(self, status=None):
        """根据状态构建事件对象"""
        status = status or self.status
        return {
            "data": self.to_dict(),
            "event": f"thread.run.{status}"
            }

    # def status_event(self, status=None):
    #     status = status or self.status
    #     yield f'data: {json.dumps(self.construct_status_event(status=status))}\n\n'

    @property
    def valid_status(self):
        return ["queued", "created", "requires_action", "in_progress", 
                "completed", "failed", "cancelling", "cancelled", "expired"]

    def create_run_step(self, **kwargs):
        run_step_type = kwargs.get("type", "message_creation")
        stream = kwargs.get("stream", False)
        # evc: EventCollector = kwargs.get("event_collector", None)
        assert run_step_type in ["message_creation", "tool_calls"], f"Invalid run step type: {run_step_type}"

        step_id = self.auto_id(prefix="step_", length=30)

        step = ThreadRunStep(
            id=step_id,
            object="thread.run.step",
            created_at=int(time.time()),
            run_id=self.id,
            assistant_id=self.assistant_id,
            thread_id=self.thread_id,
            type=run_step_type,
            status="created",
            step_details=None,
            usage=None
        )

        self.steps.append(step)
        
        # if stream and evc:
        #     evc.add_event_source(step.event_generator())  # 添加事件源
        #     step.set_status("created", emit=True)  # 设置状态，同时触发事件
        return step
