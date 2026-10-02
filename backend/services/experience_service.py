import uuid
from typing import List
from models.user import User
from models.experience import WorkHistory
from models.enums import RoleEnum
from schemas.experience import ExperienceCreate, ExperienceUpdate
from repositories.experience_repository import ExperienceRepository
from repositories.worker_repository import WorkerRepository
from core.exceptions import (
    ExperienceNotFoundError,
    InvalidExperienceOwnershipError,
    WorkerNotFoundError,
    InvalidWorkerRoleError
)

class ExperienceService:
    def __init__(self, experience_repo: ExperienceRepository, worker_repo: WorkerRepository):
        self.experience_repo = experience_repo
        self.worker_repo = worker_repo

    def _verify_worker(self, user: User):
        if user.role != RoleEnum.WORKER:
            raise InvalidWorkerRoleError("Only users with WORKER role can perform this action")
        worker = self.worker_repo.get_by_user_id(user.id)
        if not worker:
            raise WorkerNotFoundError("Worker profile not found")
        return worker

    def create_experience(self, user: User, request: ExperienceCreate) -> WorkHistory:
        self._verify_worker(user)
        
        experience = WorkHistory(
            worker_id=user.id,
            **request.model_dump()
        )
        return self.experience_repo.create_experience(experience)

    def get_my_experience(self, user: User) -> List[WorkHistory]:
        self._verify_worker(user)
        return self.experience_repo.get_by_worker_id(user.id)

    def update_experience(self, user: User, experience_id: uuid.UUID, request: ExperienceUpdate) -> WorkHistory:
        self._verify_worker(user)
        
        experience = self.experience_repo.get_by_id(experience_id)
        if not experience:
            raise ExperienceNotFoundError("Experience entry not found")
            
        if experience.worker_id != user.id:
            raise InvalidExperienceOwnershipError("You do not have permission to modify this experience entry")
            
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(experience, key, value)
            
        # Cross-field validation if partially updated
        if experience.currently_working and experience.end_date is not None:
            raise ValueError("end_date must be None if currently_working is True")
        if experience.start_date and experience.end_date and experience.end_date < experience.start_date:
            raise ValueError("end_date must be >= start_date")
            
        return self.experience_repo.update_experience(experience)

    def delete_experience(self, user: User, experience_id: uuid.UUID) -> None:
        self._verify_worker(user)
        
        experience = self.experience_repo.get_by_id(experience_id)
        if not experience:
            raise ExperienceNotFoundError("Experience entry not found")
            
        if experience.worker_id != user.id:
            raise InvalidExperienceOwnershipError("You do not have permission to delete this experience entry")
            
        self.experience_repo.delete_experience(experience)
