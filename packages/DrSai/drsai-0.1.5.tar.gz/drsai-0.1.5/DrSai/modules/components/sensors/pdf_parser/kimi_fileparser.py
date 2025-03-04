import os, json
from hepai import HepAI
from pathlib import Path

class FileParser:
    """
    基于kimi的文档解析器，用来解析文档的内容，包括文本内容，图片内容，音频内容等。
    """
    def __init__(self, api_key: str) -> None:
        self.client = HepAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1",
            )
        pass

    def create(self, file: Path, purpose: str):
        file_object = self.client.files.create(file=file, purpose=purpose)
        file_json = file_object.__dict__
        file_json['created_by'] = str(self.client.base_url)
        return file_json
    
    def retrieve(self, file_id):
        file_content = self.client.files.content(file_id=file_id).text
        file_content = json.loads(file_content)
        file_content = file_content['content']
        return 

def pdf_parser_by_kimi(
    path: str = None, 
    api_key: str = None): # 
    assert os.path.exists(path), "PDF路径不存在.请提供有效的PDF路径。"
    assert api_key, "Cannot get HEPAI_API_KEY. Please provide it in the api_key parameter or set it in the environment variables."
    file_parser = FileParser(api_key=api_key)
    file_path = Path(path)
    file_json = file_parser.create(file=file_path, purpose="file-extract")
    file_content = file_parser.retrieve(file_id=file_json['id'])

    return file_content

# if __name__ == '__main__':
#     api_key = os.getenv("MOONSHOT_API_KEY")
#     path = "your_pdf_path/2501_01370.pdf"
#     pdf_parser_by_kimi(path=path, api_key=api_key)