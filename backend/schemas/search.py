from typing import Optional, List
import uuid
from pydantic import BaseModel, Field
from models.enums import JobTypeEnum
from schemas.job import JobResponse

class SearchJobsRequest(BaseModel):
    keyword: Optional[str] = None
    category_id: Optional[int] = None
    company_id: Optional[uuid.UUID] = None
    city: Optional[str] = None
    state: Optional[str] = None
    job_type: Optional[JobTypeEnum] = None
    min_salary: Optional[float] = Field(None, ge=0)
    max_salary: Optional[float] = Field(None, ge=0)
    experience_required_years: Optional[int] = Field(None, ge=0)
    is_remote: Optional[bool] = None
    
    # Pagination
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    
    # Sorting
    sort_by: Optional[str] = Field("newest", pattern="^(newest|oldest|salary_high|salary_low)$")

class SearchJobsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[JobResponse]
