import uuid
from typing import Optional

from models.enums import ApplicationStatusEnum
from pydantic import BaseModel, ConfigDict


class ApplicationBase(BaseModel):
    cover_letter: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatusEnum] = None
    cover_letter: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    id: uuid.UUID
    job_id: uuid.UUID
    worker_id: uuid.UUID
    status: ApplicationStatusEnum

    model_config = ConfigDict(from_attributes=True)
