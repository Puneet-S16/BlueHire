import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from models.experience import WorkHistory

class ExperienceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, experience_id: uuid.UUID) -> Optional[WorkHistory]:
        return self.db.execute(select(WorkHistory).where(WorkHistory.id == experience_id)).scalar_one_or_none()

    def get_by_worker_id(self, worker_id: uuid.UUID) -> List[WorkHistory]:
        return list(self.db.execute(select(WorkHistory).where(WorkHistory.worker_id == worker_id)).scalars().all())

    def create_experience(self, experience: WorkHistory) -> WorkHistory:
        try:
            self.db.add(experience)
            self.db.commit()
            self.db.refresh(experience)
            return experience
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def update_experience(self, experience: WorkHistory) -> WorkHistory:
        try:
            self.db.commit()
            self.db.refresh(experience)
            return experience
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def delete_experience(self, experience: WorkHistory) -> None:
        try:
            self.db.delete(experience)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise
