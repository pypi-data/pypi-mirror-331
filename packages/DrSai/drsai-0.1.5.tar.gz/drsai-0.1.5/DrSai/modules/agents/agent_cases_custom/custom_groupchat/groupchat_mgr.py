import os, sys, re, copy
from typing import Dict, List, Optional, Tuple, Union, Generator
import json
from openai.types.chat import ChatCompletionChunk
from openai import Stream

from DrSai.apis.autogen_api import GroupChat
from DrSai.apis.autogen_api import Agent, ConversableAgent
from DrSai.apis.autogen_api import logging_enabled, log_new_agent
from DrSai.apis.base_agent_api import HumanProxyAgentForStream, LearnableAgent
from DrSai.apis.utils_api import load_configs
from DrSai.utils import str_utils
from DrSai.configs import CONST
from  DrSai.modules.agents.agent_cases_custom.custom_groupchat import action_host

from .groupchat import GroupChatWithTasks
from .tool_call_agent import ToolCallAgent
from .tasks import Task
from DrSai.apis.base_objects import Thread
from DrSai.apis.base_objects import ThreadRun, TruncationStrategy, Usage, Tool
from DrSai.apis.base_objects import ThreadMessage, Content, Text
from DrSai.apis.base_objects import ThreadRunStep, StepDetails, MessageCreation
from DrSai.apis.base_objects import ThreadsManager
try:
    from termcolor import colored
except ImportError:
    def colored(x, *args, **kwargs):
        return x
# from inputimeout import inputimeout, TimeoutOccurred

from DrSai.apis.utils_api import Logger

logger = Logger.get_logger("groupchat_mgr.py")

class NoEligibleSpeakerException(Exception):
    """Exception raised for early termination of a GroupChat."""

    def __init__(self, message="No eligible speakers."):
        self.message = message
        super().__init__(self.message)
        
