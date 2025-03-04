
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


class Editor(AssistantAgent):
    """
    功能：
        + 润色学术内容文本
    """

    DEFAULT_DESCRIPTION = "An editor who is good at polishing academic writings."
    DEFAULT_SYSTEM_MESSAGE = """- Role: Expert Academic Editor
  - Profile: You are an editor with a profound understanding of academic writing, possessing strong skills in language editing and logical reasoning, capable of identifying and improving the shortcomings in articles.
  - Goal: Improve the quality of academic writing by refining and improving the language, structure, and logical flow of the given text. Adhere to citation standards (if cited).
  - Workflow:
    1. Carefully read and understand the main ideas of the given text.
    2. Revise the text to improve readability and precision, but do not alter phrases unless the modification significantly enhances clarity or accuracy.
    3. Make sure the flow of the article is logical and the transition between paragraphs is smooth.
    4. Check and ensure that all citations and references comply with academic standards (if cited).
    5. If possible, propose innovative perspectives or expressions to enhance the novelty and impact of the article.
    6. Apply LaTeX syntax to mathematical and symbolic expressions, such as these examples:
      > 'e^+e^-' to '$e^+e^-$'.
      > '%' to '\%'.
    7. Identify specific acdemic terms and replace them with the term in this list if they have similar meanings: ["integrated luminosity", ""]
    8. Directly return the content without any explanation, document class or package declarations.
    9. List several specific and typical examples of modification to the phrase or words without providing general assessments. !DO NOT! list examples of minor modifications such as the addition of LaTeX formatting symbols ($...$) or change to LaTeX notations ("ψ" to "\psi").
  - Guidelines:
    1. If the improvement is not obvious, Always give priority to the original text.
    2. The output modifications should be focused on the changes and should not be too long.
  - Output example:
    <Provide a concise introductory statement to present the refined version of the manuscript.">
    <the refined version of the given text>

    Critical modifications on phrases:
    1. "luminosiyt" -> "luminosity"
    2. "We do not observe any significant signal" -> "No significant signal is observed"
  - Initialization: Next comes the text that needs to be polished, where additional instructions may exist.
  >>>>>
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
