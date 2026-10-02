import uuid
from typing import List, Tuple
from models.user import User
from models.saved_job import SavedJob
from models.enums import RoleEnum, JobStatusEnum
from repositories.saved_job_repository import SavedJobRepository
from repositories.worker_repository import WorkerRepository
from repositories.job_repository import JobRepository
from core.exceptions import (
    SavedJobAlreadyExistsError,
    SavedJobNotFoundError,
    InvalidWorkerRoleError,
    WorkerNotFoundError,
    JobNotFoundError,
    JobNotOpenError
)

class SavedJobService:
    def __init__(self, saved_job_repo: SavedJobRepository, worker_repo: WorkerRepository, job_repo: JobRepository):
        self.saved_job_repo = saved_job_repo
        self.worker_repo = worker_repo
        self.job_repo = job_repo

    def _verify_worker(self, user: User):
        if user.role != RoleEnum.WORKER:
            raise InvalidWorkerRoleError("User must have WORKER role")
        worker = self.worker_repo.get_by_user_id(user.id)
        if not worker:
            raise WorkerNotFoundError("Worker profile not found")
        return worker

    def save_job(self, user: User, job_id: uuid.UUID) -> SavedJob:
        self._verify_worker(user)
        
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise JobNotFoundError("Job not found")
            
        if job.status != JobStatusEnum.ACTIVE:
            raise JobNotOpenError("Only ACTIVE jobs can be saved")
            
        existing = self.saved_job_repo.get_saved_job(user.id, job_id)
        if existing:
            raise SavedJobAlreadyExistsError("Job is already saved")
            
        saved_job = SavedJob(worker_id=user.id, job_id=job_id)
        return self.saved_job_repo.save_job(saved_job)

    def unsave_job(self, user: User, job_id: uuid.UUID) -> None:
        self._verify_worker(user)
        
        existing = self.saved_job_repo.get_saved_job(user.id, job_id)
        if not existing:
            raise SavedJobNotFoundError("Saved job not found")
            
        self.saved_job_repo.unsave_job(existing)

    def get_saved_jobs(self, user: User, page: int = 1, page_size: int = 20) -> Tuple[int, List[SavedJob]]:
        self._verify_worker(user)
        return self.saved_job_repo.get_saved_jobs(user.id, page, page_size)
