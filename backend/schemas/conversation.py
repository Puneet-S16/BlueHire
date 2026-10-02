import uuid
from typing import List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ConversationCreate(BaseModel):
    application_id: uuid.UUID

class ConversationResponse(BaseModel):
    id: uuid.UUID
    application_id: uuid.UUID
    employer_id: uuid.UUID
    worker_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConversationListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[ConversationResponse]
