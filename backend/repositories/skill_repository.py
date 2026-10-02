import uuid
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from models.skill import Skill, WorkerSkill

class SkillRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, skill_id: int) -> Optional[Skill]:
        return self.db.execute(select(Skill).where(Skill.id == skill_id)).scalar_one_or_none()

    def get_by_name(self, name: str) -> Optional[Skill]:
        return self.db.execute(select(Skill).where(Skill.name == name)).scalar_one_or_none()

    def list_skills(self, skip: int = 0, limit: int = 100) -> List[Skill]:
        return list(self.db.execute(select(Skill).offset(skip).limit(limit)).scalars().all())

    def create_skill(self, skill: Skill) -> Skill:
        try:
            self.db.add(skill)
            self.db.commit()
            self.db.refresh(skill)
            return skill
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def update_skill(self, skill: Skill) -> Skill:
        try:
            self.db.commit()
            self.db.refresh(skill)
            return skill
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def delete_skill(self, skill: Skill) -> None:
        try:
            self.db.delete(skill)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise

class WorkerSkillRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_skill(self, worker_id: uuid.UUID, skill_id: int) -> WorkerSkill:
        try:
            worker_skill = WorkerSkill(worker_id=worker_id, skill_id=skill_id)
            self.db.add(worker_skill)
            self.db.commit()
            self.db.refresh(worker_skill)
            return worker_skill
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def remove_skill(self, worker_id: uuid.UUID, skill_id: int) -> None:
        try:
            worker_skill = self.get_by_worker_and_skill(worker_id, skill_id)
            if worker_skill:
                self.db.delete(worker_skill)
                self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def get_worker_skills(self, worker_id: uuid.UUID) -> List[WorkerSkill]:
        return list(
            self.db.execute(
                select(WorkerSkill).options(joinedload(WorkerSkill.skill)).where(WorkerSkill.worker_id == worker_id)
            ).scalars().all()
        )

    def has_skill(self, worker_id: uuid.UUID, skill_id: int) -> bool:
        return self.get_by_worker_and_skill(worker_id, skill_id) is not None

    def get_by_worker_and_skill(self, worker_id: uuid.UUID, skill_id: int) -> Optional[WorkerSkill]:
        return self.db.execute(
            select(WorkerSkill).where(WorkerSkill.worker_id == worker_id, WorkerSkill.skill_id == skill_id)
        ).scalar_one_or_none()
