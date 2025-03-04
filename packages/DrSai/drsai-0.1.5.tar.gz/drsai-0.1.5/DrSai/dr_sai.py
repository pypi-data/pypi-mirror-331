
from typing import List, Type, Dict, Callable, Generator, Tuple, Any, Union, Optional
import sys, copy
from pathlib import Path
import time
import json

here = Path(__file__).parent

try:
    from DrSai.version import __version__
except:
    sys.path.append(str(here.parent))
    from DrSai.version import __version__
from hepai import HepAI
from DrSai.apis.base_agent_api import (LearnableAgent, AssistantAgent, HostAgent, 
                                       HumanProxyAgent, HumanProxyAgentForStream, 
                                       GroupChatForHepAI, GroupChatWithTasks)
from DrSai.apis.agent_cases_api import Coder, Navigator
from DrSai.apis.components_api import tool_calls_register
from DrSai.apis.base_objects import Assistant, Thread, ThreadRun
from DrSai.apis.utils_api import Logger
from DrSai.configs import BaseArgs, CONST
from DrSai import THREADS_MGR, ASSISTANTS_MGR, VECTOR_STORES_MGR, FILES_MGR, VECTOR_STORE_FILES_MGR

from DrSai.apis.autogen_api import UserProxyAgent

logger = Logger.get_logger("dr_sai.py")


