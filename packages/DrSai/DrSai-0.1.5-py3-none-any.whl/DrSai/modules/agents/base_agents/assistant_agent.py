
from typing import Any, List, Dict, Union, Optional, Literal, Callable, Generator, Tuple
import os, sys, copy
from pathlib import Path
here = Path(__file__).parent


from DrSai.apis.base_agent_api import LearnableAgent
from DrSai.apis.base_agent_utils_api import HepAIWrapper
from DrSai.apis.autogen_api import (Agent, OpenAIWrapper,
                                  logging_enabled, log_new_agent)
from DrSai.configs import CONST
from DrSai.modules.agents.agent_utils.hepai_wrapper import  HepAIChatCompletionClient
import hepai
from hepai import HRModel, LRModel
from hepai import HepAI
import inspect
import logging
logger = logging.getLogger(__name__)


class AssistantAgent(LearnableAgent):
    """
    功能：
        + 可自定义回复函数worker_generate_reply, 深度开发消息列表的处理逻辑，支持传入其它任意参数
        + 可访问远程HepAI平台的远程无限函数worker，或者自定义消息列表处理类
    要求：
        + 无论是远程HepAI平台的远程无限函数worker还是自定义消息列表处理类, 都必须调用统一的interface函数接口进行消息列表处理
        + interface函数输出格式必须为纯文本/str生成器/openai stream 或者包括"content"字段的字典，如：{"status":str, "content":str, "image":base64},其他字段另加
        + 自定义回复函数worker_generate_reply自会在配置worker_name时才会生效
    """

    DEFAULT_SYSTEM_MESSAGE = """You are a helpful assisstant.""" 

    DEFAULT_DESCRIPTION = "A assistant agent that can interact with users and provide assistance."

    def __init__(
        self,
        name: str,
        system_message: Optional[str] = DEFAULT_SYSTEM_MESSAGE,
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        model_client: HepAIChatCompletionClient = None,
        is_termination_msg: Optional[Callable[[Dict], bool]] = None,
        max_consecutive_auto_reply: Optional[int] = None,
        human_input_mode: Optional[str] = "NEVER",
        description: Optional[str] = DEFAULT_DESCRIPTION,
        function_map: Optional[dict[str, Callable[..., Any]]] = None,
        tools: Optional[List[Callable[..., Any]]] = None,
        reply_function: Optional[Callable[..., Any]] = None, 
        only_reply_function: Optional[bool] = False, 
        **kwargs,
    ):
        '''
        reply_function: 自定义回复函数
        only_worker_reply: 是否只返回reply_function的回复，不使用其它的回复函数
        '''
        
        super().__init__(
            name,
            system_message=system_message,
            is_termination_msg=is_termination_msg,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            human_input_mode=human_input_mode,
            llm_config=llm_config,
            model_client=model_client,
            tools = tools,
            function_map=function_map,
            description=description,
            **kwargs,
        )

        if logging_enabled():
            log_new_agent(self, locals())
        
        # 判断是否使用自定义开发
        self.user_cofig: Dict = kwargs # 用户传递给自定义回复函数的自定义配置
        self.only_reply_function: bool = only_reply_function
        self.reply_function = reply_function
        if self.reply_function is None:
            pass
        else:
            self.register_reply([Agent, None], AssistantAgent.your_generate_reply)
    
    def your_generate_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[HepAIWrapper] = None,
        system_prompt: Optional[str] = None,
        **kwargs
        ) -> Tuple[bool, Union[str, Dict, None, Generator]]:
        '''
        + 将messages传递给reply_function进行处理
        + reply_function输出格式必须为纯文本/str生成器/openai stream 或者包括"content"字段的字典，如：{"status":str, "content":str, "image":base64},其他字段另加
        '''
        client = self.client if config is None else config
        if client is None:
            return False, None
        if messages is None:
            messages = self._oai_messages[sender]
        if system_prompt is None:
            system_message = self._oai_system_message
        else:
            if isinstance(system_prompt, str):
                system_message = [{"content": system_prompt, "role": "system"}]
            else:
                system_message = system_prompt
        
        kwargs.update(self.user_cofig)

        # RAG
        messages_rag = copy.deepcopy(system_message + messages)
        if self._memory_function is not None:
            messages_rag = copy.deepcopy(system_message + messages)
            try:
                messages_rag: List[Dict] = self._memory_function(messages_rag, **kwargs)
            except Exception as e:
                return True, f"Error: RAG function {self._memory_function.__name__} failed with error {e}."

        
        try:
            kwargs.update({"sender": sender, "client": client})
            result: Union[str, Dict, None, Generator] = self.reply_function(messages_rag, **kwargs)
            status = True
        except Exception as details:
            result =  f"Error: Custom function {self.reply_function.__name__} failed with error {details}."
            status = False

        if self.only_reply_function:
            return True, result
        else:
            return status, result
    
