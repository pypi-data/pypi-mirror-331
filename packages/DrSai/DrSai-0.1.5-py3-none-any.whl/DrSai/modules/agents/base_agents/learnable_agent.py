import copy

import inspect
from DrSai.apis.autogen_api import (
    OpenAIWrapper, Cache, ConversableAgent, Agent, ChatResult,
    consolidate_chat_info, AbstractCache, gather_usage_summary, logging_enabled, log_event
    )

from DrSai.apis.base_agent_utils_api import HepAIWrapper
from DrSai.apis.base_objects import base_oai_manager
from typing import Any,  Callable, Dict, List, Literal, Optional, Tuple,TypeVar, Union
from typing import Generator
import logging
import warnings
from DrSai.modules.agents.agent_utils.hepai_wrapper import  HepAIChatCompletionClient
from openai import Stream
from hepai import Stream as Stream2
from hepai.types import ChatCompletionChunk as ChatCompletionChunk2
from openai.types.chat import ChatCompletionChunk
try:
    from termcolor import colored
except ImportError:

    def colored(x, *args, **kwargs):
        return x

logger = logging.getLogger(__name__)
F = TypeVar("F", bound=Callable[..., Any])

def construct_openai_tool(
            Func: callable
            ) -> dict:
        '''
        构造openai的函数描述字典-tool
        '''
        # 获取函数的签名、参数和描述
        sig = inspect.signature(Func)
        params = sig.parameters
        description = Func.__doc__  # 获取函数描述
        function_name = Func.__name__  # 函数名称

        properties = {}

        for name, param in params.items():
            # 使用get_type_hints获取类型和描述
            annotation = param.annotation
            # 如果是Annotated，获取类型和描述
            if hasattr(annotation, "__metadata__"):
                param_description = annotation.__metadata__[0]  # 获取描述
                param_type = annotation.__args__[0]  # 获取类型
            else:
                param_description = "无描述"
                param_type = annotation
            param_detail = {
                "description": param_description,
                "type": "string"  # 默认类型设置为 string
            }

            # 根据参数类型进行判断并更新类型
            if param_type == str:
                param_detail["type"] = "string"
            elif param_type == int:
                param_detail["type"] = "integer"
            elif param_type == float:
                param_detail["type"] = "number"
            elif param_type == bool:
                param_detail["type"] = "boolean"
            elif param_type == dict:
                param_detail["type"] = "object"
            elif hasattr(param_type, '__origin__') and param_type.__origin__ is Literal:
                param_detail["enum"] = [*param_type.__args__]  # 枚举值
            elif param_type == tuple:
                param_detail["type"] = "array"
                param_detail["items"] = {"type": "string"}  # 假设是字符串数组，可以根据需要调整
            elif param_type == list:
                param_detail["type"] = "array"
                param_detail["items"] = {"type": "number"}  # 假设是数字数组，可以根据需要调整
            properties[name] = {**param_detail}
        
        # required_properties
        required_properties = [name for name, param in params.items() if (param.default is inspect.Parameter.empty) and (name != "kwargs")]  # 所有必需的参数
        
        tool = {
            "type": "function",
            "function": {
                "description": description,
                "name": function_name,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required_properties  # 所有必需的参数
                }
            }
        }

        return tool


