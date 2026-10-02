import uuid
from typing import List
from models.user import User
from models.experience import Education
from models.enums import RoleEnum
from schemas.education import EducationCreate, EducationUpdate
from repositories.education_repository import EducationRepository
from repositories.worker_repository import WorkerRepository
from core.exceptions import (
    EducationNotFoundError,
    InvalidEducationOwnershipError,
    WorkerNotFoundError,
    InvalidWorkerRoleError
)

class EducationService:
    def __init__(self, education_repo: EducationRepository, worker_repo: WorkerRepository):
        self.education_repo = education_repo
        self.worker_repo = worker_repo

    def _verify_worker(self, user: User):
        if user.role != RoleEnum.WORKER:
            raise InvalidWorkerRoleError("Only users with WORKER role can perform this action")
        worker = self.worker_repo.get_by_user_id(user.id)
        if not worker:
            raise WorkerNotFoundError("Worker profile not found")
        return worker

    def create_education(self, user: User, request: EducationCreate) -> Education:
        self._verify_worker(user)
        
        education = Education(
            worker_id=user.id,
            **request.model_dump()
        )
        return self.education_repo.create_education(education)

    def get_my_education(self, user: User) -> List[Education]:
        self._verify_worker(user)
        return self.education_repo.get_by_worker_id(user.id)

    def update_education(self, user: User, education_id: uuid.UUID, request: EducationUpdate) -> Education:
        self._verify_worker(user)
        
        education = self.education_repo.get_by_id(education_id)
        if not education:
            raise EducationNotFoundError("Education entry not found")
            
        if education.worker_id != user.id:
            raise InvalidEducationOwnershipError("You do not have permission to modify this education entry")
            
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(education, key, value)
            
        # Optional cross-field validation for start_date and end_date if partially updated
        if education.start_date and education.end_date and education.end_date < education.start_date:
            raise ValueError("end_date must be >= start_date")
            
        return self.education_repo.update_education(education)

    def delete_education(self, user: User, education_id: uuid.UUID) -> None:
        self._verify_worker(user)
        
        education = self.education_repo.get_by_id(education_id)
        if not education:
            raise EducationNotFoundError("Education entry not found")
            
        if education.worker_id != user.id:
            raise InvalidEducationOwnershipError("You do not have permission to delete this education entry")
            
        self.education_repo.delete_education(education)