class DrSai:

    def __init__(self, 
                 args: BaseArgs = None, 
                 **kwargs):
        """
        DrSai多智能体框架初始化
        输入参数：
            args: BaseArgs, 多智能体框架参数配置
        启动后端框架方式：
            start_run: AutoGen形式命令行启动DrSai
            start_chat_completions: 使用openai chat/completions启动DrSai: https://platform.openai.com/docs/api-reference/chat
            start_run_stream: 使用OpenAI ASSISTANTS形式启动DrSai
            # https://platform.openai.com/docs/api-reference/assistants
        """
        self.args = args or BaseArgs()
        self.llm_config = None
        self.api_key = kwargs.pop('api_key', None)
        self.base_url = kwargs.pop('base_url', "https://aiapi.ihep.ac.cn/apiv2")
        self.base_models = kwargs.pop('base_models', None)
        if self.api_key is not None:
            self.llm_config = self.get_hepai_config(
                api_key=self.api_key, 
                base_url=self.base_url, 
                base_models=self.base_models, **kwargs)
        self.assistants_mgr = ASSISTANTS_MGR
        self.threads_mgr = THREADS_MGR
        self.vector_stores_mgr = VECTOR_STORES_MGR
        self.vector_store_files_mgr = VECTOR_STORE_FILES_MGR
        self.files_mgr = FILES_MGR

        self._registered_agents = dict()
        self._registered_functions = dict()
        self._default_agents = None

        self.username = "anonymous"
        self.agent: LearnableAgent | HostAgent = kwargs.pop('agent', None)
        self.stream = False if not isinstance(self.agent, LearnableAgent) else self.agent.stream


    @property
    def registered_agents(self) -> Dict[str, Type[LearnableAgent]]:
        return self._registered_agents
    
    @property
    def registered_functions(self) -> Dict[str, Callable]:
        return self._registered_functions

    def register_agent(self, name: str, agent: Type[LearnableAgent]) -> None:
        """注册Agent类, 用于从Assistants中加载Agent"""
        self._registered_agents[name] = agent

    def register_function(self, name: str, func: Callable) -> None:
        assert callable(func), f"Function {func} is not callable."
        self._registered_functions[name] = func

    def verify_headers(self, headers, base_url=None):
        """从Headers中验证API-KEY，返回用户名"""
        api_key: str = headers.get("authorization").split(" ")[-1]

        if base_url is None:
            # 判断是否是ddf1或者ddf2的API-KEY
            if api_key.startswith("Hi"):
                version = "v1"
                base_url = CONST.BASE_URL
            elif api_key.startswith("sk"):
                version = "v2"
                base_url = CONST.BASE_URL_V2
        try:
            hepai_client = HepAI(api_key=api_key, base_url = base_url)
            user_info = hepai_client.verify_api_key(api_key=api_key, version=version)
            if "user_id" in user_info:
                user_info["username"] = user_info["user_id"]
        except:
            user_info = {"success": True, "username": "anonymous"}

        return user_info
    
    def get_hepai_config(
            self, 
            HEPAI_API_KEY: str=None, 
            base_models: Union[str,List[str]] = None, 
            base_url: str = None,
            version="v2",
            **kwargs):
        
        if base_url is None:
            # 使用默认的hepai api地址
            if version == "v1":
                base_url = CONST.BASE_URL
            elif version == "v2":
                base_url = CONST.BASE_URL_V2
            else:
                raise ValueError(f"Unsupported version: {version}")

        api_key = HEPAI_API_KEY if HEPAI_API_KEY else self.api_key
        assert api_key is not None, "No HEPAI_API_KEY provided."
        self.llm_config = copy.deepcopy(self.args.llm_config)
        temperature = kwargs.pop('temperature', 0)
        top_p = kwargs.pop('top_p', 1)
        cache_seed = kwargs.pop('cache_seed', None)
        stream = kwargs.pop('stream', True)
        self.llm_config["temperature"] = temperature
        self.llm_config["top_p"] = top_p
        self.llm_config["cache_seed"] = cache_seed

        if base_models:
            config_list = []
            config_list_i = self.llm_config["config_list"][0]
            if isinstance(base_models, str):
                base_models = [base_models]
            for model in base_models:
                config_list_i_cp = config_list_i.copy()
                config_list_i_cp["model"] = model
                config_list_i_cp["api_key"] = api_key
                config_list_i_cp["base_url"] = base_url
                config_list_i_cp["stream"] = stream
                config_list.append(config_list_i_cp)
            self.llm_config["config_list"] = config_list
        else:
            # 使用默认的 llm_config
            for i, _ in enumerate(self.llm_config["config_list"]):
                if self.llm_config["config_list"][i]['base_url'] == base_url:
                    self.llm_config["config_list"][i]["api_key"] = api_key
            
        return self.llm_config
    
    def loading_agents(self, llm_config: Dict, **kwargs) -> List[Type[LearnableAgent]]:
        '''
        默认的Agent列表:
            - Assistant: 助手
            - Coder: 代码编写者
            - Navigator: 查询Arxiv/docDB/web等论文信息
        需要前端传入llm_config的配置,请在这里更改和注册你自己定义的Agents
        '''
        stream = kwargs.get('stream', True)
        # TODO: 增加默认的RAG
        if self._default_agents is None:
            assistant = AssistantAgent("Assistant", llm_config=llm_config, model_client_stream=stream)
            self.register_agent(assistant.name, assistant)
            coder = Coder("Coder", llm_config=llm_config, model_client_stream=stream)
            self.register_agent(coder.name, coder)
            navigator = Navigator("Navigator", llm_config=llm_config, model_client_stream=True)
            tool_calls_register.all_tools(agent=navigator)
            self.register_agent(navigator.name, navigator)
            
            self._default_agents = [coder, assistant, navigator]
        return self._default_agents

    #### --- 关于AutoGen --- ####
    def start_runs(
            self, 
            messages: List[Dict[str, str]] = [],
            **kwargs) -> Union[str, Generator[str, None, None], None]:
        """
        启动aotugen原生多智能体运行方式和多智能体逻辑
        """
        # 传入的消息列表
        usermessage = messages[-1]["content"]
        # 是否使用流式模式
        stream = kwargs.pop('stream', self.stream)
        if isinstance(self.agent, HostAgent) and stream:
            groupchat = self.agent._groupchat
            for participant in groupchat.agents:
                if not participant.stream:
                    raise ValueError("Streaming mode is not supported when participant.model_client_stream is False")
                
        if isinstance(self.agent, HostAgent):
            human = None
            for participant in self.agent._groupchat.agents:
                if isinstance(participant, HumanProxyAgent) or isinstance(participant, HumanProxyAgentForStream) \
                        or isinstance(participant, UserProxyAgent):
                    human = participant
                    break
            if human is None:
                raise ValueError("No human agent found in the groupchat.")
            # 传入的消息列表
            self.agent._groupchat.messages = messages
        else:
            self.llm_config = self.agent.llm_config if isinstance(self.agent, LearnableAgent) else self.agent._groupchat.agents[0].llm_config
            human = HumanProxyAgent(
                name="Human",
                human_input_mode="ALWAYS",
                code_execution_config=False,
                llm_config=self.llm_config,
                system_message="You are a human proxy",
                description="A human proxy for starting a group chat."
                )
        # Start #
        if stream:
            res = human.initiate_chat_stream(recipient=self.agent, message=usermessage)
            try:
                while True:
                    # 获取下一个 yield 的值
                    chunk: str = next(res)
                    pass
            except StopIteration as e:
                # 函数返回值通过 StopIteration 异常传递
                result = e.value
                # pass
            
        else:
            result = human.initiate_chat(recipient=self.agent, message=usermessage)
        print(result)
        return result
    
    #### --- 关于OpenAI Chat/Completions --- ####
    def start_chat_completions(
            self, 
            HEPAI_API_KEY: str=None,
            **kwargs) -> Union[str, Generator[str, None, None], None]:
        """
        启动聊天任务，使用completions后端模式
        加载默认的Agents, 并启动聊天任务, 这里默认使用GroupChat
        params:
        stream: bool, 是否使用流式模式
        messages: List[Dict[str, str]], 传入的消息列表
        HEPAI_API_KEY: str, 访问hepai的api_key
        usr_info: Dict, 用户信息
        base_models: Union[str, List[str]], 智能体基座模型
        chat_mode: str, 聊天模式，默认once
        **kwargs: 其他参数
        """
        # 是否使用流式模式
        stream = kwargs.pop('stream', self.stream)
        if isinstance(self.agent, HostAgent) and stream:
            groupchat = self.agent._groupchat
            for participant in groupchat.agents:
                if not participant.stream:
                    raise ValueError("Streaming mode is not supported when participant.model_client_stream is False")
        # 传入的消息列表
        messages: List[Dict[str, str]] = kwargs.pop('messages', [])
        usermessage = messages[-1]["content"]
        # 大模型配置
        temperature = kwargs.pop('temperature', 0)
        top_p = kwargs.pop('top_p', 1)
        cache_seed = kwargs.pop('cache_seed', None)
        # 额外的请求参数
        extra_body: Union[Dict, None] = kwargs.pop('extra_body', None)
        if extra_body is not None:
            ## 用户信息 从DDF2传入的
            user_info: Dict = kwargs.pop('extra_body', {}).get("user", {})
            self.api_key = user_info.get("api_key", None) or HEPAI_API_KEY
            self.username = user_info.get("name", "anonymous")
            ## 智能体基座模型
            base_models: Union[str, List[str]] = extra_body.get("base_models", "openai/gpt-4o")  # 选择智能体基座模型
            base_url: str = extra_body.get("base_url", "https://aiapi.ihep.ac.cn/apiv2")  # 选择智能体基座地址
            chat_mode = extra_body.get("chat_mode", "once")  # 聊天模式，默认once
        else:
            self.api_key = HEPAI_API_KEY
            base_models: Union[str, List[str]] = kwargs.get("base_models", "openai/gpt-4o")
            base_url: str = kwargs.get("base_url", "https://aiapi.ihep.ac.cn/apiv2")
            self.username = kwargs.get("name", "anonymous")
            chat_mode = kwargs.pop('chat_mode', "once")
                
        if isinstance(self.agent, HostAgent):
            human = None
            for participant in self.agent._groupchat.agents:
                if isinstance(participant, HumanProxyAgent) or isinstance(participant, HumanProxyAgentForStream) \
                        or isinstance(participant, UserProxyAgent):
                    human = participant
                    break
            if human is None:
                raise ValueError("No human agent found in the groupchat.")
            # 传入的消息列表
            self.agent._groupchat.messages = messages

            if self.agent._backend_mode != "completions":
                raise ValueError("HostAgent with backend_mode != completions is not supported.")
            
            if stream:
                groupchat = self.agent._groupchat
                for participant in groupchat.agents:
                    if not participant.stream:
                        raise ValueError("Streaming mode is not supported when participant.model_client_stream is False")
        else:
            self.llm_config = self.agent.llm_config if isinstance(self.agent, LearnableAgent) else self.agent._groupchat.agents[0].llm_config
            human = HumanProxyAgent(
                name="Human",
                human_input_mode="ALWAYS",
                code_execution_config=False,
                llm_config=self.llm_config,
                system_message="You are a human proxy",
                description="A human proxy for starting a group chat."
                )

        # Start #
        if stream:
            yield from human.initiate_chat_stream(recipient=self.agent, message=usermessage)
        else:
            # 将流式内容转化为非流
            gen = human.initiate_chat_stream(recipient=self.agent, message=usermessage)
            chatcompletions = {
                'id': 'chatcmpl-123', 
                'choices': [
                    {'finish_reason': 'stop', 
                     'index': 0, 
                     'logprobs': None, 
                     'message': {'content': '', 
                                 'refusal': None, 
                                 'role': 'assistant', 
                                 'audio': None, 
                                 'function_call': None, 
                                 'tool_calls': None}}], 
                                 'created': 1739758379, 
                                 'model': 'DrSai', 
                                 'object': 'chat.completion', 
                                 'service_tier': 'default', 
                                 'system_fingerprint': 'fp_13eed4fce1', 
                                 'usage': {
                                     'completion_tokens': 10, 'prompt_tokens': 8, 
                                     'total_tokens': 18, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 
                                     'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}}
            content = ""
            try:
                while True:
                    # 获取下一个 yield 的值
                    chunk: str = next(gen)
                    oai_json = json.loads(chunk.split("data: ")[1])
                    textchunck = oai_json["choices"][0]["delta"]["content"]
                    if textchunck:
                        content += textchunck
            except StopIteration as e:
                # 函数返回值通过 StopIteration 异常传递
                # result = e.value
                pass
            chatcompletions["choices"][0]["message"]["content"] = content
            yield json.dumps(chatcompletions)

    #### --- 关于OPENAI ASSISTANTS --- ####
    def load_agents_from_assistants(self, llm_config: Dict, assistants: List[Assistant], default = True , **kwargs) -> List[Type[LearnableAgent]]:
        """
        加载默认的Dr.Sai Agents或者通过前端创建的Assistant加载自定义Agent
        """
        stream = kwargs.get('stream', True)
        agents = []
        # 加载Agents 
        if self._registered_agents:
            for agents_name in self._registered_agents:
                agents.append(self._registered_agents[agents_name])
        elif default:
            agents: List[LearnableAgent] = self.loading_agents(self.llm_config, stream = stream) # 加载默认的Agents
        else:
            for assistant in assistants:
                # 获取assistant的相关信息
                asst_description = assistant.description
                asst_system_message = assistant.instructions
                asst_model = assistant.model
                asst_name = assistant.name
                asst_metadata = assistant.metadata
                asst_top_p = assistant.top_p
                asst_temperature = assistant.temperature
                asst_response_format = assistant.response_format
                asst_tools = assistant.tools
                asst_tool_resources = assistant.tool_resources
                ## 收集Assistant的tools
                for tools in asst_tools:
                    # TODO: 代码文件执行: https://platform.openai.com/docs/assistants/tools/code-interpreter
                    if tools['type'] == "code_interpreter":
                        code_interpreter: Dict = asst_tool_resources.get("code_interpreter", [])
                        file_ids = code_interpreter.get("file_ids", [])
                        pass
                    # TODO: 返回tool_call: https://platform.openai.com/docs/assistants/tools/function-calling
                    if tools['type'] == "function":
                        func_tools = [x for x in asst_tool_resources if x['type'] == "function"]
                        pass
                    # TODO: 加载vector_store_ids: https://platform.openai.com/docs/assistants/tools/file-search
                    if tools['type'] == "file_search":
                        vector_store_ids_dict: Dict = asst_tool_resources.tool_resources.get("file_search", False)
                        vector_store_ids: List[str] = vector_store_ids_dict.get("vector_store_ids", [])
                        # TODO：加载memory的RAG组件
                llm_config["config_list"][0]["model"] = asst_model
                llm_config["temperature"] = asst_temperature
                llm_config["top_p"] = asst_top_p
                if asst_response_format != "auto":
                    llm_config["response_format"] = asst_response_format
                agent: AssistantAgent = AssistantAgent(
                    name = asst_name, 
                    system_message=asst_system_message, 
                    description=asst_description, 
                    llm_config=llm_config, 
                    model_client_stream=stream)
                self.register_agent(agent.name, agent)
                agents.append(agent)
        return agents


    #### --- 关于Asisstants --- ####
    def create_assistants(self, model, username=None, **kwargs):
        """
        创建一个助手
        :param model: str, required, The model to use for the assistant.
        :param name: str, The name of the assistant.
        :param username: str, The username of the user who is creating the assistant.
        """
        return self.assistants_mgr.create_assistant(model, username=username, **kwargs)
        
    def list_assistants(self, username=None, **kwargs):
        username = username or CONST.DEFAULT_USERNAME
        return self.assistants_mgr.list_assistants(username=username, **kwargs)

    def retrive_assistants(self, assistant_id, username=None):
        """获取一个已经创建的助手"""
        return self.assistants_mgr.retrieve_assistant(assistant_id=assistant_id, username=username)
    
    def list_and_retrive_assistant(self, username=None, **kwargs):
        """
        列出助手，并获取一个助手
        :param username: str, The username of the user who is creating the assistant.
        :param index: int, The index of the assistant to retrieve.
        :param create_if_not_exist: bool, Whether to create a new assistant if none exist.
        """
        index = kwargs.pop('index', 0)
        create_if_not_exist = kwargs.pop('create_if_not_exist', True)
        
        assts = self.list_assistants(username=username, **kwargs)
        assts = assts["data"]
        if len(assts) == 0:
            if not create_if_not_exist:
                raise ValueError(f"No assistant found for user: {username}.")
            asst = self.create_assistants(
                model=CONST.DEFAULT_MODEL,
                name='Dr.Sai-Primary', 
                save_immediately=False)
        else:
            asst = assts[index]
        asst = self.retrive_assistants(assistant_id=asst.id, username=username)
        return asst
        

    #### --- 关于Threads --- ####
    def retrive_threads(self, thread_id, username=None):
        """获取一个已经创建的线程"""
        return self.threads_mgr.retrieve_thread(thread_id, username=username)
    
    def create_threads(self, **kwargs):
        """
        {
        "id": "thread_abc123",
        "object": "thread",
        "created_at": 1699012949,
        "metadata": {},
        "tool_resources": {}
        }
        """
        messages = kwargs.pop('messages', None)
        thread = self.threads_mgr.create_threads(**kwargs)
        if messages:
            for msg in messages:
                self.create_message(thread_id=thread.id, **msg)
                # 注意：此处的`thread`是Thread对象，不是thread_id，即是的message在现有thread对象inplace更新
        return thread
    
    def create_thread_and_run(
            self, 
            assistant_ids: str | List[str], 
            username=None, **kwargs):

        thread = self.create_threads(**kwargs)
        
        res = self.create_runs(
            thread_id=thread.id, assistant_ids=assistant_ids,
            username=username, **kwargs)
        return res

    def check_and_save_threads(self, username=None, **kwargs):
        return self.threads_mgr.check_and_save(username=username, **kwargs)

    #### --- 关于Messages --- ####
    def create_message(self, thread_id, role, content, **kwargs):
        """

        Parameters:
        thread_id: str, required, The ID of the thread to create a message for.
        role: str, required, The role of the entity that is creating the message. Allowed values include: 'user', 'assistant'.
        content: str, required, The content of the message.
        attachments: list or None, A list of files attached to the message, and the tools they should be added to.
        metadata: dict or None, Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.
        """
        return self.threads_mgr.create_message(thread_id, role, content, **kwargs)
    
    def list_messages(
            self, thread_id, limit=20, order='desc', after=None, before=None, 
            run_id=None, username=None, **kwargs):
        return_format = kwargs.pop('return_format', 'object')
        return self.threads_mgr.list_messages(
            thread_id, limit=limit, order=order, after=after, before=before,
            run_id=run_id, username=username, return_format=return_format, **kwargs)

    #### --- 关于Runs --- ####
    def retrive_runs(self, thread_id, run_id, username=None):
        return self.threads_mgr.retrieve_run(thread_id, run_id, username=username)
    
    def create_runs_stream(self, thread_id: str, assistant_ids: str | List[str], 
            username: str=None, **kwargs):
        """带有流式event的创建run"""
        stream = kwargs.get('stream')
        assert stream is True, "The `stream` parameter must be set to True."
        
        run: ThreadRun = self.threads_mgr.create_runs(thread_id, assistant_ids, **kwargs)
        yield from run.status_event("created", set_status=True)
        
        yield from self.start_runs_stream(run, username=username, **kwargs)

        # return evc.all_events_generator()

    def create_runs(
            self, thread_id: str, assistant_ids: str | List[str], 
            username: str=None, **kwargs):
        """
        Create a run.
        :param thread_id: str, required, The ID of the thread to create a run for.
        :param assistant_ids: str or list of str, required, The ID of the assistant to create a run for.
        :param model
        :param instructions
        ...
        """
        start = kwargs.get('start', False)
        run_on_main_thread = kwargs.get('run_on_main_thread', False)
        stream = kwargs.get('stream', False)
        if stream:
            return self.create_runs_stream(thread_id, assistant_ids, username=username, **kwargs)
        
        run: ThreadRun = self.threads_mgr.create_runs(thread_id, assistant_ids, **kwargs)
       
        if run_on_main_thread:  # 在主线线程启动
            run = self.start_runs(run, username=username, **kwargs)
        elif start:  # 在子线程启动，用于轮询
            run.start(run_func=self.start_runs)
        return run
    
    def create_and_poll(self, thread_id, assistant_ids, username=None, **kwargs):
        """
        Create a run and poll it until it is completed.
        """

        # Create
        start = kwargs.pop('start', True)
        kwargs.pop('run_on_main_thread', False)
        run = self.create_runs(
            thread_id, assistant_ids, username=username, start=start, 
            run_on_main_thread=False, **kwargs)
        
        # Poll
        while run.status != "completed":
            run = self.retrive_runs(thread_id, run.id, username=username)
            logger.debug(f'Main thread, run status: {run.status}')
            time.sleep(1)
        return run
    
    ## --- 启动run --- ##hep
    def start_runs_stream(
            self, run: ThreadRun, username=None, **kwargs
            ):
        '''
        启动聊天任务，使用assistants后端模式
        加载默认的Agents, 并启动聊天任务
        '''
        stream = kwargs.get('stream', True)
        assts: List[Assistant] = run.assistants
        self.username = username or "anonymous"
        HEPAI_API_KEY = kwargs.get("HEPAI_API_KEY2", None) or self.api_key
        self.api_key = HEPAI_API_KEY
        base_models: Union[str, List[str]] =kwargs.get("base_models", "openai/gpt-4o")  # 选择智能体基座模型
        base_url = kwargs.get("base_url", "https://aiapi.ihep.ac.cn/apiv2")  # 选择智能体基座API地址
        if self.llm_config is None:
            self.llm_config = self.get_hepai_config(
                HEPAI_API_KEY = HEPAI_API_KEY,
                base_models=base_models,
                base_url=base_url,
                **kwargs
                )
        default = kwargs.get("default_agents", True)
        agents: List[LearnableAgent] = self.load_agents_from_assistants(
            llm_config = self.llm_config,
            assistants = assts, 
            username=username, 
            default=default, # 加载默认的Agents
            **kwargs)

        human = HumanProxyAgentForStream(
            name="Human",
            human_input_mode="ALWAYS",
            code_execution_config=False,
            llm_config=self.llm_config,
            description="A human agent, managing all unclear or unusual tasks.",
            system_message="""
                As a capable steward of the user, you are expected to push the assigned task forward by providing a feasible proposal on how to deal with the assigned task without explanation. 
                
                Please be mindful of the following three scenarios:
                    - If the task need further results or solutions, just restate its content without adding any words.
                    - If the task description is overly simplistic and unclear, please offer a succinct suggestion for potential tasks that align with the current task based on the chat history.
                    - If the task has been successfully completed, provide a brief comment and then conclude with a closing message indicating the end of the conversation, such as "Looks like everything is done. See you next time.".
                
                Given the instructions above, please proceed with the following task:
            """,
            # human_input_terminal= "cli",
            human_input_terminal= "webui",
            model_client_stream=stream,
        )
        self.register_agent("Human", human)
        agents.insert(0, human) # 第一个位置插入human
        
        # 从thread加载messages
        thread: Thread = run.thread
        groupchat: GroupChatWithTasks = kwargs.get("groupchat", None)
        if groupchat is None:
            s_select_method = "auto" if len(agents) > 2 else "round_robin" 
            groupchat = GroupChatWithTasks(
                agents=agents,  # 传入智能体 ,
                thread=thread,  # 传入持久化消息，自动更新任务
                max_round=50,
                speaker_selection_method=s_select_method,
                )
        else:
            groupchat.agents.append(human)
        host: HostAgent = kwargs.get("host", None)
        if host is None:
            chat_mode = "once" if not kwargs.get("chat_mode") else kwargs.get("chat_mode")
            host = HostAgent(
                name='host',
                groupchat=groupchat, 
                thread_run=run,
                llm_config=self.llm_config,
                threads_manager=self.threads_mgr,
                chat_mode=chat_mode,
                backend_mode = "assistants",
                model_client_stream=stream,
                )
        else:
            host._thread_run = run
            host.threads_mgr = self.threads_mgr
        logger.debug(f"Create a run on thread `{thread.id}` with agents: {[x.name for x in agents]}")
        messages = [x.to_oai_message() for x in thread.messages] # 从线程中加载消息.
        assert len(messages) > 0, "No messages found in the thread."
        
        yield from run.status_event("queued", set_status=True)
        yield from human.run_stream(recipient=host, message=messages[-1]["content"])
        return run

   
 

