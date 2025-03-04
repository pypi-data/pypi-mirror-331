

import os, sys, re, copy, io
from typing import Dict, List, Optional, Tuple, Union, Generator
import json
from DrSai.apis.autogen_api import GroupChat, IOStream
from DrSai.apis.autogen_api import Agent, ConversableAgent
from .groupchat import GroupChatForHepAI, GroupChatWithTasks

from DrSai.apis.base_agent_api import LearnableAgent, HumanProxyAgent, HumanProxyAgentForStream
from DrSai.apis.base_objects import Thread
from DrSai.apis.base_objects import ThreadRun
from DrSai.apis.base_objects import ThreadMessage, Content, Text
from DrSai.apis.base_objects import ThreadRunStep
from DrSai.apis.base_objects import ThreadsManager
from DrSai.apis.base_objects import base_oai_manager

from openai import Stream
from hepai import Stream as Stream2

try:
    from termcolor import colored
except ImportError:
    def colored(x, *args, **kwargs):
        return x

from DrSai.apis.utils_api import Logger

logger = Logger.get_logger("groupchat_mgr.py")

class NoEligibleSpeakerException(Exception):
    """Exception raised for early termination of a GroupChat."""

    def __init__(self, message="No eligible speakers."):
        self.message = message
        super().__init__(self.message)
        
