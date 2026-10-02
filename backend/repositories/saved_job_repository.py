import uuid
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from models.saved_job import SavedJob

class SavedJobRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_saved_job(self, worker_id: uuid.UUID, job_id: uuid.UUID) -> SavedJob:
        return self.db.execute(
            select(SavedJob)
            .where(SavedJob.worker_id == worker_id, SavedJob.job_id == job_id)
        ).scalar_one_or_none()

    def get_saved_jobs(self, worker_id: uuid.UUID, page: int = 1, page_size: int = 20) -> Tuple[int, List[SavedJob]]:
        query = select(SavedJob).where(SavedJob.worker_id == worker_id)
        
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar() or 0
        
        query = query.order_by(SavedJob.created_at.desc())
        skip = (page - 1) * page_size
        query = query.offset(skip).limit(page_size)
        
        records = list(self.db.execute(query).scalars().all())
        return total, records

    def save_job(self, saved_job: SavedJob) -> SavedJob:
        try:
            self.db.add(saved_job)
            self.db.commit()
            self.db.refresh(saved_job)
            return saved_job
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def unsave_job(self, saved_job: SavedJob) -> None:
        try:
            self.db.delete(saved_job)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise
