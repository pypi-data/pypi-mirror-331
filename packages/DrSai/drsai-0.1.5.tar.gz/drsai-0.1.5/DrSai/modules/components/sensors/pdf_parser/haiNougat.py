import os
import base64
import requests
from typing import Dict
from DrSai.apis.utils_api import Logger
logger = Logger.get_logger(__name__)

def pdf_pre_process(data: Dict):
    pdf_path = data.pop('pdf_path', None)
    pdf_path = os.path.abspath(pdf_path)
    if not os.path.exists(pdf_path):
        raise ValueError("PDF路径为空.请使用pdf_path参数来提供有效的PDF路径。")
    else:
        with open(pdf_path, 'rb') as pdf_file:
            pdfbin = pdf_file.read()          
        pdfbin= base64.b64encode(pdfbin).decode()
    
    data['pdfbin'] = pdfbin

    return data

def pdf_parser_by_haiNougat(
    path: str = None, 
    api_key: str = None,
    stream: bool = True,
    **kwargs):
    assert os.path.exists(path), "PDF路径不存在.请提供有效的PDF路径。"
    assert api_key, "Cannot get HEPAI_API_KEY. Please provide it in the api_key parameter or set it in the environment variables."

    request_headers = {"Authorization": f"Bearer {api_key}"}
    request_data = {
        "model": r'hepai/hainougat',
        "timeout": 300,
        "stream": stream, #False处理完PDF输出，超时报错。设置True
        "pdf_path": path,
        "url": "https://aiapi.ihep.ac.cn",
    }
    request_data = pdf_pre_process(data = request_data)
    url = "https://aiapi.ihep.ac.cn/v1/inference"
    timeout = 300

    session = requests.Session() 
    response = session.post(
        f'{url}',
        headers=request_headers,
        json=request_data,
        timeout=timeout,
        stream=stream
    )
    if response.status_code != 200:
        raise Exception(f"Got status code {response.status_code} from server: {response.text}")
        # print(response.content)  # 只有非流式相应才能查看内容
    try:
        data: Dict = response.json()
        status_code = data.pop('status_code', 42901)
        if status_code != 42901:
            error_info = f'Request error: {data}'
            logger.error(error_info)
            raise Exception(error_info)
    except:
        pass
    
    if not stream:            
        data = response.json()
        data = data['message']
    else: 
        #data = response.content.decode('utf-8', errors='ignore')
        data = response.content.decode('utf-16-le', errors='ignore')
        data = data.replace('[DONE]', "")
    return data

if __name__ == '__main__':
    api_key = os.getenv("HEPAI_API_KEY2")
    path = "your_pdf_path/2501_01370.pdf"
    pdf_parser_by_haiNougat(path=path, api_key=api_key)