class HostAgent(ToolCallAgent):
    """The host is an agent that can manage a group chat of multiple agents."""

    DEFAULT_SYSTEM_MESSAGE = """你是Dr. Sai，一名擅长高能物理数据分析的科学助手，你的长处在于能够通过函数调用来咨询具备不同能力的专家获取专业的建议。
  你将看到一段聊天记录，其中可能涉及多个话题的讨论，每个参与者在发言前都会自报姓名。
  你作为讨论的主持者，需要参与到最新的话题的讨论当中去，为话题的焦点高效地提供最为全面和合适的回应。假如你认为自己的知识储备不足以提供合适的回答，那么你可以积极地向助手咨询，他们会提供专业的参考信息。当然，你也要辩证看待来自他们的建议，因为他们的意见也不一定完全正确。
  请记住，你主导着话题的走向。具体而言，你可以通过选择咨询不同的助手来给话题增加多个视角的信息，最后在你认为合适的时候，由你自己提供最终的包含所有有价值信息的回应内容。有时话题讨论陷入僵局，你也需要及时调整策略，即使回答内容不完善，也需要及时总结进展，给所有参与者共享经验教训。

  请充分理解上面的文字，明确你的工作内容。下面我将给你一些参考的行动步骤和注意事项：
  行动步骤：
    1.跟踪话题进展，理解话题焦点和讨论现状。
    2.选择合适的行动方向，决定是咨询助手，还是自行作答。
      - 若选择咨询助手，确保你想要选择的助手的能力范围内能够提供有价值的信息帮助你思考。
      - 若选择自行作答，请确保自己有足够的知识储备和能力来回答问题，并直接以第一人称描述你的方案。
        **你的发言应该基于其他参与者的讨论内容，要完整涵盖参考的具体内容以及最终的解决方案，不能仅仅局限于补充或评价别人的意见。请确保你的发言能使读者不依靠其他的任何资料就能完整理解你的方案，即使这意味着重复别人的观点。**
        另外，禁止在回复开头称述你的名字，也不要提及任何具体信息来源。When answering, use the language initially used by the topic provider, unless otherwise specified. 
  注意事项：
    - **禁止连续(两次及以上)咨询同一个助手**，因为如果你的请求内容变化不大，助手给出的信息也是同质化的，没有参考价值。

  我相信你的能力，对待这份工作请务必充分地思考，灵活应对遇到的各种情况，在高效和满意的结果之间找到平衡，给话题的参与者带来最佳的讨论体验，这对我，对任何人都很重要，谢谢你的帮助！
  Now, please take a breathe and be ready to check the discussion content of some topics:
"""

    def __init__(
        self,
        groupchat: GroupChatWithTasks,
        name: Optional[str] = "DrSai",
        # unlimited consecutive auto reply by default
        max_consecutive_auto_reply: Optional[int] = sys.maxsize,
        human_input_mode: Optional[str] = "NEVER",
        system_message: Optional[Union[str, List]] = None,
        thread_run: Optional[ThreadRun] = None,
        **kwargs,
    ):
        if kwargs.get("llm_config") and (kwargs["llm_config"].get("functions") or kwargs["llm_config"].get("tools")):
            raise ValueError(
                "GroupChatManager is not allowed to make function/tool calls. Please remove the 'functions' or 'tools' config in 'llm_config' you passed in."
            )
        
        # if system_message.endswith('.yaml'):
        #     self.prompt_template = load_configs(system_message)
        #     system_message = self.prompt_template['system']

        if system_message is None:
            system_message = self.DEFAULT_SYSTEM_MESSAGE

        super().__init__(
            name=name,
            system_message=system_message,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            human_input_mode="NEVER",
            **kwargs,
        )
        # if logging_enabled():
        #     log_new_agent(self, locals())
            
        ## 注册函数
        action_host.all_tools(agent=self)

        # Store groupchat
        self._groupchat = groupchat if groupchat else GroupChatWithTasks()
        self._thread_run = thread_run 

        self.current_speakers = []

        self.threads_mgr: ThreadsManager = kwargs.get("threads_manager", None)

        # Order of register_reply is important.
        # Allow sync chat if initiated using initiate_chat
        self.register_reply(
            Agent, 
            HostAgent.run_chat_stream, 
            config=self._groupchat, 
            reset_config=GroupChatWithTasks.reset)
        # Allow async chat if initiated using a_initiate_chat
        self.register_reply(
            Agent,
            HostAgent.a_run_chat,
            config=self._groupchat,
            reset_config=GroupChatWithTasks.reset,
            ignore_async_in_sync_chat=True,
        )

        # import inspect
        # tmp = inspect.iscoroutinefunction(self.a_run_chat)
        # tmp2 = inspect.iscoroutinefunction(GroupChatManager.run_chat)
        # print(f'{tmp}, {tmp2}')
        # pass
        # tmp = inspect.isgeneratorfunction(self.run_chat_stream)
        # print(f'{tmp}')
        # exit()
        

    def __repr__(self) -> str:
        return f'HostAgent(name="{self.name}", groupchat={self._groupchat})'

    @property
    def gc(self) -> GroupChatWithTasks:
        return self._groupchat
    
    @property
    def groupchat(self) -> GroupChatWithTasks:
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

        if clear_history:
            self._groupchat.reset()

        for agent in self._groupchat.agents:
            if (recipient != agent or prepare_recipient) and isinstance(agent, ConversableAgent):
                agent._prepare_chat(self, clear_history, False, reply_at_receive)

    def _process_received_message(self, message: Union[Dict, str], sender: Agent, silent: bool):
        # When the agent receives a message, the role of the message is "user". (If 'role' exists and is 'function', it will remain unchanged.)
        super()._process_received_message(message, sender, silent)
        # 还需要进行任务的处理
        # self.groupchat.parse_tasks_from_message(message, sender, silent)

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
            #stream=self.stream,
            stream=True,
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

    ## mine ################################################################################################################################
    def send_message_to_frontend(self, message: Union[Generator, str], agent: Agent, groupchat: GroupChatWithTasks, update_tasks: bool = False) -> Union[Generator, str]:
        output = message

        ## 创建ThreadMessage用于输出到前端
        th_msg: ThreadMessage = self.threads_mgr.create_message(
                thread=groupchat.thread,
                role="assistant",
                content=[],
                sender=agent.name,
                stream=True,
            )
        yield from th_msg.status_event("created", set_status=True)
        yield from th_msg.status_event("in_progress", set_status=True)

        ## 判断消息类型 str | Stream (oai_stream)
        if isinstance(message, str):
            reply2msd=Content(type="text", text=Text(value=message,annotations=[])) # 更新content。若ThreadMessage的content为空，会导致无法发送消息
            th_msg.content = [reply2msd]
            yield from th_msg.convert_str_to_stream_message_delta(text=message, chunk_size=5, sleep_time=0.05) # 发送消息到前端
        elif isinstance(message, Stream):
            output = yield from th_msg.convert_oai_stream_to_message_delta(message)
        else:
            raise ValueError("The message should be a string or a generator of ChatCompletionChunk.")

        ## 更新th_msg状态为completed
        yield from th_msg.status_event("completed", set_status=True)

        ## 更新任务树
        if update_tasks:
            groupchat.update_tasks_from_message(th_msg)
        
        return output ## return str
    
    def convert_agentReply_to_str(self, message: Union[Generator, str]) -> str:
        if isinstance(message, str):
            return message
        elif isinstance(message, Stream):
            output = ""
            for i, x in enumerate(message):
                assert isinstance(x, ChatCompletionChunk), "The stream should be a generator of ChatCompletionChunk"
                content = x.choices[0].delta.content
                
                if content:
                    output += content
            
            return output
        else:
            raise ValueError("The AgentReply should be a string or a generator of ChatCompletionChunk.")

    #####################################################################################################################################

    def run_chat_stream(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[LearnableAgent] = None,
        config: Optional[GroupChat] = None,
    ) -> Generator:
        """Run a group chat."""
        #assert self.stream is True, "The group chat manager must be in stream mode."
        
        groupchat: GroupChatWithTasks = config
        thread: Thread = groupchat.thread
        run: ThreadRun = self.thread_run
        thread_mgr: ThreadsManager = self.threads_mgr # 在加载ThreadMessage时已经更新初始根任务

        # 从groupchat中找出HUMAN
        Human: HumanProxyAgentForStream = None
        for agent in groupchat.agents:
            if isinstance(agent, HumanProxyAgentForStream):
                Human = agent
                break
        if Human is None:
            raise ValueError("No human agent found in the groupchat.")

        # 从assistant_metadata中获取的信息
        # assistants_metadata = run.assistants[0].metadata

        send_introductions = getattr(groupchat, "send_introductions", False)
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

        ## 初始化speaker和messages。messages已经在human initial chat的时候加载过了
        speaker = sender # 初始化speaker为sender
        messages = [item for item in messages if item.get('name') != 'Human'] # 过滤掉human的消息，因为其中可能包含任务清单，会导致任务重复执行

        #### 开始多轮群聊 ####
        yield from run.status_event("in_progress", set_status=True)
        print(">>>>>>>>Start a new Round")
        # print(f"thread.messages:{thread.messages}")
        for i in range(groupchat.max_round): # 每一轮都处理一个任务       
            # 判断各种退出条件
            # if self._is_termination_msg(message):
            #     yield from run.status_event("teminated", set_status=True)
            #     break
            if i == groupchat.max_round - 1:
                yield from run.status_event("incomplete", set_status=True)
                break
            if groupchat.is_all_tasks_finished():
                yield from run.status_event("completed", set_status=True)
                break

            ## 任务状态更新
            logger.debug(f"[Round {i + 1:0>2}]")
            run_step = yield from self.create_run_step_stream(run) # 为本轮对话创建一个run_step
            yield from run_step.status_event("in_progress", set_status=True) 
            groupchat.current_task.status = "in_progress" # 将任务状态从queued更新为in_progress
            
            ## 从任务树中提取本轮需要处理的任务。以及其他消息处理。
            current_task_content = groupchat.current_task.content
            message_current_task = {"content": f"{Human.name}: {current_task_content}", "role": "user", "name": "TaskManager"} # role=user
            messages.append(message_current_task) # 将任务内容写入消息记录
            #message = messages[-1] # 这里初始化massage作为该轮任务开始，在groupchat循环时由循环内部更新message
            #groupchat.append(message, speaker) # 群聊历史记录中添加上一个speaker的message -- 弃用
            if CONST.DEBUG_BACKEND:
                print(colored(f"Current task: {groupchat.current_task.content}", "yellow"))

            # # 使用BESIII AI 或者 GroupChat +  timeout > 0时启用下面的人类介入
            # # chat_type = assistants_metadata.get("chat_type", "BESIII AI")
            # agent_function = assistants_metadata.get("functions", True)
            # timeout = int(assistants_metadata.get("human_reaction_time", 10)) if not CONST.DEBUG_BACKEND else 0 # {timeout}秒内人类输出未完成输入，则超时
            # if agent_function == "Groupchat" and timeout > 0:
            #     ## 让用户和user_proxy进行多轮对话确定任务列表。跳出循环的方式：用户不输入，超时，或者输入exit
            #     isTerminal = False
            #     while True:
            #         ## 更新messages用于选择speaker, 在agent发言后增加任务内容提示，以加强任务导向
            #         messages_for_speaker_selector = copy.deepcopy(messages) # 创建临时消息记录用于选择speaker
            #         message = {'content': f'The next task should be: "{groupchat.current_task.content}"', 'role': 'user', 'name': 'Human'}
            #         messages_for_speaker_selector.append(message) # 将用户的反馈写入历史记录
                    
            #         # select the next speaker
            #         speaker = groupchat.select_speaker(speaker, self, messages_for_speaker_selector)  # use messages to select speaker
            #         yield from self.speaker_event(speaker) # 生成一个speaker选择的事件，但目前（240624）并不被前端捕获输出
            #         logger.debug(colored(f"`{speaker.name}` is speaking ...", "yellow"))
            #         self.current_speakers = [speaker.name]

            #         ## 创建ThreadMessage用于输出到前端给人类判断是否介入
            #         th_msg00: ThreadMessage = thread_mgr.create_message(
            #             thread=thread,
            #             role="GroupChatManager",
            #             content=[],
            #             sender=speaker.name,
            #             stream=self.stream,
            #             )
            #         yield from th_msg00.status_event("created", set_status=True)
            #         yield from th_msg00.status_event("in_progress", set_status=True)
                    
            #         prompt = f"Please give feedback if you have any comments (in {timeout} seconds).\n1.'r' - Revise.   2.'c' - Continue.   3.'s' - Stop."
            #         ask_msg = f"Attention: auto-selected speaker '{speaker.name}' is ready to handle the current task: \n'{groupchat.current_task.content}'. \n\n{prompt}"
            #         ask_msg2msd=Content(type="text", text=Text(value=ask_msg,annotations=[]))# 这里需要更新content，否则会导致ThreadMessage的content为空，导致无法发送消息
            #         th_msg00.content = [ask_msg2msd]
            #         # data = th_msg0.construct_delta_event(ask_msg, id=0) 
            #         # yield f'data: {json.dumps(data)}\n\n'
            #         yield from th_msg00.convert_str_to_stream_message_delta(text=ask_msg, chunk_size=5, sleep_time=0.05)
            #         yield from th_msg00.status_event("completed", set_status=True) # 更新th_msg状态为completed

            #         ## 允许人类介入，获取人类输入
            #         ## 使用键盘事件判断用户是否想中断或干预, 在每次Groupchatmanager循环中留给键盘响应时间
            #         try:
            #             ## 创建ThreadMessage用于人类输入介入
            #             th_msg1: ThreadMessage = thread_mgr.create_message(
            #                 thread=thread,
            #                 role="user",
            #                 content=[],
            #                 sender=speaker.name,
            #                 stream=self.stream,
            #                 )
            #             yield from th_msg1.status_event("created", set_status=True)
            #             yield from th_msg1.status_event("in_progress", set_status=True)
            #             # human_input = inputimeout(colored(f"{prompt}", "red"), timeout=60) # terminal test
            #             human_input = yield from Human.get_human_input(thread_message=th_msg1, prompt=prompt, timeout=timeout)
            #             yield from th_msg1.status_event("completed", set_status=True)

            #             if human_input in ["exit", "stop", "quit", "e", "s", "q"]:
            #                 isTerminal = True
            #                 break # jump out of the while
            #             elif human_input in ["c", "No user input", None, "", "                  "]:      # press "Enter"/no input
            #                 break # jump out of the while
            #             else: 
            #                 ## 创建ThreadMessage用于人类输入对当前的任务列表进行修改
            #                 th_msg2: ThreadMessage = thread_mgr.create_message(
            #                     thread=thread,
            #                     role="user",
            #                     content=[],
            #                     sender=speaker.name,
            #                     stream=self.stream,
            #                     )
            #                 yield from th_msg2.status_event("created", set_status=True)
            #                 yield from th_msg2.status_event("in_progress", set_status=True)
            #                 # human_input = inputimeout(colored(f"{prompt}", "red"), timeout=60) # terminal test
            #                 human_input = yield from Human.get_human_input(thread_message=th_msg2, prompt=prompt, timeout=99999)
            #                 yield from th_msg2.status_event("completed", set_status=True)
            #                 ## 将用户的反馈写入历史记录
            #                 isHumanInput = True
            #                 message = {'content': human_input, 'role': 'user', 'name': 'Human'}
            #                 messages.append(message)

            #                 ## 更新任务列表，支持处理用户输入的任务列表修改
            #                 groupchat.update_tasks_from_message(th_msg2)
            #                 # 如是展示任务列表，则直接跳出循环
            #                 if 'show me the task list' in groupchat.current_task.content:
            #                     break
                                
            #                 # if groupchat.admin_name in groupchat.agent_names:
            #                 #     admin = groupchat.agent_by_name(groupchat.admin_name)
            #                 #     groupchat.append(message, admin) # 将用户的反馈写入群聊记录
            #                 # else: # userproxy not found
            #                 #     raise Exception("Admin agent not found in the GroupChat")

            #                 # prompt_user_proxy = messages
            #                 # prompt_user_proxy[-1]["content"] += f" The full task list is: {groupchat.tasks}. The user request is: {human_input}." # TODO: 修改提示词
                            
            #                 # ## 使用agent理解用户意图并生成任务列表
            #                 # message_to_userProxy = {'content': f" The full task list is: '{groupchat.tasks}'. The user request is: '{human_input}'.", 'role': 'user', 'name': 'Human'}
            #                 # reply_user_proxy = user_proxy.generate_reply(messages=[message_to_userProxy]) # 不用历史消息，因为user_proxy可能会对历史消息做出回应，导致重复拆分任务
            #                 # task_list = str_utils.split_to_list(reply_user_proxy) # [task_type, task1, task2]
            #                 # task_type = task_list.pop(0) # get the task category
                            
            #                 # ## 更新任务列表
            #                 # if task_type == "Add":
            #                 #     groupchat.update_tasks_from_message(th_msg2)
            #                 # else: # multiple tasks
            #                 #     ## 重置当前任务树
            #                 #     groupchat._current_task.parent_task = None
            #                 #     ## 判断当前任务是否完成：如果完成则切换下一个任务/添加新的子任务/所有任务完成
            #                 #     groupchat.update_tasks_from_message(th_msg2)
                                
            #                 # ## 更新记录user_proxy的消息 -- 没必要把任务制定的相关信息添加到群聊记录中，可能会影响speaker选择
            #                 # message = {'content': reply_user_proxy, 'role': 'assistant', 'name': user_proxy.name}
            #                 # messages.append(message) # 将user_proxy的反馈写入历史记录

            #                 # if groupchat.admin_name in groupchat.agent_names:
            #                 #     admin = groupchat.agent_by_name(groupchat.admin_name)
            #                 #     groupchat.append(message, admin) # 将user_proxy的反馈写入群聊记录
            #                 # else: # userproxy not found
            #                 #     raise Exception("Admin agent not found in the GroupChat")         
                                        
            #         except TimeoutOccurred: # no human interrupt
            #             break # jump out of the while

            #     if isTerminal or groupchat.is_all_tasks_finished(): # 如果用户主动退出，或者主动删除了最后一个任务，则跳出循环
            #         yield from run.status_event("completed", set_status=True)
            #         break # stop the conversation
            #     # if not isHumanInput and speaker.name != "Tester" and i != 0: # 没有人类介入，添加当前任务内容提示以强化任务导向。Tester的上一个任务需要是代码块，因此不加任务提示
            #     #     message = {'content': f"{groupchat.current_task.content}", 'role': 'user', 'name': 'Human'}
            #     #     messages.append(message)
            # # elif chat_type == "Personal assistant" and agent_function != "Groupchat": # 私人助理 直接选择下一个spearker
            # else: # 直接选 next speaker
            #     pass
            
            ## 针对单个任务，Host和agents多轮聊天，商讨出合适的答案
            messages_ideas = []
            messages_for_experts = []
            count = 0
            reply_host = ""
            
            while True:
                count += 1
                if count > 5: # 首先设置聊天轮数上限为5，防止死循环。
                    ## 获取Host的系统提示词
                    #agentlist = ", ".join([agent.name for agent in groupchat.agents if agent.name != "Human"])
                    #roles = groupchat._participant_roles(groupchat.agents)
                    # prompt_template = load_configs(f'{CONST.PROMPTS_DIR}/host.yaml')
                    #system_message_template = prompt_template['system']
                    #system_message = system_message_template.format(roles=roles)
                    system_message_summarizer = '''您的任务是总结一段任务执行记录，其中包含任务描述和做出的各种尝试信息。
  **请您以第一人称视角给出聊天记录中尝试过的解决方案，以及得到的具体结果的详细的总结性回复**。
  请确保您的回应语种与聊天记录中使用的语种保持一致。'''
                    host_summarizer = LearnableAgent(
                                name="summarizer",
                                system_message= system_message_summarizer,
                                llm_config=groupchat.llm_config,
                                human_input_mode="NEVER",
                            )
                    reply_host = host_summarizer.generate_reply(messages_for_experts) # 让独立的agent总结做过的尝试并输出
                    #raise Exception("Too many loops where Host consults experts, the conversation is stuck.")
                else:
                    ## Host生成回复
                    reply_host = self.generate_reply(messages=messages+messages_ideas, memory_config=False, stream=True)
                    
                    ## 流式模式时，即使tool_call返回的是字典，回复的内容也只会是字符串格式。这里尝试提取字典内容
                    try:
                        reply_host = json.loads(reply_host)
                    except:
                        pass # 下面兼容了纯字符串回复
                
                ## 若选择了专家，则让专家先说。若无，则让Host说。
                if isinstance(reply_host, Dict):
                    thoughts = reply_host.get("thoughts", "")
                    next_speaker_name = reply_host.get("expert", None)
                    request = reply_host.get("request", None)
                    
                    ## 把Host的想法输出到前端。也可以不输出
                    #yield from self.send_message_to_frontend(message=thoughts, agent=self, groupchat=groupchat)
                    #messages.append({'content': thoughts, 'role': 'assistant', 'name': self.name})

                    ## 让专家说话
                    if next_speaker_name in groupchat.agent_names:
                        speaker = groupchat.agent_by_name(next_speaker_name)
                    else:
                        raise AssertionError(f"Suggested agent: {next_speaker_name} not found")
                    
                    messages_for_experts.append({'content': f"{self.name}: "+request, 'role': 'user', 'name': self.name}) # 角色身份很重要，以assistant请求可能导致例如kimi不执行检索行为，返回空值

                    Reply_or_Gen = speaker.generate_reply(messages_for_experts, stream=True)

                    ## 处理特定agent的回复
                    task_type = ""
                    if speaker.name == "TaskManager":
                        ## TaskManager的回应不直接输出，而是根据回复的参数执行任务操作
                        reply_taskManager = self.convert_agentReply_to_str(Reply_or_Gen)
                        json_taskManager = str_utils.extract_json_content(reply_taskManager)
                        
                        task_type = json_taskManager.get("task_type", "insert")
                        tasks = json_taskManager.get("tasks", [])
                        if not tasks: # 如果没有子任务，那就把当前任务内容作为子任务
                            tasks = [request]
                        tasks.insert(0, task_type)
                        #print(colored(f"\n`{speaker.name}`:\n" + ', '.join(task for task in tasks), "yellow"))

                        ## 处理任务列表并更新任务树
                        result = groupchat.update_tasks_from_message(tasks)
                        Reply_or_Gen = result
                    
                    ## 将agent的回复流式输出到前端,兼容str和Generator两种类型
                    reply = yield from self.send_message_to_frontend(message=Reply_or_Gen, agent=speaker, groupchat=groupchat)

                    if task_type == "select":
                        reply = "The task tree has been updated successfully. The tasks tree has been shown." # 避免单条消除存在大量独立任务影响LLM判断
                    
                    ## messages添加agent回复, TODO: 截断messages的长度
                    #messages.append({'content': f"Response from expert '{speaker.name}':\n{reply}", 'role': 'assistant', 'name': speaker.name}) # name键值不会用于提示LLM，agent名字需要自己手动加入
                    messages_ideas.append({'content': f"{speaker.name}: {reply}", 'role': 'assistant', 'name': speaker.name})
                    messages_for_experts.append({'content': f"{speaker.name}: {reply}", 'role': 'assistant', 'name': speaker.name})
                    if CONST.DEBUG_BACKEND:
                        print(colored(f"\n`{speaker.name}`:\n{reply}", "yellow"))

                    if speaker.name == "TaskManager":
                        break # 跳出循环，结束该轮任务的讨论。因为TaskManager的执行结果不需要反思

                else: # 无专家建议，直接输出Host的最终回答，格式应为str
                    if CONST.DEBUG_BACKEND:
                        print(colored(f"\n`Host`:\n{reply_host}", "yellow"))
                    yield from self.send_message_to_frontend(message=reply_host, agent=self, groupchat=groupchat, update_tasks=True)
                    
                    messages.append({'content': f"{self.name}: {reply_host}", 'role': 'assistant', 'name': self.name})
                    messages_ideas.clear()
                    messages_for_experts.clear()
                    break


                # try: #即使重复强调，host仍然可能不以JSON回复
                #     #reply00 = str_utils.fix_json_string(reply_host) # 假如回复以{开头，但不是可解析的JSON格式，则尝试修复
                #     #reply0 = json.loads(reply00)
                #     reply0 = str_utils.extract_json_content(reply_host) 
                
                #     #logger.info(colored(f"auto-selected speaker: {reply}", "yellow"),)
                #     thoughts = reply0.get("thoughts", "")
                #     next_speaker_name = reply0.get("expert", None)
                #     request = reply0.get("request", None)
                #     answer = reply0.get("reply", None)
                    
                #     thoughts = str_utils.fix_newlines(thoughts) # 修复换行符
                #     answer = str_utils.fix_newlines(answer) # 修复换行符

                #     if next_speaker_name: # 如果有建议的agent，则更新speaker
                #         if next_speaker_name in groupchat.agent_names:
                #             speaker = groupchat.agent_by_name(next_speaker_name)
                #         else:
                #             raise AssertionError(f"Suggested agent: {next_speaker_name} not found")
                    
                #     ## 输出Host的回答
                #     reply_host_choice = answer if answer else thoughts
                #     if not isinstance(reply_host_choice, str): #以防LLM返回了字典/列表等非字符串类型
                #         reply_host_choice = str(reply_host_choice)
                    
                #     th_msg0: ThreadMessage = thread_mgr.create_message(
                #         thread=thread,
                #         role= host.name, ##"assistant",
                #         content=[],
                #         sender=host.name,
                #         stream=self.stream,
                #         )
                #     yield from th_msg0.status_event("created", set_status=True)
                #     yield from th_msg0.status_event("in_progress", set_status=True)
                #     yield from th_msg0.send_to_frontend(text=reply_host_choice)
                #     yield from th_msg0.status_event("completed", set_status=True) # 更新th_msg状态为completed
                #     message = {'content': reply_host_choice, 'role': 'assistant', 'name': host.name}
                #     messages.append(message)
                    
                #     message_for_agents = {'content': request, 'role': 'assistant', 'name': host.name}
                #     messages_for_experts.append(message_for_agents)
                    
                #     if next_speaker_name: ## 优先选择候选专家输出建议
                #         reply = ""
                #         ## 创建ThreadMessage输出agent的回复
                #         th_msg: ThreadMessage = thread_mgr.create_message(
                #             thread=thread,
                #             role= speaker.name, ##"assistant",
                #             content=[],
                #             sender=speaker.name,
                #             stream=self.stream,
                #             )
                #         yield from th_msg.status_event("created", set_status=True)
                #         yield from th_msg.status_event("in_progress", set_status=True)

                #         ## 让speaker生成回复
                #         # TODO:通过construct_delta_even中构造image字段，可以将image url发送给前端捕获
                #         if isinstance(speaker, HumanProxyAgent): # if speaker.name == 'Human':
                #             ##请求人类回答前，先给出提示
                #             request = f"For Human: {request}" if request else "Can not understand your query, please provide more details or modify the content."
                #             yield from th_msg.send_to_frontend(text=request)
                            
                #             reply = yield from speaker.get_human_input(thread_message=th_msg, prompt=request) # TODO：prompt不知为何不显示在前端
                #         else:
                #             Reply_or_Gen = speaker.generate_reply(messages_for_experts, stream=True)

                #             if isinstance(Reply_or_Gen, str): # 将str流式输出到前端
                #                 yield from th_msg.send_to_frontend(text=Reply_or_Gen)
                #                 reply = Reply_or_Gen
                #             else: #  isinstance(Reply_or_Gen, Generator) openai.Stream != Generator???
                #                 """
                #                 分两种情况:
                #                     1.LLM生成的是中间参数，需要先转成str再流式输出到前端
                #                     2.LLM生成的是最终回复，直接流式输出到前端
                #                 """
                #                 if speaker.name == "TaskManager":
                #                     reply = th_msg.convert_oai_stream_to_str(Reply_or_Gen)
                #                     json_taskManager = str_utils.extract_json_content(reply) 
                #                     #reply = str_utils.fix_json_string(reply)
                #                     #json_taskManager = json.loads(reply)
                #                     task_type = json_taskManager.get("task_type", "insert")
                #                     tasks = json_taskManager.get("tasks", [])
                                    
                #                     if not tasks: # 如果没有子任务，那就把当前任务内容作为子任务
                #                         tasks = [request]
                #                     tasks.insert(0, task_type)
                #                     #print(colored(f"\n`{speaker.name}`:\n" + ', '.join(task for task in tasks), "yellow"))

                #                     ## 处理任务列表并更新任务树
                #                     reply = groupchat.update_tasks_from_message(tasks)

                #                     ## 将reply发送到前端
                #                     yield from th_msg.send_to_frontend(text=reply)

                #                     if task_type == "select":
                #                         reply = "The task tree has been updated successfully. The tasks tree has been shown to the user." # 避免单条消除存在大量独立任务影响LLM判断
                #                 else: # 直接流式输出到前端
                #                     reply = yield from th_msg.convert_oai_stream_to_message_delta(Reply_or_Gen)

                                        
                #         ## agent回复完毕，结束th_msg
                #         yield from th_msg.status_event("completed", set_status=True) # 更新th_msg状态为completed
                        
                #         ## messages添加agent回复, TODO: 截断messages的长度 NOTE: 附加prompt后Coder无法正常
                #         print(colored(f"\n`{speaker.name}`:\n{reply}", "yellow"))
                #         message = {'content': f"Response from expert '{speaker.name}':\n{reply}", 'role': 'assistant', 'name': speaker.name} # name键值不会用于提示LLM，agent名字需要自己手动加入
                #         messages.append(message)
                #         messages_for_experts.append(message)

                #         if speaker.name == "TaskManager":
                #             break # 跳出循环，结束对话。因为TaskManager只执行不思考
                #     elif answer: ## 假如无候选专家且有Host的回答，则视为当前任务结束，跳转到下一个
                #         groupchat.update_tasks_from_message(th_msg0)
                #         break
                # except json.JSONDecodeError as e:
                #     if CONST.DEBUG_BACKEND:
                #         print(colored(f"Host generate_reply ERROR ({count}): {e}\nThe reply should be a parsable JSON):\n{reply_host}", "red"))
                    
                #     system_message_parser = prompt_template['parser']
                #     system_message_parser = system_message_parser.format(agentlist=agentlist)
                #     host_parser = LearnableAgent(
                #                 name="parser",
                #                 system_message= system_message_parser,
                #                 llm_config=groupchat.llm_config,
                #                 human_input_mode="NEVER",
                #             )
                #     ## 假如Host回答不是JSON（不以"{"开头），利用LLM提取一个JSON。不考虑手动，因为Host可能还没准备好最终回复而是想继续咨询。
                #     reply_host = host_parser.generate_reply(messages=[{'content': reply_host, 'role': 'assistant', 'name': host.name}], response_format = {"type": "json_object"})
                #     isUseHost = False
            
                # count = count + 1
                # if count > 5: # 超过5轮，则直接总结对话内容，替换Host回复给出回答
                #     system_message_summarizer = prompt_template['summarizer']
                #     host_summarizer = LearnableAgent(
                #                 name="summarizer",
                #                 system_message= system_message_summarizer,
                #                 llm_config=groupchat.llm_config,
                #                 human_input_mode="NEVER",
                #             )
                #     reply_host = host_summarizer.generate_reply(messages_for_experts, response_format = {"type": "json_object"})
                #     isUseHost = False
                #     #raise Exception("Too many loops where Host consults experts, the conversation is stuck.")
            
            ## 单轮对话结束
            # logger.debug(f"Thread.messages_end:{thread.messages}") # 当前thread的消息接口
            yield from run_step.status_event("completed", set_status=True)

        return True, None
    

    def run_chat(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[GroupChat] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Run a group chat."""
        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]
        speaker = sender
        
        groupchat: GroupChatWithTasks = config
        thread: Thread = groupchat.thread
        run: ThreadRun = self.thread_run
        thread_mgr: ThreadsManager = self.threads_mgr

        send_introductions = getattr(groupchat, "send_introductions", False)
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

        # 更新任务, Deprecated，在加载ThreadMessage时已经更新
        # self.groupchat.update_tasks(message, sender=sender, silent=True)
        if self.stream:
            event_collector = self.event_collector
    
        self.set_status(run, "in_progress")
        for i in range(groupchat.max_round):
            groupchat.append(message, speaker) # record the message+speaker.name
            # broadcast the message to all agents except the speaker
            for agent in groupchat.agents:
                if agent != speaker:
                    self.send(message, agent, request_reply=False, silent=True)
            # 判断各种退出条件
            if self._is_termination_msg(message):
                self.set_status(run, "teminated")
                break
            if i == groupchat.max_round - 1:
                self.set_status(run, "incomplete")
                break
            # if groupchat.is_all_tasks_finished():
            #     self.set_status(run, "completed")
            #     break

            #if groupchat.current_task:
            #        groupchat.current_task.status = "in_progress"
            
            #logger.debug(f"[Round {i + 1:0>2}], message: {message}")

            # select next speaker
            speaker = groupchat.select_speaker(speaker, self)
            if speaker is None:
                self.set_status(run, "completed")
                break
            
            next_speaker_name = speaker.name
            logger.debug(f"`{next_speaker_name}` is speaking...")
            #self.current_speakers = [speaker.name] ???
            logger.debug(f"last msg: {message}") ## delete after test
            reply = speaker.generate_reply(sender=self)
            # if next_speaker_name in groupchat.agent_names:
            #     speaker = groupchat.agent_by_name(next_speaker_name)
            #     reply = speaker.generate_reply(sender=self)
            # elif next_speaker_name == "Looks like there's nothing left to do. See you next time.":
            #     self.set_status(run, "completed")
            #     break
            # else:
            #     raise AssertionError(f"auto-selected agent: {next_speaker_name} not found")
            
            if reply is None:
                self.set_status(run, "completed")
                break
            if reply == "Looks like everything is done. See you next time.":
                self.set_status(run, "completed")
                break
            ## process last message with humanproxy
            # let the first speaker (userproxy) to speak

            # if groupchat.admin_name in groupchat.agent_names:
            #     speaker = groupchat.agent_by_name(groupchat.admin_name)
            #     reply = speaker.generate_reply(sender=self)
            # else: # userproxy not found
            #     raise

            # # 使用键盘事件判断用户是否想中断或干预, 在每次Groupchatmanager循环中留给键盘响应时间
            # try:
            #     # 5秒内未完成输入，则超时
            #     prompt='Press "Enter" if you want to revise (in 5 seconds), otherwise using auto-reply\n'
            #     flag = inputimeout(colored(f"{prompt}", "red"), timeout=5)
            # except TimeoutOccurred:
            #     flag = False
            
            # if flag == False: # no human input
            #     # let the first speaker (userproxy) to speak
            #     if groupchat.admin_name in groupchat.agent_names:
            #         speaker = groupchat.agent_by_name(groupchat.admin_name)
            #         reply = speaker.generate_reply(sender=self)


            # try:
            #     # 判断用户是否想要输入
            #     # user_is_input = group_is_termination()
            #     # if user_is_input == False: # if no input, then pick userproxy to generate auto-reply
            #     #     if groupchat.admin_name in groupchat.agent_names:
            #     #         speaker = groupchat.agent_by_name(groupchat.admin_name)
            #     #         reply = speaker.generate_reply(sender=self)
            #     #     else: # userproxy not found
            #     #         raise
            #     #     pass # go to next stage
            #     # else:
            #     #     reply = self.get_human_input(
            #     #             f"Please give feedback to {self.name}. Press 'Enter' or type 'exit' to continue or stop the conversation: "
            #     #         )
            #     #     if reply == "exit":
            #     #         break # stop the conversation
            #     #     else:
            #     #         # 将用户的干预作为人类写入记录
            #     #         for agent in groupchat.agents:
            #     #             if isinstance(agent, HumanProxyAgent):
            #     #                 message = {'content': reply, 'role': 'user', 'name': agent.name}
            #     #                 groupchat.append(message, agent)
            #     #                 break
                
            #     # select the next speaker
            #     #mgr_thoughts = self.generate_reply(message)#----------------------------------------------------------------
            #     #for agent in groupchat.agents:
            #     #    if mgr_thoughts == agent.name
            #     #        speaker = agent
            #     speaker = groupchat.select_speaker(speaker, self)  # speaker is an agent object
            #     logger.debug(f"`{speaker.name}` is speaking...")
            #     self.current_speakers = [speaker.name]

            #     reply = speaker.generate_reply(sender=self)
            #     pass
            # # except KeyboardInterrupt:
            # #     # let the admin agent speak if interrupted
            # #     if groupchat.admin_name in groupchat.agent_names:
            # #         # admin agent is one of the participants
            # #         speaker = groupchat.agent_by_name(groupchat.admin_name)
            # #         reply = speaker.generate_reply(sender=self)
            # #     else:
            # #         # admin agent is not found in the participants
            # #         raise
            # except NoEligibleSpeakerException:
            #     # No eligible speaker, terminate the conversation
            #     break

            # if reply is None:
            #     # no reply is generated, exit the chat
            #     # For example, human input `exit`
            #     self.set_status(run, "completed")
            #     break
            # elif reply == "Looks like there's nothing left to do. See you next time.":
            #     self.set_status(run, "completed")
            #     break

            # check for "clear history" phrase in reply and activate clear history function if found
            if (
                groupchat.enable_clear_history
                and isinstance(reply, dict)
                and "CLEAR HISTORY" in reply["content"].upper()
            ):
                reply["content"] = self.clear_agents_history(reply["content"], groupchat)
            # The speaker sends the message without requesting a reply
            speaker.send(reply, self, request_reply=False)
            message: Dict = self.last_message(speaker)


            # 更新任务和状态
            if thread_mgr:
                thread_message: ThreadMessage = thread_mgr.create_message(
                    thread=thread,
                    role=message["role"],
                    content=message["content"],
                    sender=speaker.name,
                    )
                groupchat.update_tasks_from_message(thread_message)
            # tasks = groupchat.parse_tasks_from_message(message)

            pass

        ### one round finished    
        if self.client_cache is not None:
            for a in groupchat.agents:
                a.client_cache = a.previous_cache
                a.previous_cache = None
        return True, None
    
    # def last_message(self, agent: LearnableAgent) -> Union[Dict, str]:
    #     # last_message = super().last_message(agent)
    #     # print(f"{agent.name}.last_message={agent._oai_messages}")
    #     last_message = agent.last_message(agent)
    #     # if agent.name == 'Planner':
    #     #     self.groupchat.update_tasks(last_message, sender=agent, silent=True)
    #         # last_message = self.groupchat.built_next_message_from_tasks()
    #     return last_message
 
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