from hepai import HRModel, LRModel
import logging
logger = logging.getLogger(__name__)
import json
from typing import List, Dict, Union, Any
import os

# def rag_operation_api_DDF2(
#         request_headers: Dict[str, Any] = None,
#         request_data: Dict[str, Any] = None,
#         **kwargs) -> LRModel:
#     """rag DDF2 worker api"""
#     try:
#         params = {}
#         params["base_url"] = request_data.get("base_url", "http://aiapi001.ihep.ac.cn")
#         params["name"] = request_data.get("model", "hepai/hep-rag-OS")
#         retrieve_work_api_key = request_headers.get("Authorization", None)
#         if retrieve_work_api_key is not None:
#             params["api_key"] = retrieve_work_api_key.split(" ")[-1]
#         RAGmodel = HRModel.connect(**params)
#         result: Union[List, Dict, str, bool] = RAGmodel.interface(**request_data)
#         return result
#     except Exception as e:
#         print(f"rag_operation_api_DDF2 error: {e}")
#         return None

# def retrieve_by_query_text(
#         request_data: Dict[str, Union[str, int, float, bool]],
#         headers: Dict[str, str],
#         query_text: str = None)->List[str]:

#     request_data["content"] = query_text
#     # print("request_data:",request_data)

#     retreve_cases_txt = []
#     data = rag_operation_api_DDF2(request_headers = headers, request_data = request_data, stream=False)
#     if data:
#         score_limit = request_data.get("score_limit", 0.5)
#         for i in range(len(data)):
#             if score_limit <= data[i]['score']:
#                 retreve_cases_txt.append(data[i]['node']['text']) 
#         print(f"Hai-RAG retrieve case: {len(retreve_cases_txt)}")
#         return retreve_cases_txt
#     else:
#         return retreve_cases_txt

# def hai_rag_retrieve(
#         messages: List[Dict] = None,
#         memory_config: Dict[str, any] = None,
#         **kwargs) -> Union[List[Dict], None]:
#     """retrieve DDF2 worker api"""

#     # 使用最后一条消息进行查询,j将查询消息放到最后一条消息中
#     query_text = messages[-1]['content']
#     request_data = memory_config.get("request_data", {})
#     headers = memory_config.get("headers", {})
#     retrieve_list:List = retrieve_by_query_text(
#         request_data=request_data, 
#         headers=headers,
#         query_text = query_text)
#     # print(retrieve_list[0])
#     if len(retrieve_list) > 0:
#         retreve_cases_txt = ""
#         for i in range(len(retrieve_list)):
#             retreve_cases_txt += f"\n{i+1}:{retrieve_list[i]}\n"
#         prefix_prompt = kwargs.get("prefix_prompt", "")
#         # if prefix_prompt == "":
# #             prefix_prompt = f""" - Workflow:
# #   1. Receive user's question.
# #   2. Analyze the relevance of the question to the retrieved information.
# #   3. If the question is highly relevant to the retrieved information, extract relevant information to assist in answering; if not, respond directly.
# # - Examples:
# #   - Example 1: User asks "Hello," respond directly with "Hello! How can I assist you today?"
# #   - Example 2: User asks "What are the latest advancements in AI technology that I retrieved yesterday?" Analyze the retrieved information, extract information related to the latest advancements in AI technology, and provide an answer.
# #   - Example 3: User asks "What are the recent tech news?" Analyze the retrieved information, extract recent tech news, and provide an answer.
# # """
        
#         prefix_prompt += f"The retrieved information is:\n{retreve_cases_txt}"
#         prefix_prompt += f"\n- User's question: {query_text}"
#         messages[-1]["content"] = prefix_prompt
#         return messages
#     else:
#         return None

