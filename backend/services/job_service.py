import uuid
from typing import List
from models.user import User
from models.job import Job
from models.enums import RoleEnum
from schemas.job import JobCreate, JobUpdate
from repositories.job_repository import JobRepository
from repositories.employer_repository import EmployerRepository
from core.exceptions import JobNotFoundError, InvalidJobOwnershipError, EmployerNotFoundError, InvalidEmployerRoleError

class JobService:
    def __init__(self, job_repo: JobRepository, employer_repo: EmployerRepository):
        self.job_repo = job_repo
        self.employer_repo = employer_repo

    def _get_employer_and_verify(self, user: User):
        if user.role != RoleEnum.EMPLOYER:
            raise InvalidEmployerRoleError("Only users with EMPLOYER role can perform this action")
        
        employer = self.employer_repo.get_by_user_id(user.id)
        if not employer:
            raise EmployerNotFoundError("Employer profile not found")
            
        if not employer.company_id:
            raise InvalidJobOwnershipError("Employer must be linked to a company to post jobs")
            
        return employer

    def create_job(self, user: User, request: JobCreate) -> Job:
        employer = self._get_employer_and_verify(user)

        job = Job(
            company_id=employer.company_id,
            posted_by_id=employer.user_id,
            **request.model_dump()
        )
        return self.job_repo.create_job(job)

    def get_job(self, job_id: uuid.UUID) -> Job:
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise JobNotFoundError("Job not found")
        return job

    def list_jobs(self, skip: int = 0, limit: int = 100) -> List[Job]:
        return self.job_repo.list_jobs(skip=skip, limit=limit)

    def update_job(self, user: User, job_id: uuid.UUID, request: JobUpdate) -> Job:
        employer = self._get_employer_and_verify(user)
        job = self.get_job(job_id)

        if job.company_id != employer.company_id:
            raise InvalidJobOwnershipError("You do not have permission to modify this job")

        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(job, key, value)
            
        return self.job_repo.update_job(job)

    def delete_job(self, user: User, job_id: uuid.UUID) -> None:
        employer = self._get_employer_and_verify(user)
        job = self.get_job(job_id)

        if job.company_id != employer.company_id:
            raise InvalidJobOwnershipError("You do not have permission to delete this job")

        self.job_repo.delete_job(job)
