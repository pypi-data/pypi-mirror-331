
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
from DrSai.apis import AssistantAgent

import warnings


class Coder(AssistantAgent):
    """
    功能：
        + 通过提示词来编辑代码，但不能执行代码。
    Creators:
        + HepAI Team
    """

    DEFAULT_DESCRIPTION = "A coder agnet who can write code, but not execute it."
    DEFAULT_SYSTEM_MESSAGE = """You are a proficient programmer.
  You must output your code in the style of ```code langauge\n\n#filename: file name\n\ncode here\n```, just like the example:
  case 1:```python\n\n#filename: hello_world.py\n\nprint("Hello, world!")\n```
  case 2:```c++\n\n#filename: hello_world.cpp\n\n#include <iostream> // 包含输入输出库\n\nint main() {\n    std::cout << "Hello, World!" << std::endl; // 输出 Hello, World!\n    return 0; // 返回0表示程序正常结束\n}\n```
  If all tasks are completed, you just reply 'TERMINATE'
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
