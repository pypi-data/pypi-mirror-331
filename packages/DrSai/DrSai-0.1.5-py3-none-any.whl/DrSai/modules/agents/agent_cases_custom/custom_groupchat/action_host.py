import os, sys
from typing import List, Dict, Tuple, Optional, Any, Literal, Callable
from typing_extensions import Annotated
# import requests
# from bs4 import BeautifulSoup
# import mechanize
# import urllib.error
# import http.cookiejar as cookielib
# import urllib.request
# import feedparser
from urllib.parse import quote
import json
# import arxiv
# import time
# import re

from pathlib import Path
here = Path(__file__).parent
try:
    from DrSai.version import __version__
except:
    sys.path.append(str(here.parent.parent.parent))
    from DrSai.version import __version__
from DrSai.configs import CONST
from DrSai.apis.base_agent_api import LearnableAgent
from DrSai.utils import Logger
from DrSai.utils import str_utils

logger = Logger.get_logger("action_host.py")


#########################################################################################################
## 工具函数
# def create_function(function_name: str, agent: LearnableAgent, description: str) -> Callable:
#     """
#     批量创建函数
#     """
#     expert_name = function_name.split("_")[1]
#     @agent.register_for_execution()
#     @agent.register_for_llm(description=description)
#     @str_utils.print_args
#     def dynamic_function(
#             request: Annotated[str, f"The request for the {expert_name}. Please describe your needs clearly and in detail to receive the most accurate advice. Include relevant context and key information."],
#             **kwargs: Annotated[Any, ""],
#         ) -> Dict:
       
#         output = {
#             "expert": expert_name,
#             "request": request,
#         }
        
#         return output
    
#     dynamic_function.__name__ = function_name
#     return dynamic_function