class hairag:
    def __init__(
            self, 
            memory_config,
            messages: List[Dict] = None,):
        self.query_text: str = messages[-1]["content"]
        self.request_data: dict = memory_config.get("request_data", {})
        self.request_data["content"] = self.query_text
        self.request_headers: dict = memory_config.get("headers", {})
        params = {}
        params["base_url"] = self.request_data.get("base_url", "http://aiapi001.ihep.ac.cn")
        params["name"] = self.request_data.get("model", "hepai/hep-rag-OS")
        retrieve_work_api_key = self.request_headers.get("Authorization", None)
        if retrieve_work_api_key is not None:
            params["api_key"] = retrieve_work_api_key.split(" ")[-1]
        self.RAGmodel = HRModel.connect(**params)
        self.method = memory_config.get("method", "retrieve")
    
    def retrieve_func(self, **kwargs):
        return self.RAGmodel.interface(**kwargs)
    
    def nodes_relationships(self, result:dict, **kwargs):
        if self.method == "retrieve":
            self.relationships: dict = result["node"]["relationships"]
        elif self.method == "docs":
            self.relationships: dict = json.loads(result["payload"]['_node_content'])['relationships']
        else:
            logger.error("Method not supported")
            return None 
        try:
            dict_relationships = {
                "CHILD": self.relationships.get('5', {}).get("node_id"),
                "NEXT": self.relationships.get('3', {}).get("node_id"),
                "PARENT": self.relationships.get('4', {}).get("node_id"),
                "PREVIOUS": self.relationships.get('2', {}).get("node_id"),
                "SOURCE": self.relationships.get('1', {}).get("node_id"),
                }
            # print(dict_relationships)
            return dict_relationships
        except:
            logger.error("Relationships not found")
            return None
    
    def get_full_text(self):
        results: list = self.retrieve_func(**self.request_data)
        retreve_cases_txt = []
        if len(results) == 0:
            logger.warning("No results found")
        else:
            score_limit = self.request_data.get("score_limit", 0.5)
            SOURCE_id_list = []
            for result in results:
                if score_limit <= result['score']:
                    relationships = self.nodes_relationships(result)
                    if relationships is not None:
                        SOURCE_id = relationships.get("SOURCE")
                        if SOURCE_id in SOURCE_id_list:
                            continue
                        else:
                            SOURCE_id_list.append(SOURCE_id)
                        self.request_data["method"] = "docs"
                        self.request_data["doc_id"] = SOURCE_id
                        members = self.retrieve_func(**self.request_data)
                        text = ""
                        for member in members:
                            member_text = json.loads(member["payload"]['_node_content'])["text"]
                            text += member_text
                        retreve_cases_txt.append(text)
        return retreve_cases_txt

def hai_rag_retrieve(
        messages: List[Dict] = None,
        memory_config: Dict[str, any] = None,
        **kwargs) -> Union[List[Dict], None]:
    """retrieve DDF2 worker api"""

    # 使用最后一条消息进行查询,将查询消息放到最后一条消息中
    query_text = messages[-1]['content']
    hr = hairag(memory_config = memory_config, messages = messages)
    retrieve_list:List = hr.get_full_text()
    if len(retrieve_list) > 0:
        retreve_cases_txt = ""
        for i in range(len(retrieve_list)):
            retreve_cases_txt += f"\n{i+1}:\n{retrieve_list[i]}\n"
        prefix_prompt = kwargs.get("prefix_prompt", "")
        # if prefix_prompt == "":
#             prefix_prompt = f""" - Workflow:
#   1. Receive user's question.
#   2. Analyze the relevance of the question to the retrieved information.
#   3. If the question is highly relevant to the retrieved information, extract relevant information to assist in answering; if not, respond directly.
# - Examples:
#   - Example 1: User asks "Hello," respond directly with "Hello! How can I assist you today?"
#   - Example 2: User asks "What are the latest advancements in AI technology that I retrieved yesterday?" Analyze the retrieved information, extract information related to the latest advancements in AI technology, and provide an answer.
#   - Example 3: User asks "What are the recent tech news?" Analyze the retrieved information, extract recent tech news, and provide an answer.
# """
        
        prefix_prompt += f"The retrieved information is:\n{retreve_cases_txt}"
        prefix_prompt += f"\n- User's question: {query_text}"
        messages[-1]["content"] = prefix_prompt
        return messages
    else:
        return None     

                    


if __name__ == '__main__':
    # from hepai import HepAI
    # hepai_client = HepAI(api_key=os.environ.get('HEPAI_API_KEY2'), base_url="https://aiapi.ihep.ac.cn/apiv2")
    # models = hepai_client.models.list()
    # print(models)

    # 测试用例
    messages = [{"role": "user", "content": "产生 'J/psi -> [rho+ -> pi+ pi0] pi-' 过程的分析算法的JSON文件。要求产生能量是3.097 GeV, 并且做运动学拟合，不要求加其它任何约束。"}]
    api_key = os.environ.get('HEPAI_API_KEY2')
    # headers={"Authorization": f"Bearer {api_key}"}
    headers={}
    # HaiRag Retrieval #
    request_data = {
        "model": "hepai/hep-rag-OS",
        "username": "xiondb",
        "method": "retrieve",
        "base_url": "http://localhost:42899/apiv2",
        "similarity_top_k": 10,
        'collection':"MC_template",
        "score_limit": 0.5,
    }
    memory_config = {"request_data": request_data, "headers": headers}

    result = hai_rag_retrieve(messages, memory_config)
    print(result)

    # hr = hairag(memory_config = memory_config, messages = messages)
    # hr.get_full_text()
# funcs = model.functions()  # Get all remote callable functions.
# print(f"Remote callable funcs: {funcs}")

# # Example: Call the remote function "get_collections" to get all collections.
# result = model.inference(
#     username="zijieshang",  # 必填，提供您的用户名
#     collection="test",  # 必填，提供您要创建的collection名称
#     method="get_collections"    # 指定要调用的方法
# )
# print(result)