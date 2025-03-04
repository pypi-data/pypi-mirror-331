
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
class ExpiresAfter(BaseModel):
    anchor: Optional[str]=None
    days: Optional[int]=None


@dataclass
class File(BaseObject):
    id: str
    created_at: int
    filename: str
    bytes: int
    uploader : str
    file_path: str
    sha256: str
    file_type: str
    content_file_name: str
    purpose: Literal[
        "assistants", "assistants_output", "batch", "batch_output", "fine-tune", "fine-tune-results", "vision"
    ]
    object: Literal["file"]
    status: Literal["uploaded", "processed", "error"]
    status_details: Optional[str] = None
    expires_after: Optional[ExpiresAfter]=None
    expires_at: Optional[int]=None
    last_active_at: Optional[int] = None
    metadata: Dict[str, Any] = None
    username: Optional[str] = None
    deleted: Optional[bool] = False
    
    @property
    def output_keys(self):
        """定义了网络请求时需要返回的字段"""
        return ["id", "object", "created_at", "filename", "bytes", "sha256", "map_id", "file_path", "file_type","uploader","content_file_name",
                "purpose", "status", "status_details", "username", "expires_after", "expires_at", "last_active_at", "metadata", "deleted"]
    
    @property
    def allowed_update_keys(self):
        return ["filename", "purpose", "status", "status_details", "bytes", "last_active_at", "metadata", "deleted"]


@dataclass
class FileClient(BaseObject):
    id: str
    created_at: int
    object: Literal["file"]
    status: Literal["uploaded", "processed", "error"]
    purpose: Literal["assistants", "assistants_output", "batch", "batch_output", "fine-tune", "fine-tune-results", "vision"]
    bytes: int
    filename: str
    status_details: Optional[str]=None

@dataclass
class FileContent(BaseObject):
    id: str
    filetype: str
    content: str
    filename: str