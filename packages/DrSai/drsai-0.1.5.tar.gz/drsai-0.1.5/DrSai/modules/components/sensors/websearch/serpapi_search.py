
import requests
import time
import requests
from typing import Any, Literal, Annotated, Union, Dict, Generator
from DrSai.apis.utils_api import Tools_call


# 定义serpapi函数
def serpapi_search(
    query: Annotated[str, "Questions or keywords that need to be searched"],
    engine: Annotated[Literal["google_scholar", "google", "bing", "baidu"], "The search engine to use."] = "google_scholar",
    **kwargs: Annotated[Any, "Additional keywords to be passed to the function."], # so many similar search functions, the parameters may be confusing for LLM.
) -> str:
    """
    Retrieve a wide range of up-to-date and various information from the internet.
    """
    api_key_serpapi = kwargs.get("serpapi_api_key", None)

    engine=engine.lower()

    base_url = "https://serpapi.com/search.json"
    url = f"{base_url}?engine={engine}&q={query}&api_key={api_key_serpapi}"
    response = requests.get(url)
    results = response.json()
    organic_results = results.get("organic_results", [])
    
    output = ""
    for r in organic_results:
        #str_utils.print_json(result)
        position = r.get("position", "")
        title = r.get("title", "")
        link = r.get("link", "")
        snippet = r.get("snippet", "")
        output += f"**Result {position}:**\nTitle: {title}\nSnippet: {snippet}\nLink: {link}\n\n"
    
    if output:
        output = "Here are the search results from " + engine + ":\n\n" + output
    else:
        output = "No results found from " + engine + "."
    
    time.sleep(3) # 延迟3秒，避免频繁访问服务器
    return output

class SerpAPISearch(Tools_call):
    def __init__(
            self, 
            Funcs: list[callable] = [serpapi_search], 
            hepai_api_key: str = None,
            base_url: str = "https://aiapi.ihep.ac.cn/apiv2",
            llm_model_name: str = "openai/gpt-4o-mini",
            serpapi_api_key: str = None
            ):
        
        super().__init__(
            Funcs = Funcs,
            hepai_api_key = hepai_api_key,
            base_url = base_url,
            llm_model_name = llm_model_name)
        
        assert serpapi_api_key is not None, "Please provide a valid API key for SerpAPI"
        self.serpapi_api_key = serpapi_api_key
    
    def interface(
            self,
            messages: list[dict[str, str]], 
            **kwargs: Any) -> Union[str, Dict, Generator]:
        return self.function_interface(
            messages, 
            serpapi_api_key=self.serpapi_api_key)


