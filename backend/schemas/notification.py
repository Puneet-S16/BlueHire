import uuid
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NotificationListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[NotificationResponse]

class WorkerDashboardResponse(BaseModel):
    total_applications: int
    active_applications: int
    shortlisted_count: int
    rejected_count: int
    recent_applications: list  # Will be a list of minimal application data

class EmployerDashboardResponse(BaseModel):
    total_jobs_posted: int
    active_jobs: int
    total_applications_received: int
    recent_applications: list
    recent_jobs: list
