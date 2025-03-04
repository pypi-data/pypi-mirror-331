
from typing import Dict, Union, Optional, Literal, Callable
import os, sys
from pathlib import Path
here = Path(__file__).parent
try:
    from DrSai.version import __version__
except:
    sys.path.append(str(here.parent.parent.parent))
    from DrSai.version import __version__

from DrSai.apis.utils_api import load_configs, logging_enabled, log_new_agent, get_llm_config
from DrSai.configs import CONST
from DrSai.apis.base_agent_api import AssistantAgent, LearnableAgent


class TaskManager(AssistantAgent):
    """
    功能：
        管理任务列表
    """

    DEFAULT_DESCRIPTION = "An editor who is good at polishing academic writings."
    DEFAULT_SYSTEM_MESSAGE = """You will be given a text. **Do not respond directly** but identify the type of task and extract a numbered task list if present.

  **Task Types**:
  1. **insert**: Spontaneous tasks; use as default. 
    - *Example: "Can you tell me a joke?"*
    
  2. **add**: Request to add sub-tasks of an existing task. 
    - *Example: "I think this task can be broken down into smaller tasks."*
    - *Example: "This is the task list: 1.Task1 2.Task2 3.Task3. Execute them in order."*

  3. **delete**: Request to remove a specific task. 
    - *Example: "Delete this task."*

  4. **update**: Request to modify details of an existing task. 
    - *Example: "I don't want to do this, can you change it to '<another task request>'?"*

  5. **select**: Request to view the task list, including "task," "task list," or "task tree." 
    - *Example: "Provide the task list."*

  **Output Format**: Always respond in JSON format without any additional formatting. The output should be a JSON object, containing the identified task type and any extracted tasks. If no tasks are found, return an empty array.

  Example output format:
  {
    "task_type": "<type>",   // e.g., "add", "delete", "update", "select", "insert"
    "tasks": ["<task1>", "<task2>"] // Task list or empty array if none
  }

  Your cooperation is vital to my career! I trust in your abilities!
"""

    def __init__(
        self,
        name: str,
        system_message: Optional[str] = DEFAULT_SYSTEM_MESSAGE,
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        is_termination_msg: Optional[Callable[[Dict], bool]] = None,
        max_consecutive_auto_reply: Optional[int] = None,
        human_input_mode: Optional[str] = "NEVER",
        description: Optional[str] = None,
        **kwargs,
    ):
        # if system_message.endswith('.yaml'):
        #     self.prompt_template = load_configs(system_message)
        #     system_message = self.prompt_template['system']
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

        if logging_enabled():
            log_new_agent(self, locals())

        # Update the provided description if None, and we are using the default system_message,
        # then use the default description.
        if description is None:
            self.description = self.DEFAULT_DESCRIPTION
    
# if __name__ == "__main__":
#     config_file = f'{here.parent.parent}/configs/config.yaml'
#     configs = load_configs(config_file, include_env=False)
#     llm_config = get_llm_config(configs) 
#     editor = Editor("editor", llm_config=llm_config)
