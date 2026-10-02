import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from models.enums import DocumentTypeEnum

class DocumentBase(BaseModel):
    document_type: DocumentTypeEnum
    file_url: str = Field(..., min_length=1, max_length=500)
    file_name: Optional[str] = Field(None, max_length=255)

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    file_url: Optional[str] = Field(None, min_length=1, max_length=500)
    file_name: Optional[str] = Field(None, max_length=255)

class DocumentResponse(DocumentBase):
    id: uuid.UUID
    worker_id: uuid.UUID = Field(validation_alias='uploader_id')
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
