

from typing import List, Dict, Union, Optional, Any, Generator
from autogen.agentchat.conversable_agent import ConversableAgent
from dataclasses import dataclass, field
import ast
import damei as dm
import uuid
import time

from DrSai.apis.base_agent_utils_api import Task
from DrSai.apis.base_objects import Thread
from DrSai.apis.base_objects import ThreadMessage, Content, Text
from DrSai.apis.base_agent_api import LearnableAgent

from DrSai.configs import CONST
from DrSai.utils import Logger
from DrSai.apis.autogen_api import GroupChat, Agent

try:
    from termcolor import colored
except ImportError:
    def colored(x, *args, **kwargs):
        return x

logger = Logger.get_logger("groupchat.py")


@dataclass
class GroupChatForHepAI(GroupChat):
    '''
    - 使用LearnableAgent+提示词进行发言者自动选择
        - 需要在初始化的时候加入messages参数
        - 根据需要修改_auto_select_speaker函数, 特别是speaker_selector的提示词
    '''
    def __post_init__(self):
        super().__post_init__()
    
    @property
    def get_messages(self) -> List[Dict]:
        return self.messages
    
    # def _auto_select_speaker(
    #         self, 
    #         last_speaker: Agent, 
    #         selector: LearnableAgent, 
    #         messages: List[Dict] | None, 
    #         agents: List[Agent] | None) -> Agent:
    #     """
    #     自动选择发言者。替换父类的函数。
    #     1. 修改默认的Agent为haigen的LearnableAgent
    #     """
       
    #     if agents is None:
    #         agents = self.agents

    #     ## generate prompt for speaker selection
    #     roles = self._participant_roles(agents)
    #     agentlist = ", ".join([agent.name for agent in agents if agent.name != "Human"])
    #     sys_msg = f"""Last speaker was {last_speaker.name}. You need to choose the next speaker from the list [{agentlist}] based on messages in the conversation so far."""
    #     sys_msg += f"""\n\nAvailable roles and their descriptions:\n{roles}\n"""
    #     sys_msg += """\n\n**You must output the json style: {"speaker": "speaker_name"}.**"""

    #     speaker_selector = LearnableAgent(
    #         name="speaker_selector",
    #         system_message=sys_msg,
    #         llm_config=selector.llm_config,
    #         human_input_mode="NEVER",
    #     )
        
    #     reply = speaker_selector.generate_reply(messages=messages)

    #     try:
    #         next_speaker_name = ast.literal_eval(reply)["speaker"]
    #         # logger.info(colored(f"auto-selected speaker: {next_speaker_name}", "yellow"),)
    #     except:
    #         next_speaker_name = last_speaker.name
    #         logger.warning(colored(f"auto-selected speaker: {reply} is not a valid json style. Using last speaker: {next_speaker_name}", "red"),)
        

    #     if next_speaker_name in self.agent_names:
    #         speaker = self.agent_by_name(next_speaker_name)
    #         return speaker
    #     else:
    #         raise AssertionError(f"auto-selected agent: {next_speaker_name} not found")
    
    # def _participant_roles(self, agents: List[Agent] = None) -> str:
    #     # Default to all agents registered
    #     if agents is None:
    #         agents = self.agents

    #     roles = []
    #     for agent in agents:
    #         if agent.description.strip() == "":
    #             logger.warning(
    #                 f"The agent '{agent.name}' has an empty description, and may not work well with GroupChat."
    #             )
    #         roles.append(f"{agent.name}: {agent.description}".strip())
    #     return "\n".join(roles)
    def _create_internal_agents(
        self, agents, max_attempts, messages, validate_speaker_name, selector: Optional[LearnableAgent] = None
    ):
        checking_agent = LearnableAgent("checking_agent", default_auto_reply=max_attempts)

        # Register the speaker validation function with the checking agent
        checking_agent.register_reply(
            [LearnableAgent, None],
            reply_func=validate_speaker_name,  # Validate each response
            remove_other_reply_funcs=True,
        )

        # Override the selector's config if one was passed as a parameter to this class
        speaker_selection_llm_config = self.select_speaker_auto_llm_config or selector.llm_config

        # Agent for selecting a single agent name from the response
        speaker_selection_agent = LearnableAgent(
            "speaker_selection_agent",
            system_message=self.select_speaker_msg(agents),
            chat_messages={checking_agent: messages},
            llm_config=speaker_selection_llm_config,
            human_input_mode="NEVER",
            stream = False
            # Suppresses some extra terminal outputs, outputs will be handled by select_speaker_auto_verbose
        )

        # Register any custom model passed in select_speaker_auto_llm_config with the speaker_selection_agent
        self._register_custom_model_clients(speaker_selection_agent)

        return checking_agent, speaker_selection_agent

@dataclass
class GroupChatWithTasks(GroupChatForHepAI):
    '''
    - GroupChatWithTasks继承自GroupChatForHepAI, 增加了thread和tasks参数, 用于适配OpenAI ASSISTANTS的格式的后端消息保存与未来自动化群聊中的任务管理。
        - 从Thread中加载消息, 因此不需要在初始化的时候传入messages参数
        - TODO: 任务管理, 用于自动化任务执行中进行任务判断、任务分配和执行。
    '''
    thread: Thread = None
    messages: List[Dict] = None  # 这是OAI格式的messages
    tasks: List[Task] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        
        if self.thread:  
            messages: List[ThreadMessage]  = self.thread.messages
            # print(f"thread.messages={messages}")
            self.messages = [x.to_oai_message() for x in messages]

    
