from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class MessageRequest(BaseModel):
    content: str
    dataset_id: Optional[str] = None
    api_keys: Optional[Dict[str, str]] = None
    model_settings: Optional[Dict[str, str]] = None




class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    generated_code: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    agent_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    title: str


class ConversationCreate(BaseModel):
    project_id: str
    title: Optional[str] = "New Analysis"


class ConversationResponse(ConversationBase):
    id: str
    project_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True
