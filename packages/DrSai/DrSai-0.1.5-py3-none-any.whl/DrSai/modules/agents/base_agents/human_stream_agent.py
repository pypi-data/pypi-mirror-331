
from typing import Callable, Dict, List, Optional, Union, Literal, Generator
import json, time

from .learnable_agent import LearnableAgent
from DrSai.modules.managers.base_thread_message import ThreadMessage, Content, Text
from DrSai.modules.managers.base_thread import Thread

from DrSai.apis.autogen_api import Cache


class HumanProxyAgentForStream(LearnableAgent):
    
    # Default UserProxyAgent.description values, based on human_input_mode
    DEFAULT_USER_PROXY_AGENT_DESCRIPTIONS = {
        "ALWAYS": "An attentive HUMAN user who can answer questions about the task, and can perform tasks such as running Python code or inputting command line commands at a Linux terminal and reporting back the execution results.",
        "TERMINATE": "A user that can run Python code or input command line commands at a Linux terminal and report back the execution results.",
        "NEVER": "A computer terminal that performs no other action than running Python scripts (provided to it quoted in ```python code blocks), or sh shell scripts (provided to it quoted in ```sh code blocks).",
    }

    def __init__(
        self,
        name: str,
        is_termination_msg: Optional[Callable[[Dict], bool]] = None,
        max_consecutive_auto_reply: Optional[int] = None,
        human_input_mode: Literal["ALWAYS", "TERMINATE", "NEVER"] = "ALWAYS",
        function_map: Optional[Dict[str, Callable]] = None,
        code_execution_config: Optional[Union[Dict, Literal[False]]] = None,
        default_auto_reply: Optional[Union[str, Dict, None]] = "",
        llm_config: Optional[Union[Dict, Literal[False]]] = False,
        system_message: Optional[Union[str, List]] = "",
        description: Optional[str] = None,
        human_input_terminal: Literal["cli", "webui"] = "cli",
        **kwargs
    ):
        """
        Args:
            name (str): name of the agent.
            is_termination_msg (function): a function that takes a message in the form of a dictionary
                and returns a boolean value indicating if this received message is a termination message.
                The dict can contain the following keys: "content", "role", "name", "function_call".
            max_consecutive_auto_reply (int): the maximum number of consecutive auto replies.
                default to None (no limit provided, class attribute MAX_CONSECUTIVE_AUTO_REPLY will be used as the limit in this case).
                The limit only plays a role when human_input_mode is not "ALWAYS".
            human_input_mode (str): whether to ask for human inputs every time a message is received.
                Possible values are "ALWAYS", "TERMINATE", "NEVER".
                (1) When "ALWAYS", the agent prompts for human input every time a message is received.
                    Under this mode, the conversation stops when the human input is "exit",
                    or when is_termination_msg is True and there is no human input.
                (2) When "TERMINATE", the agent only prompts for human input only when a termination message is received or
                    the number of auto reply reaches the max_consecutive_auto_reply.
                (3) When "NEVER", the agent will never prompt for human input. Under this mode, the conversation stops
                    when the number of auto reply reaches the max_consecutive_auto_reply or when is_termination_msg is True.
            function_map (dict[str, callable]): Mapping function names (passed to openai) to callable functions.
            code_execution_config (dict or False): config for the code execution.
                To disable code execution, set to False. Otherwise, set to a dictionary with the following keys:
                - work_dir (Optional, str): The working directory for the code execution.
                    If None, a default working directory will be used.
                    The default working directory is the "extensions" directory under
                    "path_to_autogen".
                - use_docker (Optional, list, str or bool): The docker image to use for code execution.
                    Default is True, which means the code will be executed in a docker container. A default list of images will be used.
                    If a list or a str of image name(s) is provided, the code will be executed in a docker container
                    with the first image successfully pulled.
                    If False, the code will be executed in the current environment.
                    We strongly recommend using docker for code execution.
                - timeout (Optional, int): The maximum execution time in seconds.
                - last_n_messages (Experimental, Optional, int): The number of messages to look back for code execution. Default to 1.
            default_auto_reply (str or dict or None): the default auto reply message when no code execution or llm based reply is generated.
            llm_config (dict or False): llm inference configuration.
                Please refer to [OpenAIWrapper.create](/docs/reference/oai/client#create)
                for available options.
                Default to false, which disables llm-based auto reply.
            system_message (str or List): system message for ChatCompletion inference.
                Only used when llm_config is not False. Use it to reprogram the agent.
            description (str): a short description of the agent. This description is used by other agents
                (e.g. the GroupChatManager) to decide when to call upon this agent. (Default: system_message)
        """
        super().__init__(
            name=name,
            system_message=system_message,
            is_termination_msg=is_termination_msg,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            human_input_mode=human_input_mode,
            function_map=function_map,
            code_execution_config=code_execution_config,
            llm_config=llm_config,
            default_auto_reply=default_auto_reply,
            description=description if description is not None else self.DEFAULT_USER_PROXY_AGENT_DESCRIPTIONS[human_input_mode],
            **kwargs
        )

        # if logging_enabled():
        #     log_new_agent(self, locals())
        self.human_input_terminal = human_input_terminal
    
    def get_status(self):
        status = super().get_status()
        status["human_input_mode"] = self.human_input_mode
        status["length_of_human_input"] = len(self._human_input)
        return status
    

    def get_human_input(self, thread_message: ThreadMessage, prompt: str, **kwargs) -> str:
        if self.human_input_terminal == 'cli': # 前端使用cli输入
            reply = super().get_human_input(prompt)
            self.require_human_input(thread_message, reply)
            return reply
        
        # 向前端发起请求
        # th_msg: ThreadMessage = self.th_msg
        # data = th_msg.construct_delta_event(prompt, id=0)
        timeout = kwargs.get('timeout', 60)
        stream = self.require_user_input_stream(thread_message, timeout=timeout)
        return stream
    
    def require_human_input(self, thread_message: ThreadMessage, reply: str, **kwargs) -> Generator:
        reply2msd=Content(type="text", text=Text(value=reply,annotations=[]))# 这里需要更新content，否则会导致ThreadMessage的content为空，导致无法发送消息
        thread_message.content = [reply2msd] 
        data = thread_message.construct_delta_event(reply, id=0)
        yield from f'data: {json.dumps(data)}\n\n' # TODO: 不需要再向前端发送消息，直接返回reply即可

    def require_user_input_stream(self, thread_message: ThreadMessage, **kwargs) -> Union[str, Generator]:
        """
        向前端发起请求，获取用户输入, 使用metadata接受前端输入的消息, 人类输入的消息会被放入metadata["human_input"]中
        """
        
        timeout = kwargs.get('timeout', 60)
        thread_message.metadata['ask_human_input'] = True # 用于判断前端是否输入了消息
        metadata = thread_message.metadata
        assert metadata.get('ask_human_input', False) is True, f"metadata['ask_human_input'] should be True when calling require_user_input_stream"
        
        # 向前端发送特定格式的 '[Start]Ask human input for xxs[END]' 给前端解析
        data = thread_message.construct_delta_event(
            f'[ST]Ask human input for {timeout}s[END]',   
            id="msg_delta_032549316423")
        yield f'data: {json.dumps(data)}\n\n'

        t0 = time.time()

        count = 0
        verbose = False # 是否打印等待提示信息
        while True:
            if thread_message.metadata["ask_human_input"] is False:
                reply: str = thread_message.metadata["human_input"]
                break

            if time.time() - t0 > timeout:
                reply = "No user input"
                break
            
            # if count % 5 == 0:
            #     data = thread_message.construct_delta_event(
            #         # f'waiting for user input, {timeout - int(time.time() - t0)}s left', id=0
            #         f' ', id=0
            #     )
            #     yield f'data: {json.dumps(data)}\n\n'
            if verbose:
                print(f'waiting for user input, {timeout - int(time.time() - t0)}s left')
            time.sleep(1.0)
            count += 1

        
        content = Content(
            type="text",
            text=Text(
                value=reply,
                annotations=[]
                ))
        thread_message.content = [content]
        return reply
    
    def run_stream(
        self,
        recipient: "LearnableAgent",
        clear_history: Optional[bool] = True,
        silent: Optional[bool] = False,
        cache: Optional[Cache] = None,
        max_turns: Optional[int] = None,
        **context,
    ) -> Generator:
        return self.initiate_chat_stream(recipient=recipient, clear_history=clear_history, silent=silent, cache=cache, max_turns=max_turns, **context)

    

