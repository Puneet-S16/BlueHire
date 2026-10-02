import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class EmployerBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    job_title: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    company_id: Optional[uuid.UUID] = None

class EmployerCreate(EmployerBase):
    pass

class EmployerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    job_title: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    company_id: Optional[uuid.UUID] = None

class EmployerResponse(EmployerBase):
    user_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
