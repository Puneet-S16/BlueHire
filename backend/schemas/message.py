import uuid
from typing import List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)

class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    content: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MessageListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[MessageResponse]