class LearnableAgent(ConversableAgent):
    """
    说明：
        - 将所有需要openaiWrapper的部分使用HepAIWrapper替代，可方便地进行基座模型更换
        - 在generate_oai_reply中添加RAG的功能,  使用消息列表作为RAG的输入, memory_config = {"memory_function": memory_function, "memory_config": memory_config}:
          注意： memory_function是自定义的RAG函数, 其输入为消息列表和memory_config配置, 输出为包含RAG结果的消息列表, 需要用户自己在memory_function中对查询结果进行处理
        - 通过对reply_func的装饰器进行修改，使得可以支持 **kwargs
        - 添加了流式输出功能, 能够直接返回语言模型输出的OpenAI格式的流式对象, 但是必须使用initiate_chat_stream启动流式输出, 使用initiate_chat启动命令行输出
    """
    DEFAULT_SUMMARY_METHOD = "last_msg"


    def __init__(
        self,
        name: str,
        system_message: Optional[Union[str, List]] = "You are a helpful AI Assistant.",
        is_termination_msg: Optional[Callable[[Dict], bool]] = None,
        max_consecutive_auto_reply: Optional[int] = None,
        human_input_mode: Optional[str] = "TERMINATE",
        function_map: Optional[Dict[str, Callable]] = None,
        code_execution_config: Union[Dict, Literal[False]] = False,
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        model_client: HepAIChatCompletionClient = None,
        tools: Optional[List[Callable[..., Any]]] = None,
        default_auto_reply: Union[str, Dict] = "",
        description: Optional[str] = None,
        chat_messages: Optional[Dict[Agent, List[Dict]]] = None,
        memory_function: Optional[Callable] = None,  # config for the retrieve agent
        **kwargs,
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            is_termination_msg=is_termination_msg,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            human_input_mode=human_input_mode,
            function_map=function_map,
            code_execution_config=code_execution_config,
            llm_config=False,  # 传入None使父类初始化后的self.client=None
            default_auto_reply=default_auto_reply,
            description=description,
            chat_messages=chat_messages, # 必须初始化，否则无法传入  previous chat messages
        )
        # retrieve 设置
        self._memory_function: Optional[Callable] = memory_function # 

        # 注册tools
        if tools is not None:
            openai_tools =[ ]
            for func in tools:
                self.register_function({func.__name__: func})
                openai_tools.append(construct_openai_tool(func))
                

        # 用HepAIWarpper替代掉原来的OpenAIWrapper
        self.stream = kwargs.get("model_client_stream", False) # 是否指示其他智能体均流式输出

        if model_client is None:
            if (llm_config is False) or (llm_config is None):
                self.llm_config = False
                self.client = None
            else:
                self.llm_config = dict()
                if isinstance(llm_config, dict):
                    self.llm_config.update(llm_config)
                if "model" not in self.llm_config and (
                    not self.llm_config.get("config_list")
                    or any(not config.get("model") for config in self.llm_config["config_list"])
                ):
                    raise ValueError(
                        "Please either set llm_config to False, or specify a non-empty 'model' either in 'llm_config' or in each config of 'config_list'."
                        )
                if tools is not None:
                    self.llm_config["tools"] = openai_tools
                for i, _ in enumerate(self.llm_config.get("config_list", [])):
                    self.llm_config["config_list"][i]["stream"] = self.stream
                self.client = HepAIWrapper(**self.llm_config)
        else:
            self.model_client = model_client
            self.llm_config =  self.model_client.llm_config
            for i, _ in enumerate(self.llm_config.get("config_list", [])):
                    self.llm_config["config_list"][i]["stream"] = self.stream
            if tools is not None:
                self.llm_config["tools"] = openai_tools
            self.client =  self.model_client.create_hepai_client(self.llm_config)


        self.register_reply([Agent, None], LearnableAgent.generate_oai_reply, position=-2, ignore_async_in_sync_chat= True)


        for i, func in enumerate(self._reply_func_list):
            self._reply_func_list[i]["reply_func"] = self.reply_func_wrapper(func["reply_func"])

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(name="{self.name}")'
    
    def reply_func_wrapper(self, func: F) -> F:
        """
        A decorator to wrap a reply function to handle exceptions and return a tuple of (bool, Union[Dict, None]).
        """
        async def async_wrapper(
            self: "LearnableAgent",
            messages: Optional[List[Dict]] = None,
            sender: Optional[Agent] = None,
            config: Optional[Any] = None,
            **kwargs,
        ) -> Tuple[bool, Union[Dict, None]]:
            try:
                # 获取函数的签名
                sig = inspect.signature(func)
                # 检查函数是否支持 **kwargs
                if any(param.kind == inspect.Parameter.VAR_KEYWORD for param in sig.parameters.values()):
                    # 如果函数支持 **kwargs，直接调用
                    rst = await func(self, messages=messages, sender=sender, config=config, **kwargs)
                else:
                    # 如果不支持 **kwargs，调用时不传入 **kwargs
                    rst = await func(self, messages=messages, sender=sender, config=config)
                return rst
            except Exception as e:
                return (False, str(e))  # 可以选择在出现异常时返回 False 和异常信息

        def sync_wrapper(
            self: "LearnableAgent",
            messages: Optional[List[Dict]] = None,
            sender: Optional[Agent] = None,
            config: Optional[Any] = None,
            **kwargs,
        ) -> Tuple[bool, Union[Dict, None]]:
            try:
                # 获取函数的签名
                sig = inspect.signature(func)
                # 检查函数是否支持 **kwargs
                if any(param.kind == inspect.Parameter.VAR_KEYWORD for param in sig.parameters.values()):
                    # 如果函数支持 **kwargs，直接调用
                    rst = func(self, messages=messages, sender=sender, config=config, **kwargs)
                else:
                    # 如果不支持 **kwargs，调用时不传入 **kwargs
                    rst = func(self, messages=messages, sender=sender, config=config)
                return rst
            except Exception as e:
                return (False, str(e))  # 可以选择在出现异常时返回 False 和异常信息

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    def generate_oai_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[OpenAIWrapper] = None,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> Tuple[bool, Union[Generator, str, Dict, None]]:
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

        # RAG
        if self._memory_function is not None:
            messages_rag = copy.deepcopy(system_message + messages)
            try:
                messages_rag: List[Dict] = self._memory_function(messages_rag, **kwargs)
            except Exception as e:
                return True, f"Error: RAG function {self._memory_function.__name__} failed with error {e}."

            extracted_response = self._generate_oai_reply_from_client(
                client, messages_rag, self.client_cache, **kwargs
            )
        else:
            extracted_response = self._generate_oai_reply_from_client(
                    client, system_message + messages, self.client_cache, **kwargs
                )
        return (False, None) if extracted_response is None else (True, extracted_response)
        
    def _generate_oai_reply_from_client(self, llm_client: HepAIWrapper, messages, cache, **kwargs) -> Union[str, Dict, Generator, None]:
        # unroll tool_responses
        all_messages = []
        for message in messages:
            tool_responses = message.get("tool_responses", [])
            if tool_responses:
                all_messages += tool_responses
                # tool role on the parent message means the content is just concatenation of all of the tool_responses
                if message.get("role") != "tool":
                    all_messages.append({key: message[key] for key in message if key != "tool_responses"})
            else:
                all_messages.append(message)

        # TODO: #1143 handle token limit exceeded error
        HepAI = False
        if HepAI:
            response_str = llm_client.create(context=messages[-1].pop("context", None),
                messages=all_messages,
                cache=cache, )
            return response_str
        # 将所有的非'user', 'assistant', 'system' or 'function'改成'assistant'
        for message in all_messages:
            if message.get("role") not in ["user", "assistant", "system", "function"]:
                message["role"] = "assistant"
        response = llm_client.create(  # ChatCompletion
            context=messages[-1].pop("context", None),
            messages=all_messages,
            cache=cache,
            need_stream_obj=llm_client._config_list[0]["stream"],
            **kwargs,
        )
        if isinstance(response, Generator) or isinstance(response, Stream):
            return response
        extracted_response = llm_client.extract_text_or_completion_object(response)[0]

        if extracted_response is None:
            warnings.warn("Extracted_response from {response} is None.", UserWarning)
            return None
        # ensure function and tool calls will be accepted when sent back to the LLM
        if not isinstance(extracted_response, str) and hasattr(extracted_response, "model_dump"):
            extracted_response = extracted_response.model_dump()
        if isinstance(extracted_response, dict):
            if extracted_response.get("function_call"):
                extracted_response["function_call"]["name"] = self._normalize_name(
                    extracted_response["function_call"]["name"]
                )
            for tool_call in extracted_response.get("tool_calls") or []:
                tool_call["function"]["name"] = self._normalize_name(tool_call["function"]["name"])
        return extracted_response

    def generate_reply(
        self,
        messages: Optional[List[Dict[str, Any]]] = None,
        sender: Optional["Agent"] = None,
        **kwargs: Any,
    ) -> Union[str, Dict, None]:
        """Reply based on the conversation history and the sender.

        Either messages or sender must be provided.
        Register a reply_func with `None` as one trigger for it to be activated when `messages` is non-empty and `sender` is `None`.
        Use registered auto reply functions to generate replies.
        By default, the following functions are checked in order:
        1. check_termination_and_human_reply
        2. generate_function_call_reply (deprecated in favor of tool_calls)
        3. generate_tool_calls_reply
        4. generate_code_execution_reply
        5. generate_oai_reply
        Every function returns a tuple (final, reply).
        When a function returns final=False, the next function will be checked.
        So by default, termination and human reply will be checked first.
        If not terminating and human reply is skipped, execute function or code and return the result.
        AI replies are generated only when no code execution is performed.

        Args:
            messages: a list of messages in the conversation history.
            sender: sender of an Agent instance.

        Additional keyword arguments:
            exclude (List[Callable]): a list of reply functions to be excluded.

        Returns:
            str or dict or None: reply. None if no reply is generated.
        """
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

        if self._function_map:
            new_llm_config = copy.deepcopy(self.llm_config)
            for i, _ in enumerate(self.llm_config.get("config_list", [])):
                    new_llm_config["config_list"][i]["stream"] = False
            client =  self.model_client.create_hepai_client(new_llm_config)
            final, reply = self.generate_oai_reply(messages=messages, sender=sender, config=client, **kwargs)
            if final:
                messages_tmp = copy.deepcopy(messages)
                messages_tmp.append(reply)
                final, reply = self.generate_tool_calls_reply(messages=messages_tmp, config=client)
                if final:
                    return reply
                else:
                    return self._default_auto_reply
            else: 
                return self._default_auto_reply

        for reply_func_tuple in self._reply_func_list:
            reply_func = reply_func_tuple["reply_func"]
            if "exclude" in kwargs and reply_func in kwargs["exclude"]:
                continue
            if inspect.iscoroutinefunction(reply_func):
                continue
            if self._match_trigger(reply_func_tuple["trigger"], sender):
                final, reply = reply_func(self, messages=messages, sender=sender, config=reply_func_tuple["config"], **kwargs)
                if logging_enabled():
                    log_event(
                        self,
                        "reply_func_executed",
                        reply_func_module=reply_func.__module__,
                        reply_func_name=reply_func.__name__,
                        final=final,
                        reply=reply,
                    )
                if final:
                    return reply
        return self._default_auto_reply

    async def a_generate_reply(
        self,
        messages: Optional[List[Dict[str, Any]]] = None,
        sender: Optional["Agent"] = None,
        **kwargs: Any,
    ) -> Union[str, Dict[str, Any], None]:
        """(async) Reply based on the conversation history and the sender.

        Either messages or sender must be provided.
        Register a reply_func with `None` as one trigger for it to be activated when `messages` is non-empty and `sender` is `None`.
        Use registered auto reply functions to generate replies.
        By default, the following functions are checked in order:
        1. check_termination_and_human_reply
        2. generate_function_call_reply
        3. generate_tool_calls_reply
        4. generate_code_execution_reply
        5. generate_oai_reply
        Every function returns a tuple (final, reply).
        When a function returns final=False, the next function will be checked.
        So by default, termination and human reply will be checked first.
        If not terminating and human reply is skipped, execute function or code and return the result.
        AI replies are generated only when no code execution is performed.

        Args:
            messages: a list of messages in the conversation history.
            sender: sender of an Agent instance.

        Additional keyword arguments:
            exclude (List[Callable]): a list of reply functions to be excluded.

        Returns:
            str or dict or None: reply. None if no reply is generated.
        """
        if all((messages is None, sender is None)):
            error_msg = f"Either {messages=} or {sender=} must be provided."
            logger.error(error_msg)
            raise AssertionError(error_msg)

        if messages is None:
            messages = self._oai_messages[sender]

        # Call the hookable method that gives registered hooks a chance to process all messages.
        # Message modifications do not affect the incoming messages or self._oai_messages.
        messages = self.process_all_messages_before_reply(messages)

        # Call the hookable method that gives registered hooks a chance to process the last message.
        # Message modifications do not affect the incoming messages or self._oai_messages.
        messages = self.process_last_received_message(messages)

        for reply_func_tuple in self._reply_func_list:
            reply_func = reply_func_tuple["reply_func"]
            if "exclude" in kwargs and reply_func in kwargs["exclude"]:
                continue

            if self._match_trigger(reply_func_tuple["trigger"], sender):
                if inspect.iscoroutinefunction(reply_func):
                    final, reply = await reply_func(
                        self, messages=messages, sender=sender, config=reply_func_tuple["config"]
                    )
                else:
                    final, reply = reply_func(self, messages=messages, sender=sender, config=reply_func_tuple["config"], **kwargs)
                if final:
                    return reply
        return self._default_auto_reply


    def run(
        self,
        recipient: "ConversableAgent",
        clear_history: Optional[bool] = True,
        silent: Optional[bool] = False,
        cache: Optional[Cache] = None,
        max_turns: Optional[int] = None,
        **context,
    ) -> ChatResult:
        return self.initiate_chat(recipient=recipient, clear_history=clear_history, silent=silent, cache=cache, max_turns=max_turns, **context)
    
    async def a_run(
        self,
        recipient: "ConversableAgent",
        clear_history: bool = True,
        silent: Optional[bool] = False,
        cache: Optional[Cache] = None,
        max_turns: Optional[int] = None,
        summary_method: Optional[Union[str, Callable]] = "last_msg",
        summary_args: Optional[dict] = {},
        message: Optional[Union[str, Callable]] = None,
        **context,
    ) -> ChatResult:
        return await self.a_initiate_chat(
            recipient=recipient,
            clear_history=clear_history,
            silent=silent,
            cache=cache,
            max_turns=max_turns,
            summary_method=summary_method,
            summary_args=summary_args,
            message=message,
            **context,
        )
    
    def initiate_chat_stream(
            self,
            recipient: "ConversableAgent",
            clear_history: bool = True,
            silent: Optional[bool] = False,
            cache: Optional[AbstractCache] = None,
            max_turns: Optional[int] = None,
            summary_method: Optional[Union[str, Callable]] = DEFAULT_SUMMARY_METHOD,
            summary_args: Optional[dict] = {},
            message: Optional[Union[str, Callable]] = None,
            **kwargs,
        ) -> Generator:
        _chat_info = locals().copy()
        _chat_info["sender"] = self
        consolidate_chat_info(_chat_info, uniform_sender=self)
        for agent in [self, recipient]:
            agent._raise_exception_on_async_reply_functions()
            agent.previous_cache = agent.client_cache
            agent.client_cache = cache
        if isinstance(max_turns, int):
            self._prepare_chat(recipient, clear_history, reply_at_receive=False)
            for _ in range(max_turns):
                if _ == 0:
                    if isinstance(message, Callable):
                        msg2send = message(_chat_info["sender"], _chat_info["recipient"], kwargs)
                    else:
                        msg2send = self.generate_init_message(message, **kwargs)
                else:
                    msg2send = self.generate_reply(messages=self.chat_messages[recipient], sender=recipient)
                if msg2send is None:
                    break
                self.send(msg2send, recipient, request_reply=True, silent=silent)
        else:
            self._prepare_chat(recipient, clear_history)
            if isinstance(message, Callable):
                msg2send = message(_chat_info["sender"], _chat_info["recipient"], kwargs)
            else:
                msg2send = self.generate_init_message(message, **kwargs)
            yield from self.send_stream(msg2send, recipient, silent=silent)
        summary = self._summarize_chat(
            summary_method,
            summary_args,
            recipient,
            cache=cache,
        )
        for agent in [self, recipient]:
            agent.client_cache = agent.previous_cache
            agent.previous_cache = None
        chat_result = ChatResult(
            chat_history=self.chat_messages[recipient],
            summary=summary,
            cost=gather_usage_summary([self, recipient]),
            human_input=self._human_input,
        )
        return chat_result

    def get_status(self):
        
        agent_status = {
            "name": self.name,
            # "system_message": self.system_message,
            "description": self.description,
            "length_of_messages": len(self._oai_messages),
            # "status": self.status,
        }
        return agent_status

    
 
    def register_for_execution(
        self,
        name: Optional[str] = None,
    ) -> Callable[[F], F]:
        """Decorator factory for registering a function to be executed by an agent.

        It's return value is used to decorate a function to be registered to the agent.

        Args:
            name (optional(str)): name of the function. If None, the function name will be used (default: None).

        Returns:
            The decorator for registering a function to be used by an agent.

        Examples:
            ```
            @user_proxy.register_for_execution()
            @agent2.register_for_llm()
            @agent1.register_for_llm(description="This is a very useful function")
            def my_function(a: Annotated[str, "description of a parameter"] = "a", b: int, c=3.14):
                 return a + str(b * c)
            ```

        """
        return super().register_for_execution(name=name)

    def register_for_llm(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        api_style: Literal["function", "tool"] = "tool",
    ) -> Callable[[F], F]:
        """Decorator factory for registering a function to be used by an agent.

        It's return value is used to decorate a function to be registered to the agent. The function uses type hints to
        specify the arguments and return type. The function name is used as the default name for the function,
        but a custom name can be provided. The function description is used to describe the function in the
        agent's configuration.

        Args:
            name (optional(str)): name of the function. If None, the function name will be used (default: None).
            description (optional(str)): description of the function (default: None). It is mandatory
                for the initial decorator, but the following ones can omit it.
            api_style: (literal): the API style for function call.
                For Azure OpenAI API, use version 2023-12-01-preview or later.
                `"function"` style will be deprecated. For earlier version use
                `"function"` if `"tool"` doesn't work.
                See [Azure OpenAI documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/function-calling?tabs=python) for details.

        Returns:
            The decorator for registering a function to be used by an agent.

        Examples:
            ```
            @user_proxy.register_for_execution()
            @agent2.register_for_llm()
            @agent1.register_for_llm(description="This is a very useful function")
            def my_function(a: Annotated[str, "description of a parameter"] = "a", b: int, c=3.14) -> str:
                 return a + str(b * c)
            ```

            For Azure OpenAI versions prior to 2023-12-01-preview, set `api_style`
            to `"function"` if `"tool"` doesn't work:
            ```
            @agent2.register_for_llm(api_style="function")
            def my_function(a: Annotated[str, "description of a parameter"] = "a", b: int, c=3.14) -> str:
                 return a + str(b * c)
            ```

        """
        return super().register_for_llm(
            name=name,
            description=description,
            api_style=api_style,
            )

    def update_function_signature(self, func_sig: str | Dict, is_remove: None):
        super().update_function_signature(func_sig=func_sig, is_remove=is_remove)
        self.client = HepAIWrapper(**self.llm_config)
    
    def update_tool_signature(self, tool_sig: Union[str, Dict], is_remove: None):
        super().update_tool_signature(tool_sig=tool_sig, is_remove=is_remove)
        self.client = HepAIWrapper(**self.llm_config)
    
    def send_stream(
        self,
        message: Union[Dict, List, str],
        recipient: "LearnableAgent",
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ) -> Generator:
        # return self.send(message, recipient, request_reply=request_reply, silent=silent, stream=True)
        message = self._process_message_before_send(message, recipient, silent)
        # When the agent composes and sends the message, the role of the message is "assistant"
        # unless it's "function".
        valid = False
        if isinstance(message, list):
            valid = all(self._append_oai_message(m, "assistant", recipient, is_sending=True) for m in message) # recipient._oai_messages.append(m), which is host agent's oai_messages
        else:
            valid = self._append_oai_message(message, "assistant", recipient, is_sending=True)
        
        if valid:
            yield from recipient.receive_stream(message, self, request_reply, silent)
        else:
            raise ValueError(
                "Message can't be converted into a valid ChatCompletion message. Either content or function_call must be provided."
            )
        
    def receive_stream(
        self,
        message: Union[Dict, List, str],
        sender: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ):
        """Receive stream"""
        if isinstance(message, list):
            for m in message:
                self._process_received_message(m, sender, silent)# sender._oai_messages.append(m), which is human's oai_messages
        else:
            self._process_received_message(message, sender, silent)

        if request_reply is False or request_reply is None and self.reply_at_receive[sender] is False:
            return
        reply = yield from self.generate_reply_stream(messages=self.chat_messages[sender], sender=sender)
        if reply is not None:
            self.send(reply, sender, silent=silent)
            # TODO, 是send还是send_strem?

    def generate_reply_stream(
        self,
        messages: Optional[List[Dict[str, Any]]] = None,
        sender: Optional["Agent"] = None,
        **kwargs: Any,
    ) -> Union[str, Dict, Generator, None]:
        """Generate a reply to the last message from the sender and stream it to the sender."""

        if self._function_map:
            reply = self.generate_reply(messages=messages, sender=sender, **kwargs)
            if reply is not None:
                yield reply['content']
            return reply 
        
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

        for reply_func_tuple in self._reply_func_list:
            reply_func = reply_func_tuple["reply_func"]
            if "exclude" in kwargs and reply_func in kwargs["exclude"]:
                continue
            if inspect.iscoroutinefunction(reply_func):
                continue
            # # 新增：注册的函数不是流式函数，就直接跳过
            # if not inspect.isgeneratorfunction(reply_func):
            #     continue
            match = self._match_trigger(reply_func_tuple["trigger"], sender)
            if match:
                if inspect.isgeneratorfunction(reply_func):
                    final, reply = yield from reply_func(self, messages=messages, sender=sender, config=reply_func_tuple["config"], **kwargs)
                else:
                    final, reply = reply_func(self, messages=messages, sender=sender, config=reply_func_tuple["config"], **kwargs)
                    if inspect.isgenerator(reply) or isinstance(reply, Stream) or isinstance(reply, Stream2):
                        full_response = yield from base_oai_manager.convert_Generator_to_oai_stream(reply)
                        # full_response = ""
                        # for res in reply:
                        #     if isinstance(res, str):
                        #         full_response += res
                        #         yield res
                        #     elif isinstance(res, ChatCompletionChunk) or isinstance(res, ChatCompletionChunk2):
                        #         content = res.choices[0].delta.content
                        #         if content:
                        #             full_response += content
                        #             yield content
                        #     else:
                        #         raise ValueError(f"Invalid response type: {type(res)}")
                        reply = full_response
                if logging_enabled():
                    log_event(
                        self,
                        "reply_func_executed",
                        reply_func_module=reply_func.__module__,
                        reply_func_name=reply_func.__name__,
                        final=final,
                        reply=reply,
                    )
                if final:
                    return reply
        return self._default_auto_reply
    
if __name__ == "__main__":
    pass