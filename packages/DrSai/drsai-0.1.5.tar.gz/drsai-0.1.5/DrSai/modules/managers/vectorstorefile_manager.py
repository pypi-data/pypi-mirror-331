from typing import List, Dict
import os, sys, json
from pathlib import Path
from dataclasses import dataclass, field
here = Path(__file__).parent
import uuid
import time, re
import requests

try:
    from DrSai.version import __version__
except:
    sys.path.insert(1, f'{here.parent.parent.parent}')
    from DrSai.version import __version__
from DrSai.utils import BaseJsonSaver, Logger
from DrSai.configs import CONST, BaseArgs
from DrSai.version import __appname__
from DrSai.modules.managers.base_vectorstorefile import VectorStoreFile, VectorStoreFileClient,VectorStoreFileBatch     
from DrSai.modules.managers.file_manager import FilesManager
from DrSai.modules.managers.vectorstore_manager import VectorstoresManager
logger = Logger.get_logger("vector_store_manager.py")

class VectorstorefilesManager(BaseJsonSaver):
    version = "1.0.0"
    metadata = {
        "description": "Files attached to all the vector stores",
        "mapping_username2indexes": {},  # 用来存储用户名到线程索引的映射，方便快速查找
    }
    
    def __init__(self,
        file_name: str = f'vector_store.json',
        file_dir: str = f'{Path.home()}/.{__appname__}',
        **kwargs
        ) -> None:
        super().__init__(auto_save=False, **kwargs)

        self.file_path = os.path.join(file_dir, file_name)
        self._file_path = file_dir
        self._data = self._init_load(self.file_path, version=self.version, metadata=self.metadata)
        self.file_manager = FilesManager()
        self.vectorstore_manager = VectorstoresManager()

    def output_client(self, vectorstorefiles, output_keys_list):
        output_to_client = {key: getattr(vectorstorefiles, key) for key in output_keys_list}  #从output_keys_list中取出
        return output_to_client
        #return f'data: {json.dumps(output_to_client)}\n\n'


    def hai_rag(self, data, stream=False):
       return self.vectorstore_manager.hai_rag(data, stream=stream)

    def create_vectorstorefile(self, 
                               file_id=None, 
                               vector_store_id=None, 
                               username=None, 
                               collection_name=None,
                               **kwargs)-> VectorStoreFile:
        username = username or self.DEFAULT_USERNAME
        
        file_infor = self.file_manager.get_file(file_id=file_id, username=username)
        file_content = self.file_manager.get_file_content(file_id=file_id)
        file_content = file_content["content"]
        collection_name = collection_name or f"DrSai-{username}"
        doc = {"text": file_content, 'metadata': {"author": username, 
                                                  "file": file_infor.filename,
                                                  "vector_store_id": vector_store_id,
                                                  "file_id": file_id}
                                                  }
        data =  {
                "model": "hai-rag",
                "username": f"{username}",
                "collection": f"{collection_name}",
                "method": "insert",
                "doc": doc
                }
        rag_res = self.hai_rag(data, stream=False)
        doc_id = rag_res.get("doc_id")
        
        #doc_id = string.split(':')[-1].strip()
        #查重，如果有需要，在指定向量库中存多个文件，确保文件唯一性
        vectorstore = self.vectorstore_manager.get_vector_store(vector_store_id=vector_store_id, username=username)
        files_id = vectorstore.files_id or []
        docs_id = vectorstore.docs_id or []
        
        #entities = self._data.get("entities", {})
        # ids = list([x.get('docs_id', None) for x in self.entities])
        # assert doc_id not in ids, "doc_id must be unique"

        files_id.append(file_id)
        docs_id.append(doc_id)
            #更新docs_id和files_id
        vectorstore = self.vectorstore_manager.update_vector_store(
        vector_store_id=vector_store_id,
        username=username,
        files_id=files_id,
        docs_id=docs_id,
        collection=collection_name,
        save_immediately=True)
    
        vectorstorefile = VectorStoreFile(
                        id=file_id,
                        username=username,
                        object='vector_store.file',
                        created_at=int(time.time()),
                        usage_bytes=file_infor.bytes, #初始 bytes 大小设为0，后续可以根据具体情况更新
                        vector_store_id=vector_store_id,
                        status=file_infor.status,
                        last_active_at = int(time.time()),
                        last_error=None,
                        metadata=None,
                        deleted=False
                        )
        return vectorstorefile

    #     vectorstorefile = VectorStoreFile(id=file_infor.id,
    #         object="vector_store.file", 
    #         created_at=int(time.time()),
    #         usage_bytes=file_infor.bytes, #初始 bytes 大小设为0，后续可以根据具体情况更新
    #         status=file_infor.status,
    #         vector_store_id=vector_store_id,
    #         last_active_at = kwargs.get('last_active_at', None),
    #         metadata=kwargs.get('metadata', {}),  
    #         username=username,
    #         deleted=False)
    #    # vects = Vector_store.output_keys(vects)
    #     #self.append_entity(vectorstorefile, username=username, save_immediately=True)
    #     return vectorstorefile
    
    #定义返回到客户端的向量库创建信息
    def create_vectorstorefile_client(self, 
                                      file_id=None, 
                                      vector_store_id=None,
                                      collection_name=None,
                                      username=None, 
                                      **kwargs):
        username = username or self.DEFAULT_USERNAME
        if not collection_name:
            mapping_vsid2collection = self.vectorstore_manager._data["metadata"]["mapping_vsid2collection"]
            collection_name = [ x for x in mapping_vsid2collection if mapping_vsid2collection[x] == vector_store_id][0]
        vectorstorefile: VectorStoreFile = self.create_vectorstorefile(
                                                            file_id=file_id ,
                                                            vector_store_id=vector_store_id, 
                                                            username=username, 
                                                            collection_name=collection_name,
                                                            **kwargs)
        output_keys_list = ["id", "object", "created_at", "status", "last_error", 
                            "usage_bytes", "vector_store_id"]
        vectorstorefile: VectorStoreFileClient = self.output_client(vectorstorefile,
                                                                    output_keys_list)  
        return vectorstorefile
                   
    #定义包含全部向量库文件信息的列表
    def list_vector_store_files(self, username, vector_store_id, limit=20, order='desc', after=None, before=None, **kwargs):
        if after:
            raise NotImplementedError(f"after not implemented yet in version {__version__} ")
        if before:
            raise NotImplementedError(f"before not implemented yet in version {__version__} ")
        
        vectorstorefile_indexes = self.data["metadata"]["mapping_username2indexes"].get(username, [])
        #vect = [int(x) for x in vect_indexes]
        vector_store_files = [self.entities[idx] for idx in vectorstorefile_indexes]
        # output_keys = ["id", "object", "created_at", "name", "usage_bytes", "file_counts"]
        # vects  = [{key: item.get(key) for key in output_keys} for item in vects]
        #vects = {key: getattr(vects, key) for key in vects}
        #vects = [VectorStoreOutput(**x) for x in vects]
        #提取vector_store_files中vector_store_id=vector_store_id的vector_store_files的实体。
        vector_store_files = [file for file in vector_store_files if file.get("vector_store_id")==vector_store_id] 
        vector_store_files = [VectorStoreFile(**x) for x in vector_store_files]
        #vects = [x for x in vects if not x.deleted]
        reverse = True if order == 'desc' else False
        vector_store_files = sorted(vector_store_files, key=lambda x: x.created_at, reverse=reverse)
        vectorstorefiles_list = []
        for item in vector_store_files:
            output_keys_list = ["id", "object", "created_at", "name", "usage_bytes", "file_counts"]
            output_to_client = {key: getattr(item, key) for key in output_keys_list}
            # output_to_client = json.dumps(output_to_client)
            vectorstorefiles_list.append(output_to_client)
            del output_to_client, output_keys_list
        vector_store_files = vectorstorefiles_list
        del vectorstorefiles_list
        vector_store_files = [VectorStoreFileClient(**x) for x in vector_store_files]
        has_more = len(vector_store_files) > limit
        if has_more:
            vector_store_files = vector_store_files[:limit]
        if len(vector_store_files) == 0:
            return {
            "object": "list",
            "data": vector_store_files,
            "first_id": None,
            "last_id": None,
            "has_more": has_more,
        }      
        return {
            "object": "list",
            "data": vector_store_files,
            "first_id": vector_store_files[0].id,
            "last_id": vector_store_files[-1].id,
            "has_more": has_more,
        }

    #定义批量上传文件到向量库
    def bulk_upload_files_to_vector_store(self,          
                                        file_ids=None, 
                                        vector_store_id=None,
                                        collection_name=None,
                                        username=None, 
                                        **kwargs):
        username = username or self.DEFAULT_USERNAME
        id = self.auto_id(prefix='vsfb_', length=30)
        order_ids = [x['order_id'] for x in self.entities]
        order_id = f'{int(max(order_ids))+1:0>6}' if order_ids else 'vsfb_000001'
        del order_id
        for file_id in file_ids:
            VectorStoreFile = self.create_vectorstorefile(file_id=file_id,
                                        vector_store_id=vector_store_id,
                                        collection_name=collection_name,
                                        username=username,
                                        **kwargs)
        del VectorStoreFile
        vector_store_filebatch = VectorStoreFileBatch(id=id,
                                                    object="vector_store.file_batch",
                                                    created_at=int(time.time()),
                                                    vector_store_id=vector_store_id,
                                                    status="completed",
                                                    file_counts={
                                                                "in_progress": 0,
                                                                "completed": 0 if not file_ids else len(file_ids),
                                                                "failed": 0,
                                                                "cancelled": 0,
                                                                "total": 0 if not file_ids else len(file_ids),
                                                                },
                                                    )
        return vector_store_filebatch
                                                    


        
            
            






    



