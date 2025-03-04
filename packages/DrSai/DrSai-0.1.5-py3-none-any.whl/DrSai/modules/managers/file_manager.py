
import os, sys, requests
from pathlib import Path
here = Path(__file__).parent

try:
    from DrSai.version import __version__
except:
    sys.path.insert(1, f'{here.parent.parent.parent}')
    from DrSai.version import __version__

from fastapi import UploadFile
# import json
# import uuid
import hashlib
import time
# import PyPDF2

# from pydantic import BaseModel
# import openai
# from openai import OpenAI
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse, JSONResponse, PlainTextResponse
from DrSai.configs import CONST
from DrSai.utils import BaseJsonSaver, Logger
from DrSai.modules.managers.base_file import File, FileClient, FileContent
from DrSai.apis.components_api import pdf_parser_by_haiNougat

from DrSai.version import __appname__

logger = Logger.get_logger("files_manager.py")

class FilesManager(BaseJsonSaver):
    version = "1.0.0"
    metadata = metadata = {
        "version": version,
        "discription": "This is a file index for hepai file system",
        "mapping_username2indexes": {},  # 用来存储用户名到线程索引的映射，方便快速查找
    }
    def __init__(self,
        file_name: str = f'index.json',
        file_dir: str = f'{Path.home()}/.{__appname__}/files',
        pdf_parser_func: callable = pdf_parser_by_haiNougat,
        **kwargs
        ) -> None:
        super().__init__(auto_save=False, **kwargs)

        self.file_path = os.path.join(file_dir, file_name)
        self._file_path = file_dir
        #file_index = self._init_file_index(file_dir)
        self._data = self._init_load(self.file_path, version=self.version, metadata=self.metadata)  
        
        self.pdf_parser_func = pdf_parser_func

    @property
    def sha256s(self):
        return [entity['sha256'] for entity in self._data['entities']]
    
    @property
    def bytes_sizes(self):
        file_index = self._data
        return [entity['bytes'] for entity in file_index['entities']]
        
    def write_file(self, file_name, content):
        file_path = f'{self._file_path}/{file_name}'
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        with open(file_path, 'wb') as f:
            f.write(content)
        print(f"File saved to {file_path}")
        return Path(file_path)
    
    def output_client(self, files, output_keys_list):
        file_index_client = {key: getattr(files, key) for key in output_keys_list}
        return file_index_client  #从output_keys_list中取出
        #return f'data: {json.dumps(output_to_client)}\n\n'
    
    def get_id_and_file(self, bytes_size, sha256):
        """
        根据文件尺寸和哈希值判断是否重复，如果重复则重新生成，否则返回
        """
        if bytes_size not in self.bytes_sizes:
            return self.auto_id(), None
        if sha256 not in self.sha256s:
            return self.auto_id(), None
        sha256_index = self.sha256s.index(sha256)
        file_json = self._data['entities'][sha256_index]
        return file_json['id'], file_json
    
    def create_file(self, content, file: UploadFile, purpose: str, username: str=None):
        """在服务端创建文件系统"""
        filename = file.filename
        bytes_size = file.size
        sha256 = hashlib.sha256(content).hexdigest()
        id, files = self.get_id_and_file(bytes_size, sha256)
        if files:
            files = File(**files)
        else:
            status = 'uploaded'
            _file_path = f'{username}/{filename}' 
            file_path: Path = self.write_file(file_name=_file_path, content=content)  # 保存文件到本地
            try:
                if file.content_type in ['application/pdf']:
                    file_content = self.pdf_parser_func(
                        path=str(file_path.absolute()), 
                        api_key=CONST.ADMIN_API_KEY,
                        username=username)
                    _content_file_path = f'{username}/{Path(filename).stem}.txt'
                    self.write_file(_content_file_path, file_content.encode('utf-8'))               
                else:
                    file_content = content.decode('utf-8')
                    _content_file_path = f'{username}/{Path(filename).stem}.txt'
                    self.write_file(_content_file_path, file_content.encode('utf-8'))
            except:
                raise NotImplementedError("暂不支持该文件类型")
            
            files = File(id=id,
                object="file",
                created_at = int(time.time()),
                filename=filename,
                purpose=purpose,
                uploader=username,
                bytes=bytes_size,
                file_path=_file_path,
                sha256=sha256,
                status=status,
                file_type=file.content_type,
                content_file_name=_content_file_path,
                username=username)             
            self.append_entity(files, username=username, save_immediately=True)
        return files
    
    def create_file_client(self, content, file: UploadFile, purpose: str, username: str):
        username = username or self.DEFAULT_USERNAME
        file: File = self.create_file(content, file, purpose, username)
        output_keys_list = ["id", "object", "created_at", "filename", "purpose", "bytes", "status", "status_details"]
        file: FileClient = self.output_client(file, output_keys_list)  
        return file
    
    def get_file(self, file_id, username=None, return_index=False):
        if username:
            files_indexes = self.data["metadata"]["mapping_username2indexes"].get(username, [])
            if not files_indexes:
                raise ModuleNotFoundError(f"No file found for user `{username}`")
        else:
            files_indexes = list(range(len(self.entities)))
            if not files_indexes:
                raise ModuleNotFoundError(f"No file found")
        filtered = [(self.entities[idx], idx) for idx in files_indexes if self.entities[idx]['id'] == file_id]
        if not filtered:
            raise ModuleNotFoundError(f"No file found for user `{username}` and id `{file_id}`")
        files, indexes = zip(*filtered)
        if not files:
            raise ModuleNotFoundError(f"File not found, id: `{file_id}`")
        if len(files) > 1:
            raise ValueError(f"Multiple files found, id: `{file_id}`")
        file = File(**files[0])
        #output_keys = ["id", "object", "created_at", "name", "usage_bytes", "file_counts"]
        #vect = {key: vects[0].get(key) for key in output_keys}
        #vect = {key: getattr(vect, key) for key in output_keys if hasattr(vect, key)}
        #vect = VectorStoreOutput(**vect)      
        if file.deleted:
            raise ModuleNotFoundError(f"File has been deleted, id: `{file_id}`")
        if return_index:
            assert len(indexes) == 1, f"Multiple files found, id: `{file_id}`"
            return file, indexes[0]
        return file
    
    #定义返回到客户端的文件信息
    def get_file_cliet(self, file_id, username=None, **kwargs):
        file = self.get_file(file_id, username=username, **kwargs)
        output_keys_list = ["id", "object", "bytes", "created_at", "filename", "purpose"]
        file = self.output_client(file, output_keys_list)
        return file
        
    def get_file_content(self, file_id):
        if file_id not in self.ids:
            raise FileNotFoundError(f"File not found: {file_id}")
        #file_info = self._data['entities'][self.ids.index(file_id)]
        file_info = next((x for x in self.entities if x.get('id') == file_id), None)
        content_file_path = f'{self._file_path}/{file_info["content_file_name"]}'
        with open(content_file_path, 'r') as f:
            content = f.read()
        content = {
            'content': content,
            'filetype': file_info['file_type'],
            'filename': file_info['filename'],
            'id': file_id,
        }
        #content = FileContent(**content)
        #content = f'data: {json.dumps(content)}\n\n'
        return content
    
    def delete(self, file_id):
        """
        删除文件及其索引
        """
        if file_id not in self.ids:
            raise FileNotFoundError(f"File not found: {file_id}")
        entities = self._data.get("entities", [])
        file_info = [entitie for entitie in entities if entitie["id"] == file_id][0]
        
        # 删除文件和内容文件
        file_path = f'{self._file_path}/{file_info["file_path"]}'
        content_file_path = f'{self._file_path}/{file_info["content_file_name"]}'
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(content_file_path):
            os.remove(content_file_path)
        
        # 更新用户索引
        username = file_info['uploader']
        self.metadata['mapping_username2indexes'][username].remove(file_id)
        if not self.metadata['mapping_username2indexes'][username]:
            del self.metadata['mapping_username2indexes'][username]
        
        self.save_index()
        return {"status": "File deleted successfully"}
    
    def list_files(self, username):
        """
        列出某个用户上传的所有文件
        """
        if username not in self._data["metadata"]['mapping_username2indexes']:
            return []
        file_ids = self._data["metadata"]['mapping_username2indexes'][username]
        file_ids = [self.ids[file_id] for file_id in file_ids]
        entities = self._data.get("entities", [])
        files_info = [entitie for entitie in entities if entitie["id"] in file_ids]
        return JSONResponse({"data":files_info, "object": "list"})

                    
    
            
                 






