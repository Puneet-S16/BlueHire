import uuid
from typing import List
from models.user import User
from models.application import Application
from models.enums import RoleEnum, JobStatusEnum
from schemas.application import ApplicationCreate, ApplicationUpdate
from repositories.application_repository import ApplicationRepository
from repositories.worker_repository import WorkerRepository
from repositories.employer_repository import EmployerRepository
from repositories.job_repository import JobRepository
from core.exceptions import (
    ApplicationAlreadyExistsError,
    ApplicationNotFoundError,
    InvalidApplicationOwnershipError,
    JobNotOpenError,
    WorkerNotFoundError,
    EmployerNotFoundError,
    JobNotFoundError,
    InvalidWorkerRoleError,
    InvalidEmployerRoleError
)

class ApplicationService:
    def __init__(
        self,
        application_repo: ApplicationRepository,
        worker_repo: WorkerRepository,
        employer_repo: EmployerRepository,
        job_repo: JobRepository
    ):
        self.application_repo = application_repo
        self.worker_repo = worker_repo
        self.employer_repo = employer_repo
        self.job_repo = job_repo

    def apply_to_job(self, user: User, job_id: uuid.UUID, request: ApplicationCreate) -> Application:
        if user.role != RoleEnum.WORKER:
            raise InvalidWorkerRoleError("Only workers can apply to jobs")
            
        worker = self.worker_repo.get_by_user_id(user.id)
        if not worker:
            raise WorkerNotFoundError("Worker profile not found")
            
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise JobNotFoundError("Job not found")
            
        if job.status != JobStatusEnum.ACTIVE:
            raise JobNotOpenError("This job is not open for applications")
            
        existing_app = self.application_repo.get_by_worker_and_job(worker.user_id, job.id)
        if existing_app:
            raise ApplicationAlreadyExistsError("You have already applied to this job")
            
        application = Application(
            job_id=job.id,
            worker_id=worker.user_id,
            cover_letter=request.cover_letter
        )
        return self.application_repo.create_application(application)

    def get_my_applications(self, user: User) -> List[Application]:
        if user.role != RoleEnum.WORKER:
            raise InvalidWorkerRoleError("Only workers can view their applications")
            
        worker = self.worker_repo.get_by_user_id(user.id)
        if not worker:
            raise WorkerNotFoundError("Worker profile not found")
            
        return self.application_repo.get_by_worker_id(worker.user_id)

    def get_job_applications(self, user: User, job_id: uuid.UUID) -> List[Application]:
        if user.role != RoleEnum.EMPLOYER:
            raise InvalidEmployerRoleError("Only employers can view job applications")
            
        employer = self.employer_repo.get_by_user_id(user.id)
        if not employer:
            raise EmployerNotFoundError("Employer profile not found")
            
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise JobNotFoundError("Job not found")
            
        if job.company_id != employer.company_id:
            raise InvalidApplicationOwnershipError("You can only view applications for your company's jobs")
            
        return self.application_repo.get_by_job_id(job.id)

    def update_application_status(self, user: User, application_id: uuid.UUID, request: ApplicationUpdate) -> Application:
        application = self.application_repo.get_by_id(application_id)
        if not application:
            raise ApplicationNotFoundError("Application not found")
            
        if user.role == RoleEnum.EMPLOYER:
            employer = self.employer_repo.get_by_user_id(user.id)
            if not employer:
                raise EmployerNotFoundError("Employer profile not found")
                
            job = self.job_repo.get_by_id(application.job_id)
            if not job or job.company_id != employer.company_id:
                raise InvalidApplicationOwnershipError("You do not have permission to modify this application")
                
            if request.status is not None:
                application.status = request.status
                
        elif user.role == RoleEnum.WORKER:
            if application.worker_id != user.id:
                raise InvalidApplicationOwnershipError("You do not have permission to modify this application")
                
            if request.status is not None:
                raise InvalidApplicationOwnershipError("Workers cannot update application status")
                
            if request.cover_letter is not None:
                application.cover_letter = request.cover_letter
        else:
            raise InvalidApplicationOwnershipError("Invalid role for modifying applications")
            
        return self.application_repo.update_application(application)

    def withdraw_application(self, user: User, application_id: uuid.UUID) -> None:
        if user.role != RoleEnum.WORKER:
            raise InvalidWorkerRoleError("Only workers can withdraw their applications")
            
        application = self.application_repo.get_by_id(application_id)
        if not application:
            raise ApplicationNotFoundError("Application not found")
            
        if application.worker_id != user.id:
            raise InvalidApplicationOwnershipError("You do not have permission to withdraw this application")
            
        self.application_repo.delete_application(application)
