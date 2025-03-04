
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel
import time


@dataclass
class BaseObject:

    @property
    def output_keys(self) -> List[str]:
        return NotImplementedError
    
    @property
    def allowed_update_keys(self) -> List[str]:
        return NotImplementedError

    def to_dict(self, only_output_keys=True):
        if only_output_keys:
            return {k: v for k, v in self.__dict__.items() if k in self.output_keys}
        return self.__dict__
    
    def update(self, auto_metadata=False, **new_info):
        """
        更新对象的信息
        :param auto_metadata: 是否自动更新metadata，自动更新"modified"和"modified_at"字段
        """
        for k, v in new_info.items():
            assert k in self.allowed_update_keys, f"Key `{k}` is not allowed to update"
            setattr(self, k, v)
        if auto_metadata:
            self.metadata["modified"] = True
            self.metadata["modified_at"] = int(time.time())
        return self
    
    def get(self, key, default=None):
        return getattr(self, key, default)

@dataclass
class Tool:
    type: str

@dataclass
class FileCounts(BaseModel):
    in_progress: int
    completed: int
    failed: int
    cancelled: int
    total: int

@dataclass
class ExpiresAfter(BaseModel):
    anchor: Optional[str]=None
    days: Optional[int]=None

class VectorStoreClient(BaseModel):
    id: str
    object: str
    created_at: int
    name: Optional[str]
    usage_bytes: int
    file_counts: Optional[FileCounts]

@dataclass
class VectorStore(BaseObject):
    id: str
    created_at: int
    name: str
    usage_bytes: int
    file_counts: FileCounts
    object: Literal["vector_store"]
    status: Literal["expired", "in_progress", "completed"]
    order_id: Optional[str]=None
    username: Optional[str]=None
    expires_after: Optional[ExpiresAfter]=None
    expires_at: Optional[int]=None
    last_active_at: Optional[int] = None
    metadata: Dict[str, Any] = None,
    deleted: Optional[bool] = False
    collection: Optional[str] = None
    docs_id: Optional[List[str]] = None
    files_id: Optional[List[str]] = None

    
    @property
    def output_keys(self):
        """定义了网络请求时需要返回的字段"""
        return ["id", "object", "created_at", "name", "usage_bytes", "doc_id", "file_counts",
                "order_id", "username", "status", "expires_after", "expires_at", "last_active_at", 
                "metadata", "deleted", "collection", "docs_id", "files_id"]
    
    # @property
    # def output_to_client(self):
    #     output_keys_list = ["id", "object", "create_at", "name", "usage_bytes", "file_counts"]
    #     return  {key: getattr(self, key, None) for key in output_keys_list}
    # #返回output_keys中指定字段和相应的值'
    # def get_output_fields(self):
    #     output_keys = {key: getattr(self, key) for key in self.output_keys}
    #     return output_keys
    # # def get(self, key, default=None):
    #     return super().get(key, default) 
    @property
    def allowed_update_keys(self):
        return ["name", "usage_bytes", "file_counts", "status", "last_active_at", 
                "metadata", "deleted", "docs_id", "files_id", "collection", "expires_after", "expires_at"]

@dataclass
class VectorStoreFileBatch(BaseObject):
    id: str
    object: str
    created_at: int
    vector_store_id: str
    status: str
    file_counts: FileCounts


@dataclass
class VectorStoreList(BaseObject):
    object: str
    first_id: str
    last_id: str
    has_more: bool
    data: Optional[list[VectorStoreClient]]=None
    
@dataclass
class VectorstoreDeleted:
    id: str
    object: str = "vector_store.deleted"
    deleted: bool = True