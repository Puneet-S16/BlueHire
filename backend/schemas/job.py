import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator
from models.enums import JobTypeEnum, JobStatusEnum, PayTypeEnum

class JobBase(BaseModel):
    category_id: int
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    job_type: JobTypeEnum
    vacancies: int = Field(1, ge=1)
    experience_required_years: Optional[float] = Field(None, ge=0, le=100)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    pay_type: Optional[PayTypeEnum] = None
    pay_min: Optional[float] = Field(None, ge=0)
    pay_max: Optional[float] = Field(None, ge=0)
    expires_at: Optional[datetime] = None

class JobCreate(JobBase):
    @model_validator(mode='after')
    def check_pay_range(self) -> 'JobCreate':
        if self.pay_min is not None and self.pay_max is not None:
            if self.pay_min > self.pay_max:
                raise ValueError('pay_min cannot be greater than pay_max')
        return self

class JobUpdate(BaseModel):
    category_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    job_type: Optional[JobTypeEnum] = None
    status: Optional[JobStatusEnum] = None
    vacancies: Optional[int] = Field(None, ge=1)
    experience_required_years: Optional[float] = Field(None, ge=0, le=100)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    pay_type: Optional[PayTypeEnum] = None
    pay_min: Optional[float] = Field(None, ge=0)
    pay_max: Optional[float] = Field(None, ge=0)
    expires_at: Optional[datetime] = None

    @model_validator(mode='after')
    def check_pay_range(self) -> 'JobUpdate':
        if self.pay_min is not None and self.pay_max is not None:
            if self.pay_min > self.pay_max:
                raise ValueError('pay_min cannot be greater than pay_max')
        return self

class JobResponse(JobBase):
    id: uuid.UUID
    company_id: uuid.UUID
    posted_by_id: Optional[uuid.UUID]
    status: JobStatusEnum

    model_config = ConfigDict(from_attributes=True)
