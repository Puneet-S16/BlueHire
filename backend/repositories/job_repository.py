import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.job import Job

class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, job_id: uuid.UUID) -> Optional[Job]:
        return self.db.execute(select(Job).where(Job.id == job_id)).scalar_one_or_none()

    def create_job(self, job: Job) -> Job:
        try:
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)
            return job
        except Exception:
            self.db.rollback()
            raise

    def update_job(self, job: Job) -> Job:
        try:
            self.db.commit()
            self.db.refresh(job)
            return job
        except Exception:
            self.db.rollback()
            raise

    def delete_job(self, job: Job) -> None:
        try:
            self.db.delete(job)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def list_jobs(self, skip: int = 0, limit: int = 100) -> List[Job]:
        return list(self.db.execute(select(Job).offset(skip).limit(limit)).scalars().all())
