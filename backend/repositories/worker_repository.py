import uuid
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.worker import Worker

class WorkerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Worker]:
        return self.db.query(Worker).filter(Worker.user_id == user_id).first()

    def create_worker(self, worker: Worker) -> Worker:
        try:
            self.db.add(worker)
            self.db.commit()
            self.db.refresh(worker)
            return worker
        except Exception:
            self.db.rollback()
            raise

    def update_worker(self, worker: Worker) -> Worker:
        try:
            self.db.commit()
            self.db.refresh(worker)
            return worker
        except Exception:
            self.db.rollback()
            raise

    def delete_worker(self, worker: Worker) -> None:
        try:
            self.db.delete(worker)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
