import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from models.enums import AvailabilityStatusEnum

class WorkerBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    profile_photo_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = None
    total_experience_years: Optional[float] = Field(None, ge=0, le=100)
    expected_salary: Optional[float] = Field(None, ge=0)
    availability_status: AvailabilityStatusEnum = AvailabilityStatusEnum.AVAILABLE
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)

class WorkerCreate(WorkerBase):
    pass

class WorkerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    profile_photo_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = None
    total_experience_years: Optional[float] = Field(None, ge=0, le=100)
    expected_salary: Optional[float] = Field(None, ge=0)
    availability_status: Optional[AvailabilityStatusEnum] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)

class WorkerResponse(WorkerBase):
    user_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
