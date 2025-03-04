
import os, sys
from pathlib import Path
import ast
from typing import Dict, Optional, Union, Callable, Literal, List, Tuple
from collections import OrderedDict
from DrSai.apis.base_agent_api import AssistantAgent, LearnableAgent
from DrSai.apis.autogen_api import logging_enabled, log_new_agent
from DrSai.apis.autogen_api import OpenAIWrapper, Agent
from DrSai.apis.utils_api import load_configs
from DrSai.configs import CONST

import json
import damei as dm
from dataclasses import dataclass, field
import uuid
from datetime import datetime
import re




class Planner(AssistantAgent):
    """(Dr.Sai) Planner, designed to solve a task with LLM for planning.

    Planner is a subclass of AssistantAgent → BaseAgent → ConversableAgent configured with a default system message.
    The default system message is designed to solve a task with LLM,
    including suggesting python code blocks and debugging.
    `human_input_mode` is default to "NEVER"
    and `code_execution_config` is default to False.
    This agent doesn't execute code by default, and expects the user to execute the code.
    """

    DEFAULT_DESCRIPTION = "An expert in designing detailed solutions for complex BESIII physical analysis with strong physical logical reasoning ability"
    DEFAULT_SYSTEM_MESSAGE = """- You are a planner for BESIII experiment.
  - Solve tasks using your physical logical reasoning ability.
  - Solve tasks setp by step if you need to.
  - You can search for informations in arxiv if you need.

  ## Guidelines
  - You are given a physical analysis task.
  Your response should be strictly structured in a JSON format, consisting of three distinct parts with the following keys and corresponding content:
  {
    "Observation": <Describe the progress status of a task or task.>
    "Thoughts": <Outline the logical next step required to fulfill the given task.>
    "Status": <Specify whether the task is finished or not. If the task is finished, output "FINISH". If the task is not finished and need further action, output "CONTINUE". You must output either "FINISH" or "CONTINUE" in this field.>
    "Plan": <Specify the following plan of action to complete the user request. You must provided the detailed steps of action to complete the user request. If you believe the task is finished and no further actions are required, output <FINISH>.>
    "Comment": <Specify any additional comments or information you would like to provide. This field is optional. If the task is finished, you have to give a brief summary of the task or action flow to answer the user request. If the task is not finished, you can give a brief summary of your observation of screenshots, the current progress or list some points for future actions that need to be paid attention to.>
  }
  - If the user request is just asking question and do not need to take action on the application, you should answer the user request on the "Comment" field, and set the "Status" as "FINISH".
  - You must to strictly follow the instruction and the JSON format of the response. 
  - Below are some example of the response. You can refer to them as a reference.

  ## Response Examples:
  - Example 1:
  User Request: 
    "run the simulation script using BOSS software"
  Response: 
    {"Observation": "I observe that output file in the simulation process does not exist.",
    "Thought": "I need to run the simulation script using BOSS software. According to the previous simulation process, the output file does not exist. So I need to run the simulation script, and check the output file.",
    "Status": "CONTINUE",
    "Plan": "(1) Write the simulation script.\\n(2) Run the simulation script using BOSS software.\\n(3) Run the simulation script.\\n(4) Check the output file.",
    "Comment": "The suffix name of output file of the simulation process is '.rtraw'. Use 'boss.exe sim.txt > sim.log' to run the simulation script. The 'sim.log' file will save the log of the simulation process."}

  - Example 2:
  User Request: 
    "check the output file of the simulation process"
  Response: 
    {"Observation": "I observe that the output file of the simulation process is 'sim.rtraw' and log file'sim.log'.",
    "Thought": "I need to check the output file of the simulation process. According to the previous simulation process, the output file is 'sim.rtraw' and 'sim.log'. So I need to check the log file 'sim.log' to see whether there is any error in the simulation process.",
    "Status": "CONTINUE",
    "Plan": "(1) Check there is any error in the 'sim.log' file.\\n(2) If there is no error, the simulation process is finished.\\n(3) If there is error, I need to output the error message in the 'sim.log' file.",
    "Comment": "The 'sim.log' file will save the log of the simulation process. If there is no error in the 'sim.log' file, the 'successfully' should appear for three times and no 'Error' appears. If there is error in the 'sim.log' file, the 'Error' will appear."}
    
  - Example 3:
  User Request: 
    "output the error message in the 'sim.log' file"
  Response: 
    {"Observation": "I observe that the error message in the 'sim.log' file exists.",
    "Thought": "I need to output the error message in the 'sim.log' file. According to the previous simulation process, the error message in the 'sim.log' file exists. So I need to output the error message in the 'sim.log' file.",
    "Status": "FINISH",
    "Plan": "FINISH",
    "Comment": "The error message may contain the information of the error type, error location and error reason."}
  
  - Example 4:
  User Request:
    "Draw an examples of invariant mass spectrum using ROOT."
  Response:
    {"Observation": "The user requests an example of an invariant mass spectrum to be drawn using BESIII Offline Software System(BOSS)",
    "Thoughts": "To draw an invariant mass spectrum, data from a particle physice experiment is required. Subsequently, analysis code in C++ needs to be written. Finally, the ROOT is to be invoked within the BOSS executor to draw and display the images.",
    "Status": "CONTINUE",
    "Plan": "(1) Write the analysis code in C++ to generate the dataset and calculate the invariant mass of the particles of interest.\\n(2) Use the ROOT framework within BOSS to plot the invariant mass spectrum.\\n(3) Return the log file and drawn figure.",
    "Comment": "Drawing an invariant mass spectrum is a common task in particle physics to identify or study particles. It involves calculating the invariant mass from the energy and momentum of the particles, which are obtained from the experimental data. The ROOT framework, widely used in particle physics for data analysis and visualization, will be utilized here for plotting."}

  - Example 5:
  User Request:
    "Search for Zc3900"
  Response:
    {"Observation": "The user requests to search for Zc(3900) in the BESIII experiment.",
    "Thoughts": "In order to search for the Zc(3900) particle, we need to look in specific decay channels and particle systems, typically in the $\pi^{\pm}J/\psi$ system within the $e^+e^-\to\pi^+\pi^-J/\psi$ process. I need to confirm with the user whether to use this decay channel or another before proceeding with the analysis task.",
    "Status": "CONTINUE",
    "Plan": "(1) Confirm the decay channels and physical system with the user, (2) generate MC (Monte Carlo simulations), (3) write analysis code to analyze both MC and real data, (4) create plots and perform statistical analysis.",
    "Comment": "",
    }


  This is a very important task. Please read the user request, think step by step and take a deep breath before you start. 
  Make sure you answer must be strictly in JSON format only, without other redundant text such as json header. Otherwise it will crash the system.
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
        """
        Args:
            name (str): agent name.
            system_message (str): system message for the ChatCompletion inference.
                Please override this attribute if you want to reprogram the agent.
            llm_config (dict or False or None): llm inference configuration.
                Please refer to [OpenAIWrapper.create](/docs/reference/oai/client#create)
                for available options.
            is_termination_msg (function): a function that takes a message in the form of a dictionary
                and returns a boolean value indicating if this received message is a termination message.
                The dict can contain the following keys: "content", "role", "name", "function_call".
            max_consecutive_auto_reply (int): the maximum number of consecutive auto replies.
                default to None (no limit provided, class attribute MAX_CONSECUTIVE_AUTO_REPLY will be used as the limit in this case).
                The limit only plays a role when human_input_mode is not "ALWAYS".
            **kwargs (dict): Please refer to other kwargs in
                [ConversableAgent](conversable_agent#__init__).
        """
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

        self.request_history = []
        self._current_task = None

        self.register_reply([Agent, None], Planner.generate_oai_reply, position=0)

        self._register_custom_hooks()

    def _register_custom_hooks(self):
        self.register_hook("process_all_messages_before_reply", self.process_msg_hook)
        self.register_hook("process_last_received_message", self.process_msg_last_recived_hook)
        self.register_hook("process_message_before_send", self.process_msg_before_send_hook)


    @property
    def current_task(self):
        return self._current_task
    
    @current_task.setter
    def current_task(self, value):
        self._current_task = value

    def process_msg_hook(self, messages: List[Dict]) -> List[Dict]:
        """Planner接收到消息，在reply前的处理钩子函数"""
        return messages
    
    def process_msg_last_recived_hook(self, user_request: str) -> str:
        """
        Planner接收最后一条消息，在reply前的处理钩子函数
        """
        
        return user_request
    

    def process_msg_before_send_hook(self, sender, message, recipient, silent) -> str:
        """
        智能体A向智能体B发送消息前对消息的处理钩子函数:
        例如：Panner生成"{"Obser...}"之后，对消息进行处理
        """
        return message
    

    def format_last_message_from_prompt_template(self, user_request: str) -> str:
        user_template = self.prompt_template['user']

        new_prompt = user_template.format(
            request_history=json.dumps(self.request_history),  # :-1:是和generate_oai_reply添加history的顺序对应
            # prev_plan=json.dumps(self.plans),
            user_request=user_request
        )
        return new_prompt
    

    def generate_oai_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[OpenAIWrapper] = None,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        
        # 提示工程：对最后一条消息进行处理
        last_message = messages[-1]
        user_text = last_message.get("content", None)
        processed_user_text = self.format_last_message_from_prompt_template(user_text)
        messages = messages.copy()
        messages[-1]["content"] = processed_user_text
        if user_text:
            self.request_history.append(user_text)
        
        final, reply = super().generate_oai_reply(messages=messages, sender=sender, config=config)
        
        return (final, reply)
    
    def receive(self, message: Dict | str, sender: Agent, request_reply: bool | None = None, silent: bool | None = False):
        super().receive(message, sender, request_reply, silent)