class HostAgent(LearnableAgent):
    """
    The host is an agent that can manage a group chat of multiple agents.
    1. 命令行中启动使用run_chat, 若需要人类参与自动化群聊, 需要使用HumanProxyAgent
    2. 
    3. 使用前端openai的assistants模式, 流式时需要使用run_chat_stream流式, 该模式兼容OpenAI的Assistants, 若需要人类参与自动化群聊, 需要使用HumanProxyAgentForStream, 以适配OpenAI的Assistants格式
    https://platform.openai.com/docs/api-reference/assistants
    """

    def __init__(
        self,
        groupchat: Union[GroupChatWithTasks, GroupChatForHepAI],
        name: Optional[str] = "chat_manager",
        # unlimited consecutive auto reply by default
        max_consecutive_auto_reply: Optional[int] = sys.maxsize,
        human_input_mode: Optional[str] = "NEVER",
        system_message: Optional[Union[str, List]] = "Group chat manager.",
        thread_run: Optional[ThreadRun] = None,
        chat_mode: Optional[str] = "once", # run_chat_stream的聊天模式 "once" or 'auto'
        backend_mode: Optional[str] = "completions", # 对应run_chat/run_chat_stream/run_chat_completions_stream的backend_model参数, 默认为completions, 可选参数为: "completions", "assistants", "autogen"
        **kwargs,
    ):
        if kwargs.get("llm_config") and (kwargs["llm_config"].get("functions") or kwargs["llm_config"].get("tools")):
            raise ValueError(
                "GroupChatManager is not allowed to make function/tool calls. Please remove the 'functions' or 'tools' config in 'llm_config' you passed in."
            )

        super().__init__(
            name=name,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            human_input_mode=human_input_mode,
            system_message=system_message,
            **kwargs,
        )
  
  
        # Store groupchat
        self._groupchat = groupchat

        self._chat_mode = chat_mode # run_chat_stream的聊天模式 "once" or 'auto', 默认为"once", 即只运行一次
        self._backend_mode = backend_mode # 对应run_chat/run_chat_stream/run_chat_completions_stream的backend_model参数, 默认为completions
        self.current_speakers = [] # 当前轮次的发言人

        self._thread_run: ThreadRun = thread_run # 模式兼容OpenAI的Assistants格式的ThreadRun对象
        self.threads_mgr: ThreadsManager = kwargs.get("threads_manager", None) # 模式兼容OpenAI的Assistants格式的ThreadsManager对象

        # Order of register_reply is important.
        # Allow sync chat if initiated using initiate_chat
        self.register_reply(
            Agent,
            HostAgent.run_chat_completions_stream,
            config=self._groupchat,
            reset_config=GroupChat.reset,
            )
        self.register_reply(
            Agent, 
            HostAgent.run_chat_stream, 
            config=self._groupchat, 
            reset_config=GroupChat.reset)
        self.register_reply(
            Agent, 
            HostAgent.run_chat, 
            config=self._groupchat, 
            reset_config=GroupChat.reset)
        # Allow async chat if initiated using a_initiate_chat
        self.register_reply(
            Agent,
            HostAgent.a_run_chat,
            config=self._groupchat,
            reset_config=GroupChat.reset,
            ignore_async_in_sync_chat=True,
        )

    def __repr__(self) -> str:
        return f'HostAgent(name="{self.name}", groupchat={self._groupchat})'

    @property
    def gc(self) -> GroupChat:
        return self._groupchat
    
    @property
    def groupchat(self) -> GroupChat:
        """Returns the group chat managed by the group chat manager."""
        return self._groupchat

    @property
    def thread_run(self) -> ThreadRun:
        """Returns the thread run object."""
        return self._thread_run

    def chat_messages_for_summary(self, agent: Agent) -> List[Dict]:
        """The list of messages in the group chat as a conversation to summarize.
        The agent is ignored.
        """
        return self._groupchat.messages

    def _prepare_chat(
        self,
        recipient: ConversableAgent,
        clear_history: bool,
        prepare_recipient: bool = True,
        reply_at_receive: bool = True,
    ) -> None:
        super()._prepare_chat(recipient, clear_history, prepare_recipient, reply_at_receive)

        # TODO: 这里的clear_history是否需要考虑?
        # if clear_history:
        #     self._groupchat.reset()

        for agent in self._groupchat.agents:
            if (recipient != agent or prepare_recipient) and isinstance(agent, ConversableAgent):
                agent._prepare_chat(self, clear_history, False, reply_at_receive)

    def _process_received_message(self, message: Union[Dict, str], sender: Agent, silent: bool):
        # When the agent receives a message, the role of the message is "user". (If 'role' exists and is 'function', it will remain unchanged.)
        super()._process_received_message(message, sender, silent)
        
    def set_status(self, obj, value, emit=False):
        """
        Set the status of one object.
        for ThreadRun object in stream mode, it will emit corresponding event to the event collector.
        """
        if obj is None:
            return
        if isinstance(obj, ThreadRun):
            obj.set_status(value, emit=emit)
        elif isinstance(obj, ThreadRunStep):
            obj.set_status(value, emit=emit)
        else:
            obj.set_status(value, emit=emit)

    def create_run_step_stream(self, run: ThreadRun, type: str = "message_creation"):
        run_step: ThreadRunStep = run.create_run_step(
            stream=self.stream,
            type=type,
        )
        yield from run_step.status_event("created", set_status=True)

        return run_step

    def speaker_event(self, speaker: Agent):
        data = {
            "data": speaker.name,
            "event": "thread.run.speaker"
        }
        yield f"data: {json.dumps(data)}\n\n"

    def run_chat_completions_stream(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[LearnableAgent] = None,
        config: Optional[GroupChat] = None,
    ) -> Generator:
        """
        Run a group chat.
        - 适配openai chat/completions
        https://platform.openai.com/docs/api-reference/chat
        """
        if self._backend_mode != "completions":
            return False, None
        
        groupchat: GroupChatForHepAI = config # 

        send_introductions = getattr(groupchat, "send_introductions", False)
        silent = getattr(self, "_silent", False)
        if send_introductions:
            # Broadcast the intro
            intro = groupchat.introductions_msg()
            for agent in groupchat.agents:
                self.send(intro, agent, request_reply=False, silent=True)
            # NOTE: We do not also append to groupchat.messages,
            # since groupchat handles its own introductions

        if self.client_cache is not None:
            for a in groupchat.agents:
                a.previous_cache = a.client_cache
                a.client_cache = self.client_cache

        speaker: LearnableAgent = sender
        # 开始聊天
        if self._chat_mode == "once":
            # #### 选择某一个speaker进行单轮聊天 ####
            if self._is_termination_msg(messages[-1]):
                return True, None
            
            ## 选 next speaker
            speaker: LearnableAgent = groupchat.select_speaker(speaker, self)
            speaker_str = f"`{speaker.name}` is speaking ...\n"
            logger.debug(colored(speaker_str, "yellow"))
            self.current_speakers = [speaker.name]
            
            if isinstance(speaker, HumanProxyAgent): # 目前在单轮对话中不需要考虑人类参与, 请根据自己的需要修改
                reply = "抱歉，不太明白您的意思，请您说的再具体一点。"
                yield from base_oai_manager.convert_str_to_oai_stream(reply)

            else:
                Reply_or_Gen: Union[str, Generator] = speaker.generate_reply(messages) 
                if isinstance(Reply_or_Gen, str): # 智能体返回是str
                    yield from base_oai_manager.convert_str_to_oai_stream(Reply_or_Gen)
                elif isinstance(Reply_or_Gen, Generator) or isinstance(Reply_or_Gen, Stream) or isinstance(Reply_or_Gen, Stream2):  # OpenAI.Stream流式输出
                    reply = yield from base_oai_manager.convert_Generator_to_oai_stream(Reply_or_Gen)
                elif isinstance(Reply_or_Gen, dict): # 智能体返回是dict, 目前只支持text类型
                    content = Reply_or_Gen.get("content", "")
                    yield from base_oai_manager.convert_str_to_oai_stream(content)
                else:
                    raise ValueError(f"Unsupported reply type: {type(Reply_or_Gen)}")
                

        else: # 自动模式
            # #### TODO: 多轮自动群聊 ####
            message = messages[-1]
            for i in range(groupchat.max_round):
                # 连续对话的结束条件, 可深度自定义群聊结束条件
                self._last_speaker = speaker
                # broadcast the message to all agents except the speaker
                for agent in groupchat.agents:
                    if agent != speaker:
                        self.send(message, agent, request_reply=False, silent=True)
                if self._is_termination_msg(message) or i == groupchat.max_round - 1:
                    # The conversation is over or it's the last round
                    break

                ## 选 next speaker
                speaker: LearnableAgent = groupchat.select_speaker(speaker, self) # 根据message和message_history选择下一个speaker
                speaker_str = f"`{speaker.name}` is speaking ...\n"
                logger.debug(colored(speaker_str, "yellow"))
                self.current_speakers = [speaker.name]
                
                if isinstance(speaker, HumanProxyAgent): # 人类无法参与, 请根据自己的需要修改
                    reply = f"请再选择一次，不能选择human "
                    message = {'content': reply, 'role': 'user', 'name': 'Human'}
                    self._append_oai_message(message=message, role="user",sender=speaker, is_sending=False)

                else:
                    Reply_or_Gen: Union[str, Generator] = speaker.generate_reply(messages) 
                    if isinstance(Reply_or_Gen, str): # 智能体返回是str
                        reply = Reply_or_Gen
                        yield from base_oai_manager.convert_str_to_oai_stream(Reply_or_Gen)
                    elif isinstance(Reply_or_Gen, Generator) or isinstance(Reply_or_Gen, Stream) or isinstance(Reply_or_Gen, Stream2):  # OpenAI.Stream流式输出
                        reply = yield from base_oai_manager.convert_Generator_to_oai_stream(Reply_or_Gen)
                    elif isinstance(Reply_or_Gen, dict): # 智能体返回是dict, 目前只支持text类型
                        reply = Reply_or_Gen.get("content", "")
                        yield from base_oai_manager.convert_str_to_oai_stream(reply)
                    else:
                        raise ValueError(f"Unsupported reply type: {type(Reply_or_Gen)}")
     
                
                # The speaker sends the message without requesting a reply
                speaker.send(reply, self, request_reply=False, silent=silent)
                message = self.last_message(speaker)
                groupchat.append(message, speaker)
                print(colored(f"\n`{speaker.name}`:\n{reply}", "yellow"))
        
        return True, None



    def run_chat_stream(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[LearnableAgent] = None,
        config: Optional[GroupChat] = None,
    ) -> Generator:
        """
        Run a group chat.
        - 适配OopenAI的Assistants模式, 以Thread/Run/RunStep的形式运行, 以保证后端消息与前端界面的同步
        https://platform.openai.com/docs/api-reference/assistants
        """
        
        if self._backend_mode != "assistants":
            return False, None

        assert self.stream is True, "The group chat manager must be in stream mode currently."

        groupchat: GroupChatWithTasks = config # 
        thread: Thread = groupchat.thread
        run: ThreadRun = self.thread_run
        thread_mgr: ThreadsManager = self.threads_mgr 

        # 可以通过assistant.metadata从前端获取按钮等信息
        # assistants_metadata = run.assistants[0].metadata

        send_introductions = getattr(groupchat, "send_introductions", False)
        silent = getattr(self, "_silent", False)
        if send_introductions:
            # Broadcast the intro
            intro = groupchat.introductions_msg()
            for agent in groupchat.agents:
                self.send(intro, agent, request_reply=False, silent=True)
            # NOTE: We do not also append to groupchat.messages,
            # since groupchat handles its own introductions

        if self.client_cache is not None:
            for a in groupchat.agents:
                a.previous_cache = a.client_cache
                a.client_cache = self.client_cache

        speaker = sender

        # 开始聊天
        yield from run.status_event("in_progress", set_status=True) 
        if self._chat_mode == "once":
            # #### 选择某一个speaker进行单轮聊天 ####
            if self._is_termination_msg(messages[-1]):
                yield from run.status_event("completed", set_status=True)
                return True, None
            run_step = yield from self.create_run_step_stream(run) # 为本轮对话创建一个run_step
            yield from run_step.status_event("in_progress", set_status=True) 

            ## 选 next speaker
            speaker: LearnableAgent = groupchat.select_speaker(speaker, self)
            speaker_str = f"`{speaker.name}` is speaking ...\n"
            logger.debug(colored(speaker_str, "yellow"))
            self.current_speakers = [speaker.name]

            ## 创建ThreadMessage, 用于保存到当前的Thread中
            th_msg: ThreadMessage = thread_mgr.create_message(
                    thread=thread,
                    role= speaker.name, ##"assistant",
                    content=[],
                    sender=speaker.name,
                    stream=self.stream,
                    # metadata={"test01": "test01"},
                    )
            yield from th_msg.status_event("created", set_status=True)
            yield from th_msg.status_event("in_progress", set_status=True)
            
            if isinstance(speaker, HumanProxyAgentForStream): # 目前在单轮对话中不需要考虑人类参与, 请根据自己的需要修改
                reply = "抱歉，不太明白您的意思，请您说的再具体一点。"
                reply2msd=Content(type="text", text=Text(value=reply,annotations=[]))
                th_msg.content = [reply2msd]
                yield from th_msg.convert_str_to_stream_message_delta(text=reply, chunk_size=5, sleep_time=0.05)
            else:
                Reply_or_Gen: Union[str, Generator] = speaker.generate_reply(messages) 
                if isinstance(Reply_or_Gen, str): # 智能体返回是str
                    reply2msd=Content(type="text", text=Text(value=Reply_or_Gen,annotations=[]))# 这里需要更新content，否则会导致ThreadMessage的content为空，导致无法发送消息
                    th_msg.content = [reply2msd]
                    reply = Reply_or_Gen
                    yield from th_msg.convert_str_to_stream_message_delta(text=Reply_or_Gen, chunk_size=5, sleep_time=0.05)
                else: #(Generator 对象, 目前只支持str和openai.Stream流式输出)
                    reply = yield from th_msg.convert_Generator_to_message_delta(Reply_or_Gen)
            yield from th_msg.status_event("completed", set_status=True) # 更新th_msg状态为completed
                
            print(colored(f"\n`{speaker.name}`:\n{reply}", "yellow"))
            yield from run_step.status_event("completed", set_status=True)
            thread.metadata['Stream_status'] = "run_close"
            yield from run.status_event("completed", set_status=True)

        else: # 自动模式
            message = messages[-1]
            # #### TODO: 多轮自动群聊 ####
            for i in range(groupchat.max_round):
                self._last_speaker = speaker
                # broadcast the message to all agents except the speaker
                for agent in groupchat.agents:
                    if agent != speaker:
                        self.send(message, agent, request_reply=False, silent=True)
                # 连续对话的结束条件, 可深度自定义群聊结束条件
                if self._is_termination_msg(message):
                    yield from run.status_event("completed", set_status=True)
                    break
                if i == groupchat.max_round - 1:
                    yield from run.status_event("incomplete", set_status=True)
                    break

                run_step = yield from self.create_run_step_stream(run) # 为本轮对话创建一个run_step标记
                yield from run_step.status_event("in_progress", set_status=True) 

                ## 选 next speaker
                speaker: LearnableAgent = groupchat.select_speaker(speaker, self) # 根据message和message_history选择下一个speaker
                speaker_str = f"`{speaker.name}` is speaking ...\n"
                logger.debug(colored(speaker_str, "yellow"))
                self.current_speakers = [speaker.name]

                ## 创建ThreadMessage, 用于保存到当前的Thread中
                th_msg: ThreadMessage = thread_mgr.create_message(
                        thread=thread,
                        role= speaker.name, ##"assistant",
                        content=[],
                        sender=speaker.name,
                        stream=self.stream,
                        # metadata={"test01": "test01"},
                        )
                yield from th_msg.status_event("created", set_status=True)
                yield from th_msg.status_event("in_progress", set_status=True)
                
                if isinstance(speaker, HumanProxyAgentForStream): # 人类参与群聊
                    reply = f"请{speaker.name}发言: "
                    reply2msd=Content(type="text", text=Text(value=reply,annotations=[]))
                    th_msg.content = [reply2msd]
                    yield from th_msg.convert_str_to_stream_message_delta(text=reply, chunk_size=5, sleep_time=0.05)
                    yield from th_msg.status_event("completed", set_status=True) # 更新th_msg状态为completed
                    ## 创建ThreadMessage用于人类输入
                    th_msg2: ThreadMessage = thread_mgr.create_message(
                        thread=thread,
                        role="user",
                        content=[],
                        sender=speaker.name,
                        stream=self.stream,
                        )
                    yield from th_msg2.status_event("created", set_status=True)
                    yield from th_msg2.status_event("in_progress", set_status=True)
                    human_input = yield from speaker.get_human_input(thread_message=th_msg2, prompt=reply, timeout=30)
                    yield from th_msg2.status_event("completed", set_status=True)
                    ## 将用户的反馈写入历史记录
                    if human_input == "No user input":
                        iostream = IOStream.get_default()
                        iostream.print(colored(f"\n>>>>>>>> {human_input}...","red",),flush=True,)

                    message = {'content': human_input, 'role': 'user', 'name': 'Human'}
                    reply += f"\n{speaker.name} says: {human_input}"

                else:
                    Reply_or_Gen: Union[str, Generator] = speaker.generate_reply(sender=self) 
                    if isinstance(Reply_or_Gen, str): # 智能体返回是str
                        reply2msd=Content(type="text", text=Text(value=Reply_or_Gen,annotations=[]))
                        th_msg.content = [reply2msd]
                        reply = Reply_or_Gen
                        yield from th_msg.convert_str_to_stream_message_delta(text=Reply_or_Gen, chunk_size=5, sleep_time=0.05)
                    else: #(Generator 对象, 目前只支持str和openai.Stream流式输出)
                        reply = yield from th_msg.convert_Generator_to_message_delta(Reply_or_Gen)
                        
                    yield from th_msg.status_event("completed", set_status=True) # 更新th_msg状态为completed
                
                # The speaker sends the message without requesting a reply
                speaker.send(reply, self, request_reply=False, silent=silent)
                message = self.last_message(speaker)
                groupchat.append(message, speaker)
                print(colored(f"\n`{speaker.name}`:\n{reply}", "yellow"))
                yield from run_step.status_event("completed", set_status=True)
                thread.metadata['Stream_status'] = "run_step_close" # 更新后端流式状态为run_close
            # 最后一轮对话结束, 更新Run状态为completed, 表示一次群聊结束
            thread.metadata['Stream_status'] = "run_close"
            yield from run.status_event("completed", set_status=True)
        
        return True, None
    

    def run_chat(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[GroupChat] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Run a group chat:
            - aotugen原生多智能体运行方式
        """
        if self._backend_mode != "autogen":
            return False, None
        
        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]
        speaker = sender
        groupchat = config
        send_introductions = getattr(groupchat, "send_introductions", False)
        silent = getattr(self, "_silent", False)

        if send_introductions:
            # Broadcast the intro
            intro = groupchat.introductions_msg()
            for agent in groupchat.agents:
                self.send(intro, agent, request_reply=False, silent=True)
            # NOTE: We do not also append to groupchat.messages,
            # since groupchat handles its own introductions

        if self.client_cache is not None:
            for a in groupchat.agents:
                a.previous_cache = a.client_cache
                a.client_cache = self.client_cache
        for i in range(groupchat.max_round):
            self._last_speaker = speaker
            groupchat.append(message, speaker)
            # broadcast the message to all agents except the speaker
            for agent in groupchat.agents:
                if agent != speaker:
                    self.send(message, agent, request_reply=False, silent=True)
            if self._is_termination_msg(message) or i == groupchat.max_round - 1:
                # The conversation is over or it's the last round
                break
            try:
                # select the next speaker
                speaker = groupchat.select_speaker(speaker, self)
                if not silent:
                    iostream = IOStream.get_default()
                    iostream.print(colored(f"\nNext speaker: {speaker.name}\n", "green"), flush=True)
                # let the speaker speak
                # output_buffer = io.StringIO()
                # sys.stdout = output_buffer
                reply = speaker.generate_reply(sender=self)
                # sys.stdout = sys.__stdout__
            except KeyboardInterrupt:
                # let the admin agent speak if interrupted
                if groupchat.admin_name in groupchat.agent_names:
                    # admin agent is one of the participants
                    speaker = groupchat.agent_by_name(groupchat.admin_name)
                    reply = speaker.generate_reply(sender=self)
                else:
                    # admin agent is not found in the participants
                    raise
            except NoEligibleSpeakerException:
                # No eligible speaker, terminate the conversation
                break

            if reply is None:
                # no reply is generated, exit the chat
                break

            # check for "clear history" phrase in reply and activate clear history function if found
            if (
                groupchat.enable_clear_history
                and isinstance(reply, dict)
                and reply["content"]
                and "CLEAR HISTORY" in reply["content"].upper()
            ):
                reply["content"] = self.clear_agents_history(reply, groupchat)

            # The speaker sends the message without requesting a reply
            speaker.send(reply, self, request_reply=False, silent=silent)
            message = self.last_message(speaker)
        if self.client_cache is not None:
            for a in groupchat.agents:
                a.client_cache = a.previous_cache
                a.previous_cache = None
        return True, None
    
    async def a_run_chat(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[GroupChat] = None,
    ):
        """Run a group chat asynchronously."""
        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]
        speaker = sender
        groupchat = config
        send_introductions = getattr(groupchat, "send_introductions", False)

        if send_introductions:
            # Broadcast the intro
            intro = groupchat.introductions_msg()
            for agent in groupchat.agents:
                self.a_send(intro, agent, request_reply=False, silent=True)
            # NOTE: We do not also append to groupchat.messages,
            # since groupchat handles its own introductions

        if self.client_cache is not None:
            for a in groupchat.agents:
                a.previous_cache = a.client_cache
                a.client_cache = self.client_cache

        # 新增更新任务
        self.groupchat.update_tasks(message, sender=sender, silent=True)

        for i in range(groupchat.max_round):
            groupchat.append(message, speaker)

            if self._is_termination_msg(message):
                # The conversation is over
                break

            # broadcast the message to all agents except the speaker
            for agent in groupchat.agents:
                if agent != speaker:
                    await self.a_send(message, agent, request_reply=False, silent=True)
            if i == groupchat.max_round - 1:
                # the last round
                break
            try:
                # select the next speaker
                speaker = await groupchat.a_select_speaker(speaker, self)
                # yield speaker
                # let the speaker speak
                reply = await speaker.a_generate_reply(sender=self)
            except KeyboardInterrupt:
                # let the admin agent speak if interrupted
                if groupchat.admin_name in groupchat.agent_names:
                    # admin agent is one of the participants
                    speaker = groupchat.agent_by_name(groupchat.admin_name)
                    reply = await speaker.a_generate_reply(sender=self)
                else:
                    # admin agent is not found in the participants
                    raise
            if reply is None:
                break
            # The speaker sends the message without requesting a reply
            await speaker.a_send(reply, self, request_reply=False)
            message = self.last_message(speaker)
            # yield True, speaker.name
        if self.client_cache is not None:
            for a in groupchat.agents:
                a.client_cache = a.previous_cache
                a.previous_cache = None
        return True, None
        # yield True, None

    def _raise_exception_on_async_reply_functions(self) -> None:
        """Raise an exception if any async reply functions are registered.

        Raises:
            RuntimeError: if any async reply functions are registered.
        """
        super()._raise_exception_on_async_reply_functions()

        for agent in self._groupchat.agents:
            agent._raise_exception_on_async_reply_functions()

    def clear_agents_history(self, reply: str, groupchat: GroupChat) -> str:
        """Clears history of messages for all agents or selected one. Can preserve selected number of last messages.
        That function is called when user manually provide "clear history" phrase in his reply.
        When "clear history" is provided, the history of messages for all agents is cleared.
        When "clear history <agent_name>" is provided, the history of messages for selected agent is cleared.
        When "clear history <nr_of_messages_to_preserve>" is provided, the history of messages for all agents is cleared
        except last <nr_of_messages_to_preserve> messages.
        When "clear history <agent_name> <nr_of_messages_to_preserve>" is provided, the history of messages for selected
        agent is cleared except last <nr_of_messages_to_preserve> messages.
        Phrase "clear history" and optional arguments are cut out from the reply before it passed to the chat.

        Args:
            reply (str): Admin reply to analyse.
            groupchat (GroupChat): GroupChat object.
        """
        # Split the reply into words
        words = reply.split()
        # Find the position of "clear" to determine where to start processing
        clear_word_index = next(i for i in reversed(range(len(words))) if words[i].upper() == "CLEAR")
        # Extract potential agent name and steps
        words_to_check = words[clear_word_index + 2 : clear_word_index + 4]
        nr_messages_to_preserve = None
        agent_to_memory_clear = None

        for word in words_to_check:
            if word.isdigit():
                nr_messages_to_preserve = int(word)
            elif word[:-1].isdigit():  # for the case when number of messages is followed by dot or other sign
                nr_messages_to_preserve = int(word[:-1])
            else:
                for agent in groupchat.agents:
                    if agent.name == word:
                        agent_to_memory_clear = agent
                        break
                    elif agent.name == word[:-1]:  # for the case when agent name is followed by dot or other sign
                        agent_to_memory_clear = agent
                        break
        # clear history
        if agent_to_memory_clear:
            if nr_messages_to_preserve:
                print(
                    f"Clearing history for {agent_to_memory_clear.name} except last {nr_messages_to_preserve} messages."
                )
            else:
                print(f"Clearing history for {agent_to_memory_clear.name}.")
            agent_to_memory_clear.clear_history(nr_messages_to_preserve=nr_messages_to_preserve)
        else:
            if nr_messages_to_preserve:
                print(f"Clearing history for all agents except last {nr_messages_to_preserve} messages.")
                # clearing history for groupchat here
                temp = groupchat.messages[-nr_messages_to_preserve:]
                groupchat.messages.clear()
                groupchat.messages.extend(temp)
            else:
                print("Clearing history for all agents.")
                # clearing history for groupchat here
                groupchat.messages.clear()
            # clearing history for agents
            for agent in groupchat.agents:
                agent.clear_history(nr_messages_to_preserve=nr_messages_to_preserve)

        # Reconstruct the reply without the "clear history" command and parameters
        skip_words_number = 2 + int(bool(agent_to_memory_clear)) + int(bool(nr_messages_to_preserve))
        reply = " ".join(words[:clear_word_index] + words[clear_word_index + skip_words_number :])

        return reply


    def get_status(self):
        """
        return the status of the group chat
        """
        agent_names = [agent.name for agent in self._groupchat.agents]
        # 无重名
        assert len(agent_names) == len(set(agent_names)), "There are agents with the same name in the group chat."

        status_each_agent = dict()
        for agent in self._groupchat.agents:
            status_each_agent[agent.name] = agent.get_status()

        status = {
            "agents": agent_names,
            "current_speakers": self.current_speakers,
        }
        status.update(status_each_agent)
        return status


    def get_message_url(self, reply: str) -> List[str]:
        """
        return the url of the message
        """
        pic_urls = re.findall(r'\<pic\: (.*?) \>', reply)
        pdf_urls = re.findall(r'\<pdf\: (.*?) \>', reply)
        return {"pic_urls": pic_urls, "pdf_urls": pdf_urls}

