import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from models.enums import VerificationStatusEnum

class CompanyBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None

class CompanyResponse(CompanyBase):
    id: uuid.UUID
    verification_status: VerificationStatusEnum

    model_config = ConfigDict(from_attributes=True)
