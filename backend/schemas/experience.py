import uuid
from typing import Optional
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, model_validator

class ExperienceBase(BaseModel):
    company_name: str = Field(..., max_length=255)
    job_title: str = Field(..., max_length=150)
    employment_type: str = Field(..., max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    currently_working: bool = False
    description: Optional[str] = None

class ExperienceCreate(ExperienceBase):
    @model_validator(mode='after')
    def validate_dates(self) -> 'ExperienceCreate':
        if self.currently_working and self.end_date is not None:
            raise ValueError("end_date must be None if currently_working is True")
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date must be >= start_date")
        return self

class ExperienceUpdate(BaseModel):
    company_name: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=150)
    employment_type: Optional[str] = Field(None, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    currently_working: Optional[bool] = None
    description: Optional[str] = None

    @model_validator(mode='after')
    def validate_dates(self) -> 'ExperienceUpdate':
        if self.currently_working is True and self.end_date is not None:
            raise ValueError("end_date must be None if currently_working is True")
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date must be >= start_date")
        return self

class ExperienceResponse(ExperienceBase):
    id: uuid.UUID
    worker_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
