import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from models.application import Application

class ApplicationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, application_id: uuid.UUID) -> Optional[Application]:
        return self.db.execute(select(Application).where(Application.id == application_id)).scalar_one_or_none()

    def get_by_job_id(self, job_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Application]:
        return list(self.db.execute(select(Application).where(Application.job_id == job_id).offset(skip).limit(limit)).scalars().all())

    def get_by_worker_id(self, worker_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Application]:
        return list(self.db.execute(select(Application).where(Application.worker_id == worker_id).offset(skip).limit(limit)).scalars().all())

    def get_by_worker_and_job(self, worker_id: uuid.UUID, job_id: uuid.UUID) -> Optional[Application]:
        return self.db.execute(
            select(Application).where(Application.worker_id == worker_id, Application.job_id == job_id)
        ).scalar_one_or_none()

    def create_application(self, application: Application) -> Application:
        try:
            self.db.add(application)
            self.db.commit()
            self.db.refresh(application)
            return application
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def update_application(self, application: Application) -> Application:
        try:
            self.db.commit()
            self.db.refresh(application)
            return application
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def delete_application(self, application: Application) -> None:
        try:
            self.db.delete(application)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise
