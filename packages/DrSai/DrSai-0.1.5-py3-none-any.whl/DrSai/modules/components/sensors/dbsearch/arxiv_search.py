
# 该例子通过大语言模型进行函数关键词提取，并使用arxiv检索文献
import time
from typing import Any, Literal, Annotated, List, Dict, Union, Generator, Tuple, Any, Optional, Callable
import arxiv
import os 
from DrSai.configs import CONST
from DrSai.apis.utils_api import str_utils
from DrSai.apis.components_api import pdf_parser_by_haiNougat
from DrSai.apis.utils_api import Tools_call

## 文章检索结果输出格式化定义及其他工具
def article_output_formatting(title="", url="", authors=None, published_date="", abstract="", **kwargs) -> str:
    ## add hyperlink and convert to markdown format
    article_info = {}
    article_info["Title"] = f"[{title}]({url})" if url and url != "Unknown" else title
    
    formatted_authors = ""
    if authors:
        formatted_authors = ', '.join(authors[:3]) + ' *et al.*' if len(authors) > 3 else ', '.join(authors)
    article_info["Authors"] = formatted_authors

    article_info["Published date"] = published_date
    
    # abstract_split = abstract.split()
    # if len(abstract_split) > 50:
    #     # abstract_short = " ".join(abstract_split[:10]) + "..."
    #     # article_info["Abstract"] = f"<details>\n<summary>{abstract_short}</summary>\n{abstract}\n</details>"
    #     article_info["Abstract"] = " ".join(abstract_split[:50]) + "..."
    # else:
    #     article_info["Abstract"] = abstract
    article_info["Abstract"] = abstract # 假如作为参考意见给Host，则直接提供完整内容
    

    ## 假如需要全文，重新组织输出信息
    if kwargs.get("full_text", None):
        article_info.clear()
        article_info["Title"] = title
        article_info["Full text"] = kwargs["full_text"]
    
    output = ""
    for key, value in article_info.items():
        output += f"**{key}:** {value}\n"
    return output

## 文章检索结果输出格式化定义及其他工具
def articleInfos_to_string(source: str, article_infos: Dict[str, str], url: str = "") -> str:
    output = ""
    if not article_infos:
        output = f'''Oops, no article found in {source}. Please check your query url:\n```\n{url}\n```'''
    else:
        if len(article_infos) > 1:
            for key, value in article_infos.items():
                output += f"**Result {key+1}:**\n{value}\n\n"
        else:
            output = article_infos[0]
        
        output = "Here are the articles found in " + source + ":\n\n" + output
    
    output = str_utils.mathml2latex(output)
    return output

## 构建arxiv检索字段
def query_formatting(query: str) -> str:
    tokens = query.split()
    result = []
    current_group = []

    for i, token in enumerate(tokens):
        if token in {'AND', 'OR', 'NOT'}:
            if current_group:
                result.append('(' + ' AND '.join(current_group) + ')' if len(current_group) > 1 else current_group[0])
                current_group = []  # 重置当前组

            result.append(token)  # 添加逻辑符号

        else:
            current_group.append(token)

    if current_group:
        result.append('(' + ' AND '.join(current_group) + ')')

    return ' '.join(result)

## 检索提示词
query_prompt = """
Return a effective search string using non-metadata keywords. Please think step by step to generate the search string because this is very important. Here are the steps:
1. **Keyword Extraction**:
    - Extract only keywords that pertain to the article's main content, such as the title, main body, author names, or abstract. Please refrain from including metadata like publication date and source.
2. **English Translation**:
    - Translate keywords to English if they aren't already.
3. **Logical Operator Explanation**:
    - Use logical operators to connect the keywords, where:
        - **AND**: All keywords must appear simultaneously.
        - **OR**: At least one keyword must meet the condition.
        - **NOT**: Certain keywords should not appear in the search results.
    - The combinations of keywords can be nested.
4. **Special Handling**:
    - If there are names of high-energy physics particles (e.g., Zc3900), generate 3-5 spelling variants in LaTeX format as needed, connecting them with "OR" to improve retrieval accuracy. For example, to search for Zc3900, use: (Zc3900 OR 3900 OR Z_c(3900) OR Z*(3900) OR Z_{c}*).

### Sample Requests and Outputs

- **Example 1**:
- **Request**: Find 4 articles about COVID-19, vaccination, or public health policies, avoiding the field of mental health.
- **Output**: "(COVID AND 19) OR vaccination OR (public AND health AND policies) NOT (mental AND health)"

- **Example 2**:
- **Request**: Find articles about the discovery of a new elementary particle, such as the discovery of a new particle called "psi(3770)."
- **Output**: "discovery AND (psi(3770) OR 3770 OR psi3770)"

Do not use "" in the query string. For example, 'AI AND Agent AND "High Energy Physics"' should be written as 'AI AND Agent AND High Energy Physics'.
"""


