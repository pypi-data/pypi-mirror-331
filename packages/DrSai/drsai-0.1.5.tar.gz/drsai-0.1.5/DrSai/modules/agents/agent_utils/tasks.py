
from typing import Dict, List, Optional, Literal
from datetime import datetime
import re

import uuid
from dataclasses import dataclass, field

from DrSai.modules.managers.base_assistant import BaseObject
import time


@dataclass
class Task(BaseObject):
    """
    (Dr.Sai) Task object for Planner, managing tasks, sub-tasks and plans.
    Automatically updates creation time, update time, and completion time.
    """
    id: str
    object: str
    created_at: int
    content: str  # 任务的具体内容
    source: str  # 任务来源
    status : Literal["queued", "in_progress", "completed", "continued"] = "queued"

    metadata: Dict[str, str] = field(default_factory=dict)  # 元数据，可以存储一些额外信息
    task_type: str = None
    parent_task: Optional['Task'] = None  # 父任务的ID
    sub_tasks: List['Task'] = field(default_factory=list)  # 子任务列表
    completed_at: Optional[int] = None
    solution: Optional[str] = None  # 解决方案

    def __post_init__(self):
        # TODO: 用一个Agent自动解析任务类型

        pass

    @property
    def allowed_update_keys(self):
        return ["content", "status", "metadata", "completed_at"]
    
    @property
    def task_level(self):
        """任务层级，parent为None时为1，否则为不断递归指导parent为None，记录递归次数"""
        if self.parent_task is None:
            return 1
        parent_task: Task = self.parent_task
        level = 1
        while parent_task.parent_task is not None:
            parent_task = parent_task.parent_task
            level += 1
        return level
        
    def __repr__(self) -> str:
        return f'Task(task="{self.content}", status="{self.status}")'
        
    
    @property
    def thoughts(self):
        return self.metadata.get("thoughts", "")

    @property
    def plan(self):
        return self.metadata.get("plan", "")
    
    @property
    def comment(self):
        return self.metadata.get("comment", "")
    
    # @property
    # def sub_tasks(self) -> List['Task']:
    #     return self.metadata.get("sub_tasks", [])
    
    def set_completed(self, solution: str = None):
        self.status = "completed"
        self.completed_at = int(time.time())
        self.solution = solution

    def update(self, **kwargs):
        """
        根据关键词更新任务的属性，例如status, thoughts, plan, comment等等
        : param update_steps: 是否更新plan的steps
        """
        update_steps = kwargs.pop("update_steps", True)
        plan_source = kwargs.pop("plan_source", None)
        # self.sub_task_source = plan_source
        self._auto_update_time = False
        for key, value in kwargs.items():
            setattr(self, key, value)
        self._updated_at = datetime.now()
        # if update_steps:
        #     self.update_subtasks_from_plan(**kwargs)
        self._auto_update_time = True

    # def update_subtasks_from_plan(self, **kwargs):
    #     # 更新plan的steps
    #     plan = self.plan
    #     source = kwargs.get("plan_source", self.sub_task_source)
    #     self._auto_update_time = False
    #     if plan in [None, "", "FINISH"]:
    #         steps = []
    #     else:
    #         steps = self.plan_str2list(kwargs["plan"])
    #     if not (source in ['Planner', "Human"]):
    #         raise ValueError(f"{source} is not a valid source. Must be 'Planner' or 'Human'.")
    #     sub_tasks = self.steps2subtasks(steps, source=source)
    #     self.sub_tasks.extend(sub_tasks)
    #     self._auto_update_time = True 
    
    def is_finished(self):
        return self.status.upper() in ["COMPLETED", "FINISHED"]
    
    # def plan_str2list(self, plan: str) -> List[str]:
    #     # return re.findall(r'\d+\) (.+?)\s*(?=\d+\)|$)', plan)
    #     steps = re.split(r'\(\d+\)\s|\n', plan)
    #     if steps and steps[0] == '':
    #         steps.pop(0)
    #     return steps
    
    # def steps2subtasks(self, steps: List[str], source: str = None) -> List['Task']:
    #     subtasks = [Task(task=step, parent=self, source=source) for step in steps]
    #     return subtasks