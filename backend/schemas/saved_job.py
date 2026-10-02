import uuid
from typing import List
from pydantic import BaseModel, ConfigDict
from schemas.job import JobResponse

class SavedJobResponse(BaseModel):
    worker_id: uuid.UUID
    job_id: uuid.UUID
    job: JobResponse

    model_config = ConfigDict(from_attributes=True)

class SavedJobListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[SavedJobResponse]