def arxiv_search(
    query: Annotated[str, query_prompt], # must be the first parameter, otherwise error. PS: if you wanna requried parameters, do not use default value!
    category: Annotated[Literal["astro-ph", "cond-mat", "gr-qc", "hep-ex", "hep-lat", "hep-ph", "hep-th", "math-ph", "nlin", "nucl-ex", "nucl-th", "physics", "quant-ph", "cs", "econ", "eess", "math", "q-bio", "q-fin", "stat"], "The article's category. "] = "",
    metadata: Annotated[Literal["ti", "au", "abs", "id", "co", "all"], f"The search scope. 'ti' for titles, 'au' for authors, 'abs' for abstracts, 'id' for arXiv identifiers, 'co' for comments, and 'all' to search across all categories by default."] = "all",
    index: Annotated[int, "The starting index of the initial article displayed in the search results list."] = 0,
    max_results: Annotated[int, "Specify the exact number of articles to retrieve based on user query. For example, if the user asks for '3 articles on topic X' or '找三篇关于3770的文章', set this value to 3."] = 3,
    is_content_needed: Annotated[bool, "Return True if the full text of the article is needed."] = False,
    # **kwargs: Annotated[Any, "Additional keywords to be passed to the function."], # so many similar search functions, the parameters may be confusing for LLM.
) -> str:
    """
    API: https://info.arxiv.org/help/api/user-manual.html
    """

    client = arxiv.Client()
    
    ## 构建query字符串
    query_pro = str_utils.add_prefix(query, metadata + ":") # arxiv use "ti:keywords"
    query_pro = query_formatting(query_pro) # 格式化query字符串
    query_pro = query_pro.replace("*", "").replace("{", "").replace("}", "") # arxiv API检索不支持通配符和花括号，单词的括号也会影响结果
    
    ## 检索
    search = arxiv.Search(
        query = query_pro,
        max_results = max_results, # seems bug here, always =100 in query url
        sort_by = arxiv.SortCriterion.SubmittedDate, # "Relevance", "LastUpdatedDate", "SubmittedDate" ### ???用SubmittedDate或LastUpdatedDate时复杂逻辑式直接什么也搜不到，例如all:Zc3900 OR all:3900 OR all:Z_c(3900) OR all:Z(3900) OR (all:Z_c) #NOTE 不是搜索不到，而是单词括号内外的内容会当做单独的东西去搜索。比如Z(3900)，他实际会按照Z OR 3900去搜，导致匹配大量无关文章
        sort_order = arxiv.SortOrder.Descending, # "Ascending" or "Descending"
        # id_list=[], # no need to use: search_by_id = arxiv.Search(id_list=["1605.08386v1"]),
    )

    ## 处理结果
    article_infos = {}
    for i, paper in enumerate(client.results(search)):          
        title = paper.title
        authors = [author.name for author in paper.authors]
        published_date = paper._raw.published[:10]
        #article_url = paper.entry_id
        article_url = paper.pdf_url
        abstract = paper.summary

        ## 下载与解析pdf
        params = {}
        if is_content_needed:
            paper.download_pdf(dirpath=f"{CONST.FILE_DIR}", filename=f"{article_url.split('/')[-1]}.pdf")
            #paper.download_source(dirpath=f"{CONST.FILE_DIR}", filename=f"{paper.id}.tar.gz") # 源代码
            pdf_content = pdf_parser_by_haiNougat(
                path=f"{CONST.FILE_DIR}/{article_url.split('/')[-1]}.pdf",
                api_key=CONST.ADMIN_API_KEY)
            params["full_text"] = pdf_content
        
        article_info = article_output_formatting(title=title, authors=authors, published_date=published_date, url=article_url, abstract=abstract, **params)
        article_infos[i] = article_info

    
    ## 输出结果
    output = articleInfos_to_string(source="arXiv", article_infos=article_infos, url=query_pro)

    time.sleep(3) # 延迟3秒，避免频繁访问服务器
    return output

class ArxivSearch(Tools_call):
    def __init__(
            self, 
            Funcs: list[callable] = [arxiv_search], 
            hepai_api_key: str = None,
            base_url: str = "https://aiapi.ihep.ac.cn/apiv2",
            llm_model_name: str = "openai/gpt-4o-mini",
            ):
        
        super().__init__(
            Funcs = Funcs,
            hepai_api_key = hepai_api_key,
            base_url = base_url,
            llm_model_name = llm_model_name)
    
    def interface(
            self,
            messages: list[dict[str, str]], 
            **kwargs: Any) -> Union[str, Dict, Generator]:
        return self.function_interface(
            messages, 
            **kwargs)

# if __name__ == '__main__':
#     hepai_api_key = os.environ.get("HEPAI_API_KEY2")
#     Arxiv_search = Tools_call(hepai_api_key = hepai_api_key)
#     messages = [{"role": "user", "content": "I want the latest articles about AI Agent in High Energy Physics. need full text."}]
#     Funcs = [arxiv_search]
#     output = Arxiv_search.interface(messages, Funcs=Funcs)
#     print(output)
    