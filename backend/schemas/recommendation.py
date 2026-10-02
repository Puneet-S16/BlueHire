from typing import List
from pydantic import BaseModel, ConfigDict
from schemas.job import JobResponse

class RecommendedJobResponse(BaseModel):
    job: JobResponse
    match_score: int
    
    model_config = ConfigDict(from_attributes=True)

class RecommendationListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[RecommendedJobResponse]