#########################################################################################################
## 注册函数
def select_speaker(agent: LearnableAgent):
    ## The speaker and its description for calling
    speaker_list = [
        {
            "name": "Planner",
            "description": "If you need to create a plan for any task, consult the Planner for guidance on breaking down complex multi-step tasks into actionable steps.",
        },
        {
            "name": "Coder",
            "description": "When you need help with coding in Python, C++, or Shell, or require expertise in the BESIII BOSS software framework and high-energy physics tools like ROOT, ROOFIT, and PYROOT, turn to the Coder.",
        },
        {
            "name": "Tester",
            "description": "Consult the Tester when you have code that needs to be executed and tested for functionality and reliability.",
        },
        {
            "name": "Editor",
            "description": "For assistance with writing and editing texts, particularly academic papers in Chinese and English, reach out to the Editor.",
        },
        {
            "name": "Navigator",
            "description": "If you need to search for academic articles and retrieve information from databases such as arXiv, INSPIRE, or DocDB, the Navigator is your go-to expert; keep in mind this expert only returns information in a fixed format and may require additional input for reliability.",
        },
        {
            "name": "Charm",
            "description": "For comprehensive knowledge about the BESIII project and related information, consult the Charm expert.",
        },
        {
            "name": "TaskManager",
            "description": "Contact the TaskManager for tasks requiring immediate action, such as adding, removing, or updating items, and checking progress of individual tasks or the entire list. Do not contact the TaskManager for tasks that do not have an immediate execution intent, like 'create a travel itinerary'.",
        },
        {
            "name": "WebNavigator",
            "description": "Contact the WebNavigator if you need to search for common information on the web.",
        },
    ]


    thoughts = "Talk about the action you plan to take and the reasons behind it."
    #thoughts = "**Provide the situation of the conversation**, then talk about the action you plan to take and the reason behind it."
    #thoughts = "**tell me what you see about the conversation, and if there's anything abnormal in it. Especially the part of ideas you see**, **tell me if you see any ideas**. **tell me if you see any ideas**. **tell me if you see any ideas**.then talk about the action you plan to take and the reason behind it."
    #request_detail = "给出你的请求内容，其中应当包含**所有**已知的相关细节。你清楚这个意思吗？请确保请求内容没有遗漏，这对我很重要!我相信你能完成的很好。"
    request_detail = "基于所有已知的细节，详细且具体地描述你需要咨询的内容。"
    #request_detail = "罗列你所知道的所有细节，然后基于这些细节，详细描述你的请求。例如：话题是'明年6月份在武汉的会议安排是什么'，你的请求内容应该是'请告诉我明年6月份在武汉的会议安排'。话题是 “在广州市中心 100 平米左右的三居室且预算在 500 万以内的房产有哪些”，你的请求内容应该是 “请搜索广州市中心面积约 100 平米、户型为三居室且价格在 500 万以内的房产详细信息”。"
    #request_detail = "Precisely formulate your request by incorporating all the relevant details that are currently known. Ensure that the request is comprehensive and specific. Do you understand this instruction? It is of great significance to me."
    ## register the function
    # function_dict = {}
    # for speaker in speaker_list:
    #     function_name = f"ask_{speaker['name']}"
    #     description = speaker["description"]
    #     create_function(function_name=function_name, agent=agent, description=description)

    @agent.register_for_execution()
    @agent.register_for_llm(description=speaker_list[0]["description"])
    @str_utils.print_args
    def ask_planner(
        thoughts: Annotated[str, thoughts],
        all_details: Annotated[str, "罗列话题中释出的所有关键信息"], # 4o-mini的tool_call不够智能，经验得知加入这个参数能够提升request内容准确性。
        request: Annotated[str, request_detail],
        **kwargs: Annotated[Any, ""], # in case unexpected arguments from LLM
    ) -> str:
        extra_info = kwargs.get("kwargs", None)
        if extra_info:
            request = f"{request}. Extra infos: {json.dumps(extra_info)}"
            
        output = {
            "expert": {speaker_list[0]['name']},
            "request": request,
            "thoughts": thoughts + f"\nConsulting '{speaker_list[0]['name']}' for assistance.",
        }
        
        return output
    
    @agent.register_for_execution()
    @agent.register_for_llm(description=speaker_list[1]["description"])
    @str_utils.print_args
    def ask_Coder(
        thoughts: Annotated[str, thoughts],
        all_details: Annotated[str, "罗列话题中释出的所有关键信息"], # 4o-mini的tool_call不够智能，经验得知加入这个参数能够提升request内容准确性。
        request: Annotated[str, request_detail],
        **kwargs: Annotated[Any, ""], # in case unexpected arguments from LLM
    ) -> str:
        extra_info = kwargs.get("kwargs", None)
        if extra_info:
            request = f"{request}. Extra infos: {json.dumps(extra_info)}"
            
        output = {
            "expert": speaker_list[1]['name'],
            "request": request,
            "thoughts": thoughts + f"\nConsulting '{speaker_list[1]['name']}' for assistance.",
        }
        
        return output
    
    @agent.register_for_execution()
    @agent.register_for_llm(description=speaker_list[2]["description"])
    @str_utils.print_args
    def ask_Tester(
        thoughts: Annotated[str, thoughts],
        all_details: Annotated[str, "罗列话题中释出的所有关键信息"], # 4o-mini的tool_call不够智能，经验得知加入这个参数能够提升request内容准确性。
        request: Annotated[str, request_detail],
        **kwargs: Annotated[Any, ""], # in case unexpected arguments from LLM
    ) -> str:
        extra_info = kwargs.get("kwargs", None)
        if extra_info:
            request = f"{request}. Extra infos: {json.dumps(extra_info)}"
            
        output = {
            "expert": speaker_list[2]['name'],
            "request": request,
            "thoughts": thoughts + f"\nConsulting '{speaker_list[2]['name']}' for assistance.",
        }
        
        return output

    @agent.register_for_execution()
    @agent.register_for_llm(description=speaker_list[3]["description"])
    @str_utils.print_args
    def ask_Editor(
        thoughts: Annotated[str, thoughts],
        request: Annotated[str, f"The request for the {speaker_list[3]['name']}. {request_detail}"],
        **kwargs: Annotated[Any, ""], # in case unexpected arguments from LLM
    ) -> str:
        extra_info = kwargs.get("kwargs", None)
        if extra_info:
            request = f"{request}. Extra infos: {json.dumps(extra_info)}"
            
        output = {
            "expert": speaker_list[3]['name'],
            "request": request,
            "thoughts": thoughts + f"\nConsulting '{speaker_list[3]['name']}' for assistance.",
        }
        
        return output
    
    @agent.register_for_execution()
    @agent.register_for_llm(description=speaker_list[4]["description"])
    @str_utils.print_args
    def ask_Navigator(
        thoughts: Annotated[str, thoughts],
        #thoughts: Annotated[str, ""],
        all_details: Annotated[str, "罗列话题中释出的所有关键信息"], # 4o-mini的tool_call不够智能，经验得知加入这个参数能够提升request内容准确性。
        request: Annotated[str, request_detail],
        #case_of_ideas: Annotated[str, "the summary of the ideas from other perspectives you see in the conversation. OR tell me how many speakers in the conversation and what they are talking about. **tell me If there's any info from teh assistants?**"],
        #case_of_ideas: Annotated[str, "**tell me If there's any info from the assistants, not from user?**"],
        #reflection: Annotated[str, "在这个参数中的返回值中给出你对thoughts和request两个参数的返回值是否符合它们的描述的反思。"],
        #reflection: Annotated[str, ""],
        # thoughts_on_ideas: Annotated[str, "your thoughts on the ideas you see in the conversation"],
        # is_satisfied: Annotated[str, "whether you are satisfied with your request and thoughts"],
        **kwargs: Annotated[Any, ""], # in case unexpected arguments from LLM
    ) -> str:
        extra_info = kwargs.get("kwargs", None)
        if extra_info:
            request = f"{request}. Extra infos: {json.dumps(extra_info)}"
        
        output = {
            "expert": speaker_list[4]['name'],
            "request": request,
            "thoughts": thoughts + f"\nConsulting '{speaker_list[4]['name']}' for assistance.",
        }
        
        return output
    
    @agent.register_for_execution()
    @agent.register_for_llm(description=speaker_list[5]["description"])
    @str_utils.print_args
    def ask_Charm(
        thoughts: Annotated[str, thoughts],
        all_details: Annotated[str, "罗列话题中释出的所有关键信息"], # 4o-mini的tool_call不够智能，经验得知加入这个参数能够提升request内容准确性。
        request: Annotated[str, request_detail],
        **kwargs: Annotated[Any, ""], # in case unexpected arguments from LLM
    ) -> str:
        extra_info = kwargs.get("kwargs", None)
        if extra_info:
            request = f"{request}. Extra infos: {json.dumps(extra_info)}"

        output = {
            "expert": speaker_list[5]['name'],
            "request": request,
            "thoughts": thoughts + f"\nConsulting '{speaker_list[5]['name']}' for assistance.",
        }
        
        return output
    
    @agent.register_for_execution()
    @agent.register_for_llm(description=speaker_list[6]["description"])
    @str_utils.print_args
    def ask_TaskManager(
        thoughts: Annotated[str, thoughts],
        all_details: Annotated[str, "罗列话题中释出的所有关键信息"], # 4o-mini的tool_call不够智能，经验得知加入这个参数能够提升request内容准确性。
        request: Annotated[str, request_detail],
        **kwargs: Annotated[Any, ""], # in case unexpected arguments from LLM
    ) -> str:
        extra_info = kwargs.get("kwargs", None)
        if extra_info:
            request = f"{request}. Extra infos: {json.dumps(extra_info)}"
        
        output = {
            "expert": speaker_list[6]['name'],
            "request": request,
            "thoughts": thoughts + f"\nConsulting '{speaker_list[6]['name']}' for assistance.",
        }
        
        return output
    
    @agent.register_for_execution()
    @agent.register_for_llm(description=speaker_list[7]["description"])
    @str_utils.print_args
    def ask_WebNavigator(
        thoughts: Annotated[str, thoughts],
        all_details: Annotated[str, "罗列话题中释出的所有关键信息"], # 4o-mini的tool_call不够智能，经验得知加入这个参数能够提升request内容准确性。
        request: Annotated[str, request_detail],
        **kwargs: Annotated[Any, ""], # in case unexpected arguments from LLM
    ) -> str:
        extra_info = kwargs.get("kwargs", None)
        if extra_info:
            request = f"{request}. Extra infos: {json.dumps(extra_info)}"
        
        output = {
            "expert": speaker_list[7]['name'],
            "request": request,
            "thoughts": thoughts + f"\nConsulting '{speaker_list[6]['name']}' for assistance.",
        }
        
        return output
    


def all_tools(agent: LearnableAgent):
    select_speaker(agent=agent)
