from typing import List, Optional, Dict, Literal, Generator, Union
from hepai.types import ChatCompletionChunk as ChatCompletionChunk2
from openai.types.chat import ChatCompletionChunk
import json
import time
import re

# 标准openai chat/completions stream模式
chatcompletionchunk = {
                "id":"chatcmpl-123",
                "object":"chat.completion.chunk",
                "created":1694268190,
                "model":"DrSai", 
                "system_fingerprint": "fp_44709d6fcb", 
                "usage": None,
                "choices":[{"index":0,
                            "delta":{"content":"", "function_call": None, "role": None, "tool_calls": None},
                            "logprobs":None,
                            "finish_reason":None}] # 非None或者stop字段会触发前端askuser
                } 
chatcompletionchunkend = {
    "id":"chatcmpl-123",
    "object":"chat.completion.chunk",
    "created":1694268190,
    "model":"DrSai", 
    "system_fingerprint": "fp_44709d6fcb", 
    "choices":[{'delta': {'content': None, 'function_call': None, 'refusal': None, 'role': None, 'tool_calls': None}, 'finish_reason': 'stop', 'index': 0, 'logprobs': None}]
    }


def get_full_response_from_oai_stream(stream: Generator) -> Union[str, Generator]:
    full_response = ""
    for i, x in enumerate(stream):
        assert isinstance(x, ChatCompletionChunk), "The stream should be a generator of ChatCompletionChunk"
        content = x.choices[0].delta.content
        if content:
            full_response += content
        yield f"data: {json.dumps(x)}\n\n"
    return full_response

def convert_str_to_oai_stream(text: str, chunk_size: int=10, sleep_time: float=0.02) -> Generator:
        '''
        Convert a string to a stream of ChatCompletionChunk.
        chunk_size: the maximum length of each chunk.
        '''     
        Tester_OUTPUT = text.split("[**Tester OUTPUT**]") # 兼容tester的流式输出
        if len(Tester_OUTPUT) == 4: # 通过[**Tester OUTPUT**]确定是tester的输出，并进行分割
            chunks = [Tester_OUTPUT[0]+Tester_OUTPUT[1]+Tester_OUTPUT[2]+Tester_OUTPUT[3]]
        else:
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        # print(f"chunks: {chunks}")
        for i, chunk in enumerate(chunks):
            # 提取pic_url和pdf_url-这里为了兼容Tseter的输出，将图片和pdf文件路径提取出来
            pic_urls = []
            pic_pattern = r'<pic: (.*?) >'
            matches = re.findall(pic_pattern, chunk)
            if matches:
                for match in matches:
                    if match!="None":
                        pic_urls.append(match)
            pdf_urls = []
            pdf_pattern = r'<pdf: (.*?) >'
            matches = re.findall(pdf_pattern, chunk)
            if matches:
                for match in matches:
                    if match!="None":    
                        pdf_urls.append(match)

            time.sleep(sleep_time)
            data = chatcompletionchunk.copy()
            data['choices'][0]['delta']['content'] = chunk
            if pic_urls or pdf_urls: # 兼容Tseter的输出
                data['choices'][0]['delta']['pic_urls'] = pic_urls
                data['choices'][0]['delta']['pdf_urls'] = pdf_urls
            yield f'data: {json.dumps(data)}\n\n'
        
        # 最后一个chunk
        yield f'data: {json.dumps(chatcompletionchunkend)}\n\n'

def convert_Generator_to_oai_stream(stream: Generator):
        
        """
        Support for Dicts in the stream, in addition to pure str.
        目前支持yeild的类型为str或ChatCompletionChunk。 后续添加
        """
        full_response = ""
        for i, x in enumerate(stream):
            # assert isinstance(x, ChatCompletionChunk), "The stream should be a generator of ChatCompletionChunk"
            if isinstance(x, str):
                if "![Image](data:image;base64," in x:
                    print("TODO: base_oai_manager.py: Image will not be added to messages.")
                full_response += x
                data = chatcompletionchunk.copy()
                data['choices'][0]['delta']['content'] = x
                yield f"data: {json.dumps(data)}\n\n"
            elif isinstance(x, ChatCompletionChunk) or isinstance(x, ChatCompletionChunk2):
                content = x.choices[0].delta.content
                if content:
                    full_response += content
                yield f"data: {json.dumps(x.model_dump())}\n\n"
            else:
                raise ValueError(f"The stream should be a generator of str or ChatCompletionChunk but got a {str(type(x))}.")
        try:
            # 最后一个x是字符串yeild结束，此时需要发送一个结束的chunk
            if isinstance(x, str):
                yield f"data: {json.dumps(chatcompletionchunkend)}\n\n"
        except Exception as e:
            data = chatcompletionchunk.copy()
            data['choices'][0]['delta']['content'] = f"Error: {e}"
            yield f"data: {json.dumps(data)}\n\n"
            yield f"data: {json.dumps(chatcompletionchunkend)}\n\n"
            
        return full_response