from typing import List, Dict, Union, Optional
from autogen.agentchat.conversable_agent import ConversableAgent
from dataclasses import dataclass, field
import ast
import damei as dm
import uuid
import time
import json

from .tasks import Task
from DrSai.apis.base_objects import Thread
from DrSai.apis.base_objects import ThreadMessage, Content, Text
from DrSai.apis.base_agent_api import LearnableAgent

from DrSai.configs import CONST
from DrSai.utils import Logger, str_utils
from DrSai.apis.autogen_api import GroupChat, Agent

try:
    from termcolor import colored
except ImportError:
    def colored(x, *args, **kwargs):
        return x

logger = Logger.get_logger("groupchat.py")

@dataclass
class GroupChatWithTasks(GroupChat):
    thread: Thread = None
    messages: List[Dict] = None  # 这是OAI格式的messages
    tasks: List[Task] = field(default_factory=list)
    llm_config: Dict = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        
        self._root_task = self.create_task(content="", source="") # 初始化根任务
        self._current_task = self._root_task

        if self.thread:  # 从线程中加载消息，读取任务
            messages: List[ThreadMessage]  = self.thread.messages
            # print(f"thread.messages={messages}")
            self.messages = [x.to_oai_message() for x in messages]
            self.load_tasks_from_thread(self.thread) # 不保存并弃用tasks列表，因为任务树很难投影到一维

    def load_tasks_from_thread(self, thread: Thread):
        '''
        尝试从thread中提取历史根任务。由于任务关联是通过自身属性绑定的，因此预期整个任务树都挂靠在根任务上
        若拿到历史根任务，检索首个未完成的任务（即current_task）
        若历史任务树执行完毕，则current_task指向根任务
        '''
        messages: List[ThreadMessage]  = thread.messages
        
        ## 首先读取thread中的历史任务
        if thread.metadata.get('root_task', None) is not None:
            self._root_task = self.mapping_json2task(thread.metadata['root_task']) # 历史任务树的根任务
            ## 更新并检索首个未完成的任务（即current_task）
            self._current_task = self.get_next_task(current_task=self._root_task) # 继承历史任务树的current_task
            if CONST.DEBUG_BACKEND:
                logger.info("\033[33m" + f"load_tasks_from_thread_history: root_tasks = {self._root_task.sub_tasks}" + "\033[0m")

        # ## 判断最后一条消息（即人类最新的消息）中的任务数量，分割潜在的子任务(挂靠在current_task/parent_task下)        
        ## 人类的新任务默认insert，如果是首个任务则add到根任务下面 - 2024年10月31日14:09:22
        tasks_from_msg: List[Task] = self.parse_tasks_from_message(message=messages[-1])
        logger.info("\033[33m" + f"{self.process_tasks_from_taskList(tasks_from_msg)}" + "\033[0m") # 假如是首个任务，默认add
        ## 分离出任务之后，更新记录一下任务树
        thread.metadata['root_task'] = self.mapping_task2json(self._root_task)
        
        ## 初始化current_task
        if self._current_task == self._root_task:
            self._current_task = self.get_next_task(current_task=self._current_task)
        
        # print(f"load_tasks_from_thread:{tasks_from_msg}")
        # return tasks_from_msg

    @property
    def current_task(self) -> Task:
        return self._current_task
    
    def auto_id(self, prefix: str = '', length: int = 10, deduplicate: bool | List = True):
        """
        自动生成一个10位的id。
        """
        new_id = uuid.uuid4().hex
        short_id = str(new_id).replace('-', '')
        short_id = prefix + short_id[:length-len(prefix)]
        return short_id
    
    def create_task(self, content: str, source: str="", parent_task: Task=None, sub_tasks: List[Task]=None, **kwargs):
        """
        Create a task object.
        Args:
            content: str, task content
            source: str, task source
            parent_task: Task, parent task
            sub_tasks: List[Task], sub tasks of the task
            **kwargs: dict, other task information
        """
        ## 不应可变对象作为默认值，因为参数是在函数定义时计算的，而不是调用时。这会导致所有实例共享同一个列表，例如前端打开新的对话页面时任务树还会传递过去
        if sub_tasks is None:
            sub_tasks = []

        task = Task(
            id=self.auto_id(prefix='task_', length=15, deduplicate=False),
            object='task',
            created_at=int(time.time()),
            content=content,
            source=source,
            status="queued",
            parent_task=parent_task,
            sub_tasks=sub_tasks,
            task_type=kwargs.get('task_type', None),
            )
        return task
    
    def create_tasks(self, task_list: List[str]) -> List[Task]:
        '''
        直接根据一串任务字符串创建任务
        '''
        output = []
        for task in task_list:
            ## 逐个创建任务，并作为子任务挂靠在当前任务上
            itask = self.create_task(
                    content=task,
                    parent_task=self._current_task,
                    sub_tasks=[],
                    #task_type = task_type
                ) # 默认创建status是queue
            self._current_task.sub_tasks.append(itask) # 主任务与子任务相互交叉绑定
            output.append(itask)
        return output
    
    def insert_task(self, task_content: str, base_task: Task = None) -> None:
        '''
        1. 使用str创建新任务并插入到base_task之前(同一层级), base_task默认是current_task
        2. 更新current_task为新任务
        '''
        ## insert tasks before base_task. default is current_task
        if base_task is None:
            base_task = self.current_task

        base_task_list = base_task.parent_task.sub_tasks
        index = base_task_list.index(base_task)
        new_task = self.create_task(content=task_content, parent_task=base_task.parent_task, sub_tasks=[])
        base_task_list.insert(index, new_task)
        self._current_task = new_task
    
    def delete_task(self, task_id: str = "") -> None:
        '''
        1. 设置current_task(焦点任务)状态为已完成
        2. 更新current_task为焦点任务的下一个任务
        3. 删除焦点任务 TODO:现在只能删除当前任务
        '''

        parent_task = self._current_task.parent_task
        index = parent_task.sub_tasks.index(self._current_task)
        self._current_task.set_completed(solution="deleted") # 这是目标任务
        self._current_task = self.get_next_task(current_task=self._current_task) # 跳转到目标任务的下一个任务
        parent_task.sub_tasks.pop(index) # 删除当前任务
    
    def get_task_map(self, tasks: List[Task] = [], level=0, index="") -> str:
        '''
        递归调用，输出任务树的结构(str)
        '''
        if level == 0 and tasks == []:
            tasks = self._root_task.sub_tasks # 默认从第一层任务开始，即初始的直接来自用户的任务
        
        output = ""
        for i, task in enumerate(tasks):
            index_anchor = f"{index}{i+1}."
            index_sub = f"{'  '*level}{index}{i+1}."
            if task == self._current_task:
                output += f"\n{index_anchor} {task.content}  status={task.status} \u2190\n"
            else:
                output += f"\n{index_anchor} {task.content}  status={task.status}\n"
            output += self.get_task_map(task.sub_tasks, level + 1, index_sub) # 递归调用
        return output
    
    def mapping_task2json(self, task: Task) -> Dict:
        '''
        将任务对象映射为json格式
        '''
        task_dict = {
            "id": task.id,
            "object": task.object,
            "created_at": task.created_at,
            "content": task.content,
            "source": task.source,
            "status": task.status,
            "parent_task": task.parent_task.id if task.parent_task is not None else None,
            "sub_tasks": [self.mapping_task2json(sub_task) for sub_task in task.sub_tasks],
            "task_type": task.task_type,
        }
        return task_dict

    def mapping_json2task(self, task_dict: Dict) -> Task:
        '''
        将json格式的任务对象映射为Task对象
        '''
        def mapping_json2subtask(task_dict: Dict) -> Task:
            parent_task_id = task_dict["parent_task"]
            task = Task(
                id=task_dict["id"],
                object=task_dict["object"],
                created_at=task_dict["created_at"],
                content=task_dict["content"],
                source=task_dict["source"],
                status=task_dict["status"],
                parent_task=None,  # 暂时设置为None，后续再设置
                sub_tasks=[mapping_json2subtask(sub_task) for sub_task in task_dict["sub_tasks"]],
                task_type=task_dict["task_type"],
            )
            task.parent_task_id = parent_task_id  # 存储parent_task的ID
            return task
        
        root_task = mapping_json2subtask(task_dict)

        # 创建一个任务ID到任务对象的映射
        task_map = {}
        def build_task_map(task: Task):
            task_map[task.id] = task
            for sub_task in task.sub_tasks:
                build_task_map(sub_task)
        build_task_map(root_task)

        # 设置parent_task
        def set_parent_task(task: Task):
            if task.parent_task_id is not None:
                task.parent_task = task_map.get(task.parent_task_id)
            for sub_task in task.sub_tasks:
                set_parent_task(sub_task)
        set_parent_task(root_task)

        return root_task


    def get_next_task(self, current_task: Task = None) -> Task:
        current_task = current_task if current_task is not None else self.current_task

        next_task = current_task # 从当前任务开始检索

        while True:
            ## 如果当前任务完成了，向上检索父任务状态
            if next_task.status == "completed":
                next_task = next_task.parent_task
            else: # 对于没有完成的任务，向下检索子任务队列，如果没有子任务未完成则返回自己
                sub_tasks = next_task.sub_tasks
                if sub_tasks: # 当前任务有子任务
                    isFind = False # 是否找到未完成的子任务
                    for sub_task in sub_tasks:
                        if sub_task.status != "completed":
                            next_task = sub_task
                            isFind = True
                            break
                    if isFind: # 如果找到了未完成的子任务，在下一轮判断中检查该子任务状态
                        pass
                    else: # 如果没找到未完成的子任务，标记当前任务的状态为已完成，进入下一轮判断
                        if next_task == self._root_task: # 如果根任务的子任务都执行完毕，意味着任务树执行完毕，返回自己
                            return next_task
                        else: # 对于普通任务，直接设置其状态为完成。这意味着节点任务不执行
                            next_task.status = "completed"
                else: # 当前任务没有子任务，返回自己
                    return next_task
    
    def is_all_tasks_finished(self) -> bool:
        #return all(task.is_finished() for task in self.tasks)
        if self._current_task == self._root_task: # 到达任务树顶点，返回True
            ## 将任务树存进thread.metadata
            self.thread.metadata['root_task'] = self.mapping_task2json(self._root_task) ## TODO：如何考虑用户是否需要保存历史任务树？
            return True
        else:
            return False
    
    def update_tasks_from_message(self, message: Optional[Union[ThreadMessage, List[str]]]) -> str:
        output = "The task tree has been updated successfully. "

        ## 提取任务列表，若有则创建任务，并挂靠到当前任务上作为其子任务交叉绑定
        tasks_from_msg = self.parse_tasks_from_message(message) # List[str] | None

        if tasks_from_msg: # 如果当前任务分离出子任务，那么按任务种类更新任务树
            process_result = self.process_tasks_from_taskList(tasks_from_msg)
            logger.info("\033[33m" + f"Tasks from message: {process_result}" + "\033[0m")
            
            if tasks_from_msg[0] == "select": # 如果是查看任务树，那么该任务执行完之后，即当前任务就结束了
                try:
                    self._current_task.set_completed(message.content_str())
                except:
                    self._current_task.set_completed(process_result)
            output += process_result
        else: # 如果没有分离出子任务，设置任务状态为完成 -- 通常是其他agent update thread
            self._current_task.set_completed(message.content_str())
        
        ## 顺序执行下一个任务
        self._current_task = self.get_next_task()
        ## 将任务树存进thread.metadata
        self.thread.metadata['root_task'] = self.mapping_task2json(self._root_task)

        if CONST.DEBUG_BACKEND:
            print(colored(f"Current task:{self.current_task}", "green"))
            print(f"All task:\n{self.get_task_map()}")
        
        return output

    def parse_tasks_from_message(self, message: Optional[Union[ThreadMessage, List[str]]]) -> List[str] | None:
        """
        从message或者任务清单（字符串）中提取任务列表。
        只有来自Host和Human的message会分解出任务，其他agents不可以。
        如果message类型是List[str]，直接用它创建任务
        """

        output = []
        if isinstance(message, ThreadMessage):
            contents: List[Content] = message.content   # 可能一个消息包含多种类型的内容，text, image, etc
            assert len(contents) == 1, "Only one content message is supported now. Please open a new message."
            # 读取message的内容
            if message.role == "user": ## 如果来自人类，用agent解析任务类型，覆盖任务列表
                output.append("insert")

                for i, conent in enumerate(contents):
                    content_obj: Text = getattr(conent, conent.type)
                    value = content_obj.value
                    annos = content_obj.annotations
                     
                    tasks = str_utils.extract_items_from_text(value) ## 提取可能的任务列表

                    ## 假如有任务清单则添加，假如没有则将原始文本作为任务插入任务树
                    if tasks: 
                        output.extend(tasks)
                    else:
                        output.append(value)
            else: # if message from a general agent, do not add tasks
                    return None

                ## 判断是否来自Planner/人类，若是，则创建新的任务列表
                # if message.sender == "Planner":
                #     try:
                #         text_dict: Dict = ast.literal_eval(value)
                #         plan = text_dict.get("Plan", None)
                #         if plan == "FINISH" or plan is None:  # 检索到结束词/没拿到plan字段，则该任务结束
                #             return None
                #         else:
                #             value = plan # 拿到plan字段，应当是str
                #     except Exception as e:  # 是一个纯str, 认为是user发的任务
                #         pass
                
                #     ## 提取子任务列表
                #     tasks = str_utils.split_to_list(value) # task list，支持用户输入的单个任务（str）/多个固定格式的任务
                #     output.append("add")
                #     output.extend(tasks)
                # if message.role == "user": ## 如果来自人类，用agent解析任务类型，覆盖任务列表
                #     output.append(value)
                #     system_message = """
                #         Dear userproxy,

                #         Your job is to analyze and understand the user request, then identify its task type and extract independent tasks if present. 
                        
                #         The available task types are:
                #         - **insert**: represents independent or spontaneous tasks. This is the default task type, give priority to this type if you can not find a better one.
                #         - **add**: Sub-tasks of a previous one.
                #         - **delete**: User wishes to remove a task.
                #         - **update**: User wants to change task details.
                #         - **select**: The user wants to view the task list associated with this project, and the request must include terms like "task," "task list," "task tree," or their equivalent in other languages. Typical examples of such concise and direct inquiries include:
                #             - "Show me the task list."
                #             - "What tasks do we have currently?"
                #             - "Where are we in the task tree?"

                #         You should be careful when extracting tasks from the user request, as the user may not always provide clear instructions. Here are some guidelines to follow:
                #         1. **Sequential Tasks**: If tasks are listed with numbers or sequential words, extract each as a separate task.
                #         2. **Ambiguous Requests**: If the request is unclear, no need to extract tasks.
                #         3. **Clear Requests**: Treat clear requests as a whole, especially when main tasks require sub-parameters. Do not split parameters as separate tasks unless necessary for further information to complete the request.
                #         4. **Special Case**: In our system, the search and result presentation are unified, requiring no further segmentation.
                #         5. **General Guidelines**: The decomposed tasks should closely adhere to the user's original wording, with modifications made only where essential.

                #         Finally, please respond in plain JSON format. Example:
                #         {
                #             "thoughts": "<Please outline your reasoning process in a clear, step-by-step manner, detailing how you reached your conclusion. Ensure this text can be loaded as a JSON object.>",
                #             "task_type": "<task type>",
                #             "tasks": ["<task 1>", "<task 2>"]
                #         }

                #         Your cooperation is crucial for my career. I believe you can complete this task well!
                #     """
                    
                #     user_proxy1 = LearnableAgent(
                #         name="user_proxy",
                #         system_message=system_message,
                #         llm_config=self.llm_config,
                #         human_input_mode="NEVER"
                #     )

                #     # user_proxy1 = LearnableAgent(
                #     #             name="user_proxy",
                #     #             system_message="""
                #     #             - Role: user proxy
                #     #             - Goal: To accurately categorize the user request into "insert", "delete", "update", "select", or "add".
                #     #             - Workflow:
                #     #                 1. Fully understand the user request.
                #     #                 2. Determine the relationship between the next task and the user request.
                #     #                 3. Determine the appropriate task category.
                #     #                 4. Return the task category.
                #     #             - OutputFormat: 
                #     #                 <Task category>
                #     #             - Task category guidelines:
                #     #                 - Return "delete" when the user request is to delete a task.
                #     #                 - Return "update" when the user request is to update the content of the NEXT task.
                #     #                 - Return "select" when the user request is to review the entire or part of the task list, task tree, or remaining tasks.
                #     #                 - Return "add" when the user request is to break down the next task into subtasks or EXPLICITLY requires to add subtasks for the current task.
                #     #                 - Return "insert" when the user request is irrelevant to the next task.
                #     #                 - When the user request is ambiguous, return default to "insert".
                #     #             - Example:
                #     #                 > output 1: "insert"
                #     #                 > output 2: "add"
                #     #             - Initialization: please analyze the following content and fulfill your goal.
                #     #             >>>>>
                #     #             """,
                #     #             llm_config=self.llm_config,
                #     #             human_input_mode="NEVER"
                #     #         )
                #     # user_proxy2 = LearnableAgent(
                #     #             name="user_proxy",
                #     #             system_message="""
                #     #             - Role: User Proxy
                #     #             - Goal: To identify the individual tasks from the user request.
                #     #             - Workflow:
                #     #                 1. Analyze the user request to determine the number of EXECUTABLE tasks it contains for subsequent execution.
                #     #                 2. If only a single task is identified or you cannot identify the content of the tasks, the task content should be EXACTLY the user request.
                #     #                 3. Return the identified tasks in the specified format.
                #     #             - OutputFormat: 
                #     #                 (0) <Task Category>
                #     #                 (1) <Task 1>
                #     #                 (2) <Task 2>
                #     #             (and so on for each task identified)
                #     #             - Exceptional Cases:
                #     #                 - If the user EXPLICITLY wants to review the entire or part of the task list, task tree, or remaining tasks, the task category should be "select" and the task content should be EXACTLY "show me the task list". An example output is:
                #     #                     (0) select
                #     #                     (1) show me the task list
                #     #                     (2) <Task 2>
                #     #                     (and so on for each task identified)
                #     #                 - If the user request is to modify the content of the current task (adding subtasks is not included), the task category should be "update" and the task content should be EXACTLY the refined content required by the user.
                #     #                 - If the user wants to search articles, regardless of the relationship between the keywords and assign them as a whole task.
                #     #             - Initialization: Please analyze the following content and fulfill your goal.
                #     #             >>>>>
                #     #             """,
                #     #             llm_config=self.llm_config,
                #     #             human_input_mode="NEVER"
                #     #         )
                #     ## 使用agent理解用户意图并生成任务列表
                #     message_to_userProxy = {'content': f"{value}", 'role': 'user', 'name': 'Human'}
                #     reply_user_proxy1 = user_proxy1.generate_reply(messages=[message_to_userProxy]) # 不用历史消息，因为user_proxy可能会对历史消息做出回应，导致重复拆分任务. PS: 也没把历史消息传过来啊？
                #     logger.info("\033[33m" + f"userproxy: {reply_user_proxy1}" + "\033[0m")
                #     try:
                #         reply_user_proxy_dict = json.loads(reply_user_proxy1)
                #         task_type = reply_user_proxy_dict.get("task_type", None)
                #         tasks = reply_user_proxy_dict.get("tasks", [])
                        
                #         output.append(task_type) if task_type else output.append("insert")
                #         output.extend(tasks) if tasks else output.append(value)
                #     except:
                #         output.append("insert")
                #         output.append(value)

                #     # message_to_userProxy = {'content': f"task at hand: '{self.current_task}'. If this is the last message, please focus on the user request: '{value}'.", 'role': 'user', 'name': 'Human'}
                #     # reply_user_proxy1 = user_proxy1.generate_reply(messages=[message_to_userProxy]) # 不用历史消息，因为user_proxy可能会对历史消息做出回应，导致重复拆分任务
                #     # reply_user_proxy2 = user_proxy2.generate_reply(messages=[message_to_userProxy]) # 不用历史消息，因为user_proxy可能会对历史消息做出回应，导致重复拆分任务
                #     #logger.info("\033[33m" + f"user_proxy reply: {reply_user_proxy1} + {reply_user_proxy2}" + "\033[0m")
                #     # logger.info("\033[33m" + f"user_proxy reply: {reply_user_proxy1}" + "\033[0m")
                #     # tasks = str_utils.split_to_list(reply_user_proxy2) # [task_type, task1, task2]
                #     # tasks[0] = reply_user_proxy1 # 临时方案，直接用agent1的回答作为任务类型
                # else: # if message from a general agent, do not add tasks
                #     return None
        else: # messages类型是List[str]，直接用它创建任务。 -- 主要是来自TaskManager的任务创建
            output = message
        
        return output

    def process_tasks_from_taskList(self, tasks: List[str], task_type: str="") -> str:
        '''
        处理任务，增删改查
        tasks是任务列表(str)，包含任务类型和任务内容。 = [task_type, task1, task2, ...]
        空tasks返回""
        '''
        
        tasks_tmp = tasks.copy()
        output = ""
        if tasks_tmp:
            if task_type == "" and any(element in tasks_tmp[0] for element in ["add", "insert", "delete", "update", "select"]): # 任务类型为空，则从任务列表中提取
                task_type = tasks_tmp.pop(0) # get the task category
            else:
                task_type = "insert" # 默认为插入任务

            if self.current_task == self._root_task or "add" in task_type: # 新建任务树，或拆分任务为子任务
                self.create_tasks(tasks_tmp)
                output = f"{len(tasks_tmp)} Tasks created as sub-tasks of the current task."
            elif "insert" in task_type: # 在当前任务前面插入新任务
                for task in reversed(tasks_tmp): # 倒序插入任务清单，保持任务列表正序
                    self.insert_task(task)
                output = f"{len(tasks_tmp)} Tasks inserted."
            elif "delete" in task_type: # 删除任务（连带其子任务分支）
                try:
                    self.delete_task() # 删除内容为“删除任务”的任务
                    self.delete_task() # 删除目标任务
                except:
                    pass
                output = f"Current Tasks deleted."
            elif "update" in task_type: # 更新当前任务
                self.delete_task() # 删除内容为“更新任务”的任务
                self._current_task.content = tasks_tmp[0] # 更新目标任务内容
                output = f"Current Task updated."
            elif "select" in task_type: # 显示任务列表
                output = f"The task tree is:\n{self.get_task_map()}"
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
        return output
    

    def select_speaker(self, last_speaker: Agent, selector: ConversableAgent, messages: List[Dict]) -> Agent:
        """Select the next speaker (with requery)."""

        # Prepare the list of available agents and select an agent if selection method allows (non-auto)
        selected_agent, agents, message = self._prepare_and_select_agents(last_speaker) # the output message is groupchat.messages
        if selected_agent:
            return selected_agent
        elif self.speaker_selection_method == "manual":
            # An agent has not been selected while in manual mode, so move to the next agent
            return self.next_agent(last_speaker)

        # auto speaker selection with 2-agent chat
        return self._auto_select_speaker(last_speaker, selector, messages, agents)
    
    def _auto_select_speaker(
            self, 
            last_speaker: Agent, 
            selector: LearnableAgent, 
            messages: List[Dict] | None, 
            agents: List[Agent] | None) -> Agent:
        """
        自动选择发言者。替换父类的函数。
        1. 修改默认的Agent为haigen的LearnableAgent
        """
        # return super()._auto_select_speaker(last_speaker, selector, messages, agents)

        # If no agents are passed in, assign all the group chat's agents
        if agents is None:
            agents = self.agents

        ## my attempt
        ## generate prompt for speaker selection
        roles = self._participant_roles(agents)
        agentlist = ", ".join([agent.name for agent in agents if agent.name != "Human"])
        # sys_msg = f"""
        #     - Role: Chatgroup Manager
        #     - Goal: Select the most appropriate next speaker from the list [{agentlist}] based on the chat log.
        #     - Strategy: Analyze chat context to identify the next required action and assign the task to the most suitable speaker.
        #     - Workflow:
        #         1. Review the chat log for current task status.
        #         2. Identify the next logical step in the conversation.
        #         3. Assign the next speaker from the list [{agentlist}] based on the task requirement.
        #     - Guidelines:
        #         - Thoroughly familiarize yourself with the capabilities of each role, preparing to make an informed decision on the most adept problem solver.
        #         - **DO NOT** engage with or respond to the content of the given dialogue itself, your sole focus is executing your speaker selection task effectively.
        #         - After choosing the next speaker, state exactly the role name from the list in the format with brackets: **[<role name>]**, and then conclude with a concise reason for your choice in less than 30 words.
        #         - If you can not identify the most appropriate speaker, please return the name: **"[Charm]"**
        #     - Available roles and their descriptions: 
        #         {roles}

        #     - Initialization: As the Chatgroup Manager, you MUST select the next speaker to effectively continue the conversation flow. Now please read the following chat log.
        #     >>>>>
        # """
        # sys_msg = f"""
        #     - Role: Chatgroup Manager
        #     - Goal: Select the most appropriate next speaker from the list [{agentlist}] based on the chat log.
        #     - Strategy: Analyze chat context to identify the next required action and assign the task to the most suitable speaker.
        #     - Workflow:
        #         1. Review the chat log to fully understand the chat flow.
        #         2. Identify the next logical step in the conversation and generate the corresponding task requirement.
        #         3. Assign the next speaker from the list [{agentlist}] based on the task requirement.
        #     - Guidelines:
        #         - Thoroughly familiarize yourself with the capabilities of each role, preparing to make an informed decision on the most adept problem solver.
        #         - **DO NOT** engage with or respond to the content of the given dialogue itself, your sole focus is executing your speaker selection task effectively.
        #         - After choosing the next speaker, state exactly the role name from the list in the format with brackets: **[<role name>]**, and then conclude with a concise reason for your choice in less than 30 words.
        #         - **ALWAYS** inclined to extract task information from the last message first. If an executable task cannot be constructed, evaluate other messages in the chag log in reverse order.
        #         - If you can not identify the most appropriate speaker, please return the name: **"[Charm]"**
        #     - Available roles and their descriptions: 
        #         {roles}

        #     - Initialization: As the Chatgroup Manager, you MUST select the next speaker to effectively continue the conversation flow. Now please read the following chat log.
        #     >>>>>
        # """
        system_message = f"""
            Dear Host,
    
            You'll receive a chat history followed by a task. Choose the best agent from [{agentlist}] to complete the task. Please focus on selecting the agent; don't respond to the chat content! Use the history to understand the context and task, noting that it may not always be relevant.

            Here is the list of available agent names and their abilities:
                "{roles}"

            **Guidelines:**
            - If the task seems overly complex, consider asking someone to break it down into simpler subtasks first.
            - If any concepts are unclear or you need more information, choose an expert to gather the necessary details. 
            - If none of the agents on the list is suitable for the task, choose the one capable of providing a general response.
            
            Please consider the intent and goal of the task step by step, then give your chosen agent name using a bracket, e.g., [<agent name>], and briefly state your reason. I believe you can do it well!
        """

        speaker_selector = LearnableAgent(
            name="Host",
            system_message= system_message,
            llm_config=selector.llm_config,
            human_input_mode="NEVER",
        )
        reply = speaker_selector.generate_reply(messages=messages)
        #logger.info(colored(f"auto-selected speaker: {reply}", "yellow"),)
        next_speaker_name = str_utils.extract_text_in_brackets(reply)

        if next_speaker_name in self.agent_names:
            speaker = self.agent_by_name(next_speaker_name)
            return speaker
        else:
            raise AssertionError(f"auto-selected agent: {next_speaker_name} not found")
    
    def _participant_roles(self, agents: List[Agent] = None) -> str:
        # Default to all agents registered
        if agents is None:
            agents = self.agents

        roles = []
        for agent in agents:
            if agent.name == "Human": ## TODO: 选human会导致错误
                continue
            if agent.description.strip() == "":
                logger.warning(
                    f"The agent '{agent.name}' has an empty description, and may not work well with GroupChat."
                )
            roles.append(f"**{agent.name}**: {agent.description}".strip())
        return "\n".join(roles)

