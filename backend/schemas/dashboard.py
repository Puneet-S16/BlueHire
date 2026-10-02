from pydantic import BaseModel
from typing import List, Any
from schemas.application import ApplicationResponse
from schemas.job import JobResponse

class WorkerDashboardResponse(BaseModel):
    total_applications: int
    active_applications: int
    shortlisted_count: int
    rejected_count: int
    recent_applications: List[ApplicationResponse]
    unread_notifications: int
    unread_messages: int

class EmployerDashboardResponse(BaseModel):
    total_jobs_posted: int
    active_jobs: int
    total_applications_received: int
    recent_applications: List[ApplicationResponse]
    recent_jobs: List[JobResponse]
    unread_messages: int
