import uuid
from typing import List
from models.user import User
from models.skill import Skill, WorkerSkill
from models.enums import RoleEnum
from schemas.skill import SkillCreate, SkillUpdate
from repositories.skill_repository import SkillRepository, WorkerSkillRepository
from repositories.worker_repository import WorkerRepository
from repositories.category_repository import CategoryRepository
from core.exceptions import (
    SkillAlreadyExistsError,
    SkillNotFoundError,
    WorkerSkillAlreadyExistsError,
    WorkerSkillNotFoundError,
    WorkerNotFoundError,
    InvalidWorkerRoleError,
    CategoryNotFoundError
)

class SkillService:
    def __init__(
        self,
        skill_repo: SkillRepository,
        worker_skill_repo: WorkerSkillRepository,
        worker_repo: WorkerRepository,
        category_repo: CategoryRepository
    ):
        self.skill_repo = skill_repo
        self.worker_skill_repo = worker_skill_repo
        self.worker_repo = worker_repo
        self.category_repo = category_repo

    def create_skill(self, request: SkillCreate) -> Skill:
        if not self.category_repo.get_by_id(request.category_id):
            raise CategoryNotFoundError("Category not found")
        if self.skill_repo.get_by_name(request.name):
            raise SkillAlreadyExistsError("Skill with this name already exists")
        skill = Skill(category_id=request.category_id, name=request.name)
        return self.skill_repo.create_skill(skill)

    def list_skills(self, skip: int = 0, limit: int = 100) -> List[Skill]:
        return self.skill_repo.list_skills(skip=skip, limit=limit)
        
    def get_skill(self, skill_id: int) -> Skill:
        skill = self.skill_repo.get_by_id(skill_id)
        if not skill:
            raise SkillNotFoundError("Skill not found")
        return skill

    def update_skill(self, skill_id: int, request: SkillUpdate) -> Skill:
        skill = self.get_skill(skill_id)
        if request.category_id is not None:
            if not self.category_repo.get_by_id(request.category_id):
                raise CategoryNotFoundError("Category not found")
            skill.category_id = request.category_id
        if request.name is not None and request.name != skill.name:
            if self.skill_repo.get_by_name(request.name):
                raise SkillAlreadyExistsError("Skill with this name already exists")
            skill.name = request.name
            
        return self.skill_repo.update_skill(skill)

    def delete_skill(self, skill_id: int) -> None:
        skill = self.get_skill(skill_id)
        self.skill_repo.delete_skill(skill)

    def _verify_worker(self, user: User):
        if user.role != RoleEnum.WORKER:
            raise InvalidWorkerRoleError("Only users with WORKER role can perform this action")
        worker = self.worker_repo.get_by_user_id(user.id)
        if not worker:
            raise WorkerNotFoundError("Worker profile not found")
        return worker

    def assign_skill_to_worker(self, user: User, skill_id: int) -> WorkerSkill:
        worker = self._verify_worker(user)
        
        # Verify skill exists
        self.get_skill(skill_id)
        
        if self.worker_skill_repo.has_skill(worker.user_id, skill_id):
            raise WorkerSkillAlreadyExistsError("Worker already has this skill")
            
        return self.worker_skill_repo.add_skill(worker.user_id, skill_id)

    def remove_skill_from_worker(self, user: User, skill_id: int) -> None:
        worker = self._verify_worker(user)
        
        if not self.worker_skill_repo.has_skill(worker.user_id, skill_id):
            raise WorkerSkillNotFoundError("Worker does not have this skill")
            
        self.worker_skill_repo.remove_skill(worker.user_id, skill_id)

    def get_my_skills(self, user: User) -> List[WorkerSkill]:
        worker = self._verify_worker(user)
        return self.worker_skill_repo.get_worker_skills(worker.user_id)
