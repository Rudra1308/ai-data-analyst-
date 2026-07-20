from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class DashboardBase(BaseModel):
    name: str
    layout_json: Optional[Dict[str, Any]] = None


class DashboardCreate(DashboardBase):
    project_id: str


class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    layout_json: Optional[Dict[str, Any]] = None


class DashboardResponse(DashboardBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
export_files = [DashboardResponse]
