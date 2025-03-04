from typing import List, Dict, Union, Generator, Any, Literal
import inspect
import json
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from hepai import ChatCompletion as ChatCompletion2
from hepai import Stream as Stream2
from openai import Stream
from hepai import HepAI

class Tools_call:
    def __init__(
            self, 
            Funcs: list[callable] = None,
            hepai_api_key: str = None,
            base_url: str = "https://aiapi.ihep.ac.cn/apiv2",
            llm_model_name: str = "openai/gpt-4o-mini"):
        
        assert hepai_api_key is not None, "Please provide a valid API key for HepAI"
        self.Funcs = Funcs
        self.llm_model_name = llm_model_name
        self.hepai_client = HepAI(
            api_key = hepai_api_key,
            base_url = base_url
            )
    
    def construct_openai_tool(
            self,
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
    
    def call_llm(self, 
                 messages: List[Dict], 
                 system_message: str = None,
                 request_json: bool = False,
                 stream: bool = True,
                 tools: List[Dict] = None,
                 hepai_client: HepAI = None,
                 llm_model_name: str = None,
                 **kwargs) -> Union[str, Dict, Generator]:
        """
        调用LLM处理数据信息请求, request_json可以输出json，以匹配函数参数要求,否则返回完整的LLM输出str或者Stream
        """
    
        if hepai_client is None:
            hepai_client = self.hepai_client
        if system_message:
            system_message = [{"role": "system", "content": system_message}]
            messages = system_message + messages
        if request_json or tools is not None:
            stream = False
        if llm_model_name is None:
            llm_model_name = self.llm_model_name
        try:
            
            if hepai_client.base_url.path == "/v1/":
                stream = True
            param = {
                "model" : llm_model_name,
                "messages" : messages,
                "stream" : stream,
                "tools" : tools,
            }
            if request_json and not tools:
                response_format = { "type": "json_object" }
                param["response_format"] = response_format
                param.pop("tools")
            param.update(kwargs)
            res: Union[ChatCompletion, Stream, Any] = hepai_client.chat.completions.create(
                **param
                )
            if (isinstance(res, Stream)) or (isinstance(res, Stream2)):
                if stream and (request_json is False):
                    return res
                else:
                    msg_response = ""
                    full_response = ""
                    function_name = ""
                    for i, msg in enumerate(res):
                        # print(msg)
                        x_msg = msg.choices[0].delta.content if isinstance(msg, ChatCompletionChunk) else msg
                        if x_msg:  
                            msg_response += x_msg
                        x_tool = msg.choices[0].delta.tool_calls
                        if x_tool:
                            function_name = x_tool[0].function.name or function_name
                            full_response += x_tool[0].function.arguments

                response = msg_response if msg_response else full_response
                
            else:
                msg_response = res.choices[0].message.content
                full_response = ""
                function_name = ""
                if res.choices[0].message.tool_calls:
                    full_response = res.choices[0].message.tool_calls[0].function.arguments
                    function_name = res.choices[0].message.tool_calls[0].function.name
                response = msg_response if msg_response else full_response
            
            if request_json:
                try:
                    method_params = json.loads(response)
                except Exception as e:
                    # 使用正则表达式从'```json\n{"method_name": "daisy_WorkflowCTReconstruct", "method_id": "c90f08af-14a2-4aa3-bd0f-8a711c1268b0", "reason": "daisy_WorkflowCTReconstruct。"}\n```'提取json
                    import re
                    match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
                    if match:
                        json_str = match.group(1)
                        method_params = json.loads(json_str)
                    else:
                        # raise Exception(f"无法从'{response}'中提取json")
                        return response
                return {"method_name": function_name, "method_params": method_params}
            else:
                return response
        except Exception as e:
            raise str(e)


    def function_interface(
            self,
            messages: list[dict[str, str]], 
            **kwargs: Any) -> Union[str, Dict, Generator]:
        tools = []
        Funcs: list[callable] = kwargs.pop("Funcs", self.Funcs)
        for Func in Funcs:
            tool: dict = self.construct_openai_tool(Func = Func)
            tools.append(tool)
        params: dict = self.call_llm(
            messages = messages, 
            tools = tools, 
            request_json=True,
            top_p=1.0,
            temperature=0.0
            )
        try:
            method_name = params.get("method_name", None)
            method_params: dict = params.get("method_params", {})
            method_params.update(kwargs)
            for Func in self.Funcs:
                if Func.__name__ == method_name:
                    output = Func(**method_params)
                    return output
        except Exception as e:
            return ValueError(f"Error: extracting method_params bacause of {e}")
        
        # response: ChatCompletionChunk = self.hepai_client.chat.completions.create(
        #     model = "openai/gpt-4o-mini",
        #     messages = messages,
        #     tools = [tool],
        #     top_p=1.0,
        #     temperature=0.0,
        #     stream=False
        #     )
        # if response.choices[0].finish_reason == "tool_calls":
        #     params = response.choices[0].message.tool_calls[0].function.arguments
        #     params = ast.literal_eval(params)
        #     output = Func(**params)
        # else:
        #     output = response.choices[0].message.content
        # return output