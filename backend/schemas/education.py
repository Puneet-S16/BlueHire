import uuid
from typing import Optional
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, model_validator

class EducationBase(BaseModel):
    institution_name: str = Field(..., min_length=1, max_length=255)
    degree: str = Field(..., min_length=1, max_length=150)
    field_of_study: Optional[str] = Field(None, max_length=150)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    grade: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None

class EducationCreate(EducationBase):
    @model_validator(mode='after')
    def validate_dates(self) -> 'EducationCreate':
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date must be >= start_date")
        return self

class EducationUpdate(BaseModel):
    institution_name: Optional[str] = Field(None, min_length=1, max_length=255)
    degree: Optional[str] = Field(None, min_length=1, max_length=150)
    field_of_study: Optional[str] = Field(None, max_length=150)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    grade: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None

    @model_validator(mode='after')
    def validate_dates(self) -> 'EducationUpdate':
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date must be >= start_date")
        return self

class EducationResponse(EducationBase):
    id: uuid.UUID
    worker_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
