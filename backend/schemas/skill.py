from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field, AliasPath

class SkillBase(BaseModel):
    category_id: int
    name: str = Field(..., min_length=1, max_length=100)

class SkillCreate(SkillBase):
    pass

class SkillUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)

class SkillResponse(SkillBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class WorkerSkillResponse(BaseModel):
    worker_id: uuid.UUID
    skill_id: int
    skill_name: str = Field(validation_alias=AliasPath('skill', 'name'))

    model_config = ConfigDict(from_attributes=True)
