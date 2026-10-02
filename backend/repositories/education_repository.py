import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from models.experience import Education

class EducationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, education_id: uuid.UUID) -> Optional[Education]:
        return self.db.execute(select(Education).where(Education.id == education_id)).scalar_one_or_none()

    def get_by_worker_id(self, worker_id: uuid.UUID) -> List[Education]:
        return list(self.db.execute(select(Education).where(Education.worker_id == worker_id)).scalars().all())

    def create_education(self, education: Education) -> Education:
        try:
            self.db.add(education)
            self.db.commit()
            self.db.refresh(education)
            return education
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def update_education(self, education: Education) -> Education:
        try:
            self.db.commit()
            self.db.refresh(education)
            return education
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def delete_education(self, education: Education) -> None:
        try:
            self.db.delete(education)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise
