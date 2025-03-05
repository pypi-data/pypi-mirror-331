from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Enterprise(BaseModel):
    object_id: int
    name: str


class AgentTag(BaseModel):
    object_id: int
    slug: str
    name: str
    document_count: int
    owner: Optional[int]
    user_can_change: bool


class FileMetadata(BaseModel):
    object_id: int = Field(alias="id")
    filename: str = Field(alias="original_file_name")
    enterprise_object_id: int = Field(alias="storage_path")
    enterprise_name: str = ""
    agent_tag_ids: List[int] = Field(default_factory=list, alias="tags")
    agent_tag_names: List[str] = Field(default_factory=list)
    created: datetime
    modified: datetime
    deleted_at: Optional[datetime] = None
    owner_object_id: int = Field(alias="owner")


class DownloadStatus(BaseModel):
    status: bool
    message: str
