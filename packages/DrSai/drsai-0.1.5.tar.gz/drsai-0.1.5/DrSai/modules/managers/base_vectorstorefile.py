
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel
import time

# def extracts_dict_keys(data_list, keys):
#     return [{key: item.get(key, 'Unknown') for key in keys} for item in data_list]

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

class LastError(BaseModel):
    code: Literal["internal_error", "file_not_found", "parsing_error", "unhandled_mime_type"]
    """One of `server_error` or `rate_limit_exceeded`."""

    message: str
    """A human-readable description of the error."""

@dataclass
class VectorStoreFileClient(BaseObject):
    id: str
    object: Literal["vector_store.file"]
    created_at: int
    vector_store_id: Optional[str]
    usage_bytes: int
    status: Literal["in_progress", "completed", "cancelled", "failed"]
    last_error: Optional[LastError] = None

@dataclass
class ExpiresAfter(BaseModel):
    anchor: Optional[str]=None
    days: Optional[int]=None

@dataclass
class VectorStoreFile(BaseObject):
    id: str
    created_at: int
    usage_bytes: int
    vector_store_id: str
    object: Literal["vector_store.file"]
    status: Literal["in_progress", "completed", "cancelled", "failed"]
    last_error: Optional[LastError] = None
    username: Optional[str] = None
    last_active_at: Optional[int] = None
    metadata: Dict[str, Any] = None
    deleted: Optional[bool] = False
    
    @property
    def output_keys(self):
        """定义了网络请求时需要返回的字段"""
        return ["id", "object", "created_at", "usage_bytes", "vector_store_id",
                "status","last_error", "username","last_active_at", "metadata", "deleted"]
    
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
        return ["name", "usage_bytes", "object", "status", "last_error", 
                "id", "last_active_at", "metadata", "deleted"]


@dataclass
class VectorStoreFileList(BaseObject):
    object: str
    first_id: str
    last_id: str
    has_more: bool
    data: Optional[list[VectorStoreFileClient]]=None
    
@dataclass
class VectorStoreFileDeleted:
    id: str
    object: str = "vector_store_file.deleted"
    deleted: bool = True


@dataclass
class FileCounts(BaseModel):
    in_progress: int
    completed: int
    failed: int
    cancelled: int
    total: int

@dataclass
class VectorStoreFileBatch(BaseObject):
    id: str
    object: str
    created_at: int
    vector_store_id: str
    status: str
    file_counts: FileCounts
