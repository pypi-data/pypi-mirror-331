
from typing import Any, List, Dict, Union, Optional, Literal, Callable, Generator
import os, sys, copy, json
from pathlib import Path
here = Path(__file__).parent
try:
    from DrSai.version import __version__
except:
    sys.path.append(str(here.parent.parent.parent))
    from DrSai.version import __version__

from DrSai.apis.utils_api import load_configs, logging_enabled, log_new_agent, get_llm_config
from DrSai.configs import CONST
from DrSai.apis.base_agent_api import AssistantAgent
from DrSai.apis.autogen_api import Agent, log_event, ConversableAgent

from openai import Stream

import inspect
from DrSai.apis.utils_api import Logger
logger = Logger.get_logger(__name__)

class Navigator(AssistantAgent):
    """
    功能：
        + arxiv等数据库搜索
        + 单次调用即可完成函数指定+调用, 直接回答自然语言。
    
    Creators:
        + HepAI Team - Zhang Bolun
    """

    DEFAULT_DESCRIPTION = "An navigator who can search for data from databases like arxiv."
    DEFAULT_SYSTEM_MESSAGE = "You can search the arxiv paper, website, or any other database by web search or API."

    def __init__(
        self,
        name: str,
        system_message: Optional[str] = "You are a helpful AI Assistant. Call the tools if you need.",
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        is_termination_msg: Optional[Callable[[Dict], bool]] = None,
        max_consecutive_auto_reply: Optional[int] = None,
        human_input_mode: Optional[str] = "NEVER",
        description: Optional[str] = None,
        **kwargs,
    ):      
        super().__init__(
            name,
            system_message=system_message,
            is_termination_msg=is_termination_msg,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            human_input_mode=human_input_mode,
            llm_config=llm_config,
            description=description,
            **kwargs,
        )
    
    def generate_reply(
        self,
        messages: Optional[List[Dict[str, Any]]] = None,
        sender: Optional["Agent"] = None,
        **kwargs: Any,
    ) -> Union[str, Dict, None]:
        if all((messages is None, sender is None)):
            error_msg = f"Either {messages=} or {sender=} must be provided."
            logger.error(error_msg)
            raise AssertionError(error_msg)

        if messages is None:
            messages = self._oai_messages[sender]

        # Call the hookable method that gives registered hooks a chance to process the last message.
        # Message modifications do not affect the incoming messages or self._oai_messages.
        messages = self.process_last_received_message(messages)

        # Call the hookable method that gives registered hooks a chance to process all messages.
        # Message modifications do not affect the incoming messages or self._oai_messages.
        messages = self.process_all_messages_before_reply(messages)

        # reset the function list
        self.register_reply([Agent, None], Navigator.generate_tool_calls_reply, remove_other_reply_funcs=True)
        self.register_reply([Agent, None], Navigator.a_generate_tool_calls_reply, ignore_async_in_sync_chat=True)
        self.register_reply([Agent, None], Navigator.generate_oai_reply)
        self.register_reply([Agent, None], Navigator.a_generate_oai_reply, ignore_async_in_sync_chat=True)

        messages_tmp = copy.deepcopy(messages)  # avoid modifying the original messages
        args_flag = True # mark if the arguments of tool_calls are obtained
        for reply_func_tuple in self._reply_func_list:
            reply_func = reply_func_tuple["reply_func"]
            if "exclude" in kwargs and reply_func in kwargs["exclude"]:
                continue
            if inspect.iscoroutinefunction(reply_func):
                continue
            if self._match_trigger(reply_func_tuple["trigger"], sender):
                args_flag = not args_flag
                try:
                    final, reply = reply_func(self, messages=messages_tmp, sender=sender, config=reply_func_tuple["config"], **kwargs)
                except Exception as e:
                    final, reply = reply_func(self, messages=messages_tmp, sender=sender, config=reply_func_tuple["config"])
                if logging_enabled():
                    log_event(
                        self,
                        "reply_func_executed",
                        reply_func_module=reply_func.__module__,
                        reply_func_name=reply_func.__name__,
                        final=final,
                        reply=reply,
                    )
                
                if not args_flag: # here the reply should be a generator containing the Dict of tool calls arguments
                    # append the obtained arguments as new messages to call tool_calls. This messages is a Dict from openai, not str!
                    content = self.convert_oai_stream_to_message_delta(reply)
                    if isinstance(content, Dict):
                        messages_tmp.append(content)
                        print("\033[92m" + f"Tool call arguments: {content}" + "\033[0m")
                        continue
                    else: # is a str, which means a general reply, not tool_calls arguments
                        return content

                if final and args_flag: # return tool calls results
                    reply = reply["content"]
                    output = reply
                    
                    return output
        return self._default_auto_reply
    
    def convert_oai_stream_to_message_delta(self, stream: Generator | Dict | str) -> Union[Dict, str]:
        
        """
        Support for Dicts in the stream, in addition to pure str.
        """

        tool_call_flag = False
        response = {
            "content": "", 
            "role": "", 
            "function_call": None,
            "tool_calls": [{
                "id": "",
                "function": {
                    "arguments": "",
                    "name": ""
                },
                "type": "", 
                "index": 0
            }]
        }

        if isinstance(stream, Dict):
            response = stream
            if response.get("tool_calls", None):
                tool_call_flag = True
        elif isinstance(stream, str):
            response["content"] = stream
        else: # openai_stream != Generator ???
            for i, x in enumerate(stream):
                content = x.choices[0].delta.content
                
                if x.choices[0].delta.tool_calls and not tool_call_flag: # tool call discovered. Update the response{} only once
                    tool_call_flag = True
                    response["role"] = x.choices[0].delta.role
                    response["tool_calls"][0]["id"] = x.choices[0].delta.tool_calls[0].id
                    response["tool_calls"][0]["function"]["name"] = x.choices[0].delta.tool_calls[0].function.name
                    response["tool_calls"][0]["type"] = x.choices[0].delta.tool_calls[0].type
                    response["tool_calls"][0]["index"] = x.choices[0].delta.tool_calls[0].index

                if tool_call_flag and x.choices[0].delta.tool_calls: # the last loop do not contain x.xxx.tool_calls
                    response["tool_calls"][0]["function"]["arguments"] += x.choices[0].delta.tool_calls[0].function.arguments
                elif content: # deal with pure text interaction
                    response["content"] += content
                    # send to front end
                    # data = self.construct_delta_event(content, id=x.id)
                    # yield f'data: {json.dumps(data)}\n\n'
                else:
                    continue

        full_response = response["content"] if not tool_call_flag else response
        return full_response