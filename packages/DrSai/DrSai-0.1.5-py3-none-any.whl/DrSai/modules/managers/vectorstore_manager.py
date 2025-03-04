from typing import List, Dict
import os, sys, json, requests
from pathlib import Path
from dataclasses import dataclass, field
here = Path(__file__).parent
import uuid
import time


try:
    from DrSai.version import __version__
except:
    sys.path.insert(1, f'{here.parent.parent.parent}')
    from DrSai.version import __version__
from DrSai.utils import BaseJsonSaver, Logger
from DrSai.configs import CONST, BaseArgs
from DrSai.version import __appname__
import hepai as hai
from DrSai.modules.managers.base_vectorstore import VectorStore, Tool, VectorstoreDeleted, VectorStoreList, VectorStoreClient
from DrSai.modules.components.memory.hai_rag import hairag
from hepai import HRModel, LRModel
logger = Logger.get_logger("vector_store_manager.py")

class VectorstoresManager(BaseJsonSaver):
    version = "1.0.0"
    metadata = {
        "description": "Vector_stores of all users",
        "mapping_username2indexes": {},  # 用来存储用户名到线程索引的映射，方便快速查找
        "mapping_vsid2collection": {},  # 用来存储vsid到collection的映射，方便快速查找
    }
    
    def __init__(self,
        file_name: str = f'vector_store.json',
        file_dir: str = f'{Path.home()}/.{__appname__}',
        **kwargs
        ) -> None:
        super().__init__(auto_save=False, **kwargs)
        self.file_path = os.path.join(file_dir, file_name)
        self._data = self._init_load(self.file_path, version=self.version, metadata=self.metadata)

    def output_client(self, vects, **kwargs):
        output_keys_list = ["id", "object", "created_at", "name", "usage_bytes", 
                            "file_counts", "last_active_at", "metadata", "status", 
                            "expires_after", "expires_at"]
        output_to_client = {key: getattr(vects, key) for key in output_keys_list}  #从output_keys_list中取出
        return output_to_client
        #return f'data: {json.dumps(output_to_client)}\n\n'

    def hai_rag(self, data, stream=False):
        base_url = "http://localhost:44000/apiv2"
        api_key = CONST.ADMIN_API_KEY
        RAGmodel = HRModel.connect(
            name = 'hepai/hep-rag-OS',
            base_url = base_url, 
            api_key = api_key)
        return RAGmodel.interface(**data)
    
    
    #获取所有collection
    def get_all_collections(self, username, collection_name):
        username = username or self.DEFAULT_USERNAME
        data = {
            "username": f"{username}",
            "method": "get_collections",
            "collection": f"{collection_name}"
            }
        collections = self.hai_rag(data)
        return collections

    #创建collection，collection_name默认为DrSai-username，保证collection唯一性
    def create_collection(self, username, collection_name=None):
        username = username or self.DEFAULT_USERNAME
        collection_name = collection_name or f"DrSai-{username}"
        #获取所有collection
        collections = self.get_all_collections(username, collection_name)
        #判断collection是否存在
        if collection_name in collections:
            return collection_name
        else:
            #创建collection
            data = {
                "username": f"{username}",
                "collection": f"{collection_name}",
                "method": "create_collection",
                }
            self.hai_rag(data)
            return collection_name

    #删除collection
    def delete_collection(self, username, collection_name=None):
        # 3. 删除collection
        username = username or self.DEFAULT_USERNAME
        collection_name = collection_name or f"DrSai-{username}"
        data = {
            "username": f"{username}",
            "collection": f"{collection_name}",
            "method": "delete_collection",
            }
        self.hai_rag(data)
        return print(f"collection {collection_name} has been deleted")

    def create_vector_store(self, 
                            file_ids=None, 
                            username=None, 
                            **kwargs)-> VectorStore:
        username = username or self.DEFAULT_USERNAME
        collection_name = kwargs.get('name', None) or f"DrSai-{username}"
        collection_name = self.create_collection(username, collection_name=collection_name)
        if collection_name in self._data["metadata"]["mapping_vsid2collection"]:
            id = self._data["metadata"]["mapping_vsid2collection"][collection_name]
            order_id = [entitie for entitie in self.entities if entitie['id'] == id][0]['order_id']
        else:
            id = self.auto_id(prefix='vect_', length=30)
            order_ids = [x['order_id'] for x in self.entities]
            order_id = f'{int(max(order_ids))+1:0>6}' if order_ids else '000001'
            self._data["metadata"]["mapping_vsid2collection"][collection_name] = id
        #order_id = '000001'
        vects = VectorStore(id=id,
            object="vector_store", 
            created_at=int(time.time()),
            name=kwargs.get('name', None),
            usage_bytes=0, #初始 bytes 大小设为0，后续可以根据具体情况更新
            status="completed",
            collection=collection_name,
            expires_after=kwargs.get('expires_after', None),
            file_counts={
                "in_progress": 0,
                "completed": 0 if not file_ids else len(file_ids),
                "failed": 0,
                "cancelled": 0,
                "total": 0 if not file_ids else len(file_ids),
            },
            metadata=kwargs.get('metadata', {}),
            username=username,
            expires_at=kwargs.get('expires_at', None),
            last_active_at=kwargs.get('last_active_at', None),
            deleted=False,
            order_id=order_id)
        if collection_name not in self._data["metadata"]["mapping_vsid2collection"]:
            self.append_entity(entity=vects, username=username, save_immediately=True)
        return vects
    
    #定义返回到客户端的向量库创建信息
    def create_vector_store_client(self, file_ids=None, username=None, **kwargs):
        """ 
        返回值：
        json
        {
            "id": "vs_abc123",
            "object": "vector_store",
            "created_at": 1699061776,
            "name": "Support FAQ",
            "bytes": 139920,
            "file_counts": {
                "in_progress": 0,
                "completed": 3,
                "failed": 0,
                "cancelled": 0,
                "total": 3
            },
            "metadata": {}
        }
        """
        username = username or self.DEFAULT_USERNAME
        vect: VectorStore = self.create_vector_store(file_ids=file_ids, username=username, **kwargs)
        vect: VectorStoreClient = self.output_client(vect)  
        return vect
                   
    #定义包含全部向量库信息的列表
    def list_vector_stores(self, username, limit=20, order='desc', after=None, before=None, **kwargs):
        """
        list of vecotor_stores for assistant
        {
            "object": "list",
            "data": [
                {
                "id": "file-abc123",
                "object": "vector_store.file",
                "created_at": 1699061776,
                "vector_store_id": "vs_abc123"
                },
                {
                "id": "file-abc456",
                "object": "vector_store.file",
                "created_at": 1699061776,
                "vector_store_id": "vs_abc123"
                }
            ],
            "first_id": "file-abc123",
            "last_id": "file-abc456",
            "has_more": false
            }
        """
        if after:
            raise NotImplementedError(f"after not implemented yet in version {__version__} ")
        if before:
            raise NotImplementedError(f"before not implemented yet in version {__version__} ")
        
        vects_indexes = self.data["metadata"]["mapping_username2indexes"].get(username, [])
        #vect = [int(x) for x in vect_indexes]
        vects = [self.entities[idx] for idx in vects_indexes]
        # output_keys = ["id", "object", "created_at", "name", "usage_bytes", "file_counts"]
        # vects  = [{key: item.get(key) for key in output_keys} for item in vects]
        #vects = {key: getattr(vects, key) for key in vects}
        #vects = [VectorStoreOutput(**x) for x in vects]
        vects = [VectorStore(**x) for x in vects]
        #vects = [x for x in vects if not x.deleted]
        reverse = True if order == 'desc' else False
        vects = sorted(vects, key=lambda x: x.created_at, reverse=reverse)
        vects_list = []
        for item in vects:
            output_keys_list = ["id", "object", "created_at", "name", "usage_bytes", "file_counts"]
            output_to_client = {key: getattr(item, key) for key in output_keys_list}
            # output_to_client = json.dumps(output_to_client)
            vects_list.append(output_to_client)
            del output_to_client, output_keys_list
        vects = vects_list
        del vects_list
        vects = [VectorStoreClient(**x) for x in vects]
        has_more = len(vects) > limit
        if has_more:
            vects = vects[:limit]
        if len(vects) == 0:
            return {
            "object": "list",
            "data": vects,
            "first_id": None,
            "last_id": None,
            "has_more": has_more,
        }      
        return {
            "object": "list",
            "data": vects,
            "first_id": vects[0].id,
            "last_id": vects[-1].id,
            "has_more": has_more,
        }

    #定义检索返回到客户端的向量库信息 
    def retrieve_vector_store(self, username=None, vector_store_id=None, **kwargs):
        return self.get_vector_store_client(vector_store_id, username=username, **kwargs)
    
    #定义修改向量库信息的客户端接口
    def modify_vector_store(self, vector_store_id, username=None, **kwargs):
        return self.update_vector_store_client(vector_store_id, username=username, **kwargs)
    
    #获取全部向量库信息
    def get_vector_store(self, vector_store_id, username=None, return_index=False):
        """获取助手"""
        if username:
            vects_indexes = self.data["metadata"]["mapping_username2indexes"].get(username, [])
            if not vects_indexes:
                raise ModuleNotFoundError(f"No vector store found for user `{username}`")
        else:
            vects_indexes = list(range(len(self.entities)))
            if not vects_indexes:
                raise ModuleNotFoundError(f"No vector store found")
        filtered = [(self.entities[idx], idx) for idx in vects_indexes if self.entities[idx]['id'] == vector_store_id]
        if not filtered:
            raise ModuleNotFoundError(f"No vector store found for user `{username}` and id `{vector_store_id}`")
        vects, indexes = zip(*filtered)
        if not vects:
            raise ModuleNotFoundError(f"Vector store not found, id: `{vector_store_id}`")
        if len(vects) > 1:
            raise ValueError(f"Multiple vector store found, id: `{vector_store_id}`")
        vect = VectorStore(**vects[0])
        #output_keys = ["id", "object", "created_at", "name", "usage_bytes", "file_counts"]
        #vect = {key: vects[0].get(key) for key in output_keys}
        #vect = {key: getattr(vect, key) for key in output_keys if hasattr(vect, key)}
        #vect = VectorStoreOutput(**vect)      
        if vect.deleted:
            raise ModuleNotFoundError(f"Vector store has been deleted, id: `{vector_store_id}`")
        if return_index:
            assert len(indexes) == 1, f"Multiple vector store found, id: `{vector_store_id}`"
            return vect, indexes[0]
        return vect
    
    #定义返回到客户端的向量库信息
    def get_vector_store_client(self, vector_store_id, username=None, **kwargs):
        vects = self.get_vector_store(vector_store_id, username=username, **kwargs)
        vects = self.output_client(vects)
        return vects
    
    #定义更新向量库信息的接口
    def update_vector_store(self, vector_store_id, username=None, **kwargs):
        """更新向量库信息"""
        save_immediately = kwargs.pop('save_immediately', False)
        vect, idx = self.get_vector_store(vector_store_id=vector_store_id, username=username, return_index=True)
        vect.update(**kwargs)  # 更新类属性
        # 更新到数据库
        self.update_entity(entity=vect, index=idx, save_immediately=save_immediately)
        return vect
    
    #定义更新向量库信息的客户端接口
    def update_vector_store_client(self, vector_store_id, username=None, **kwargs):
        vects = self.update_vector_store(vector_store_id, username=username, **kwargs)
        vects = self.output_client(vects)
        return vects
    
    #删除向量库
    def delete_vector_stores(self, vector_store_id, username=None, **kwargs):
        """删除向量库"""
        save_immediately = kwargs.pop('save_immediately', False)
        perminate = kwargs.pop('perminate', False) # 永久删除
        perminate = True if perminate=='True' else perminate
        if not perminate:
            vect = self.update_vector_store(
                vector_store_id=vector_store_id, username=username, deleted=True,
                save_immediately=save_immediately
                )
            assert vect.deleted, "Assistant not deleted"
        else:
            vect, idx = self.get_vector_store(vector_store_id, username=username, return_index=True)
            self.remove_entity(vect, idx, save_immediately=save_immediately)

        return VectorstoreDeleted(
            id=vect.id,
            object="vector_store.deleted",
            deleted=True,
        )

    
        


        


     




    



