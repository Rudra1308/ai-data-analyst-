from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class DatasetBase(BaseModel):
    filename: str
    file_size: int
    row_count: Optional[int] = None
    col_count: Optional[int] = None


class DatasetResponse(DatasetBase):
    id: str
    project_id: str
    file_path: str
    schema_json: Optional[Dict[str, Any]] = None
    profile_json: Optional[Dict[str, Any]] = None
    version: int
    created_at: datetime

    class Config:
        from_attributes = True
