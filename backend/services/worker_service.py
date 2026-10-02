import uuid
from models.user import User
from models.worker import Worker
from models.enums import RoleEnum
from schemas.worker import WorkerCreate, WorkerUpdate
from repositories.worker_repository import WorkerRepository
from core.exceptions import WorkerAlreadyExistsError, WorkerNotFoundError, InvalidWorkerRoleError

class WorkerService:
    def __init__(self, worker_repo: WorkerRepository):
        self.worker_repo = worker_repo

    def create_worker_profile(self, user: User, request: WorkerCreate) -> Worker:
        if user.role != RoleEnum.WORKER:
            raise InvalidWorkerRoleError("Only users with WORKER role can create a worker profile")

        existing_worker = self.worker_repo.get_by_user_id(user.id)
        if existing_worker:
            raise WorkerAlreadyExistsError("User already has a worker profile")

        worker = Worker(
            user_id=user.id,
            first_name=request.first_name,
            last_name=request.last_name,
            phone_number=request.phone_number,
            profile_photo_url=request.profile_photo_url,
            bio=request.bio,
            total_experience_years=request.total_experience_years,
            expected_salary=request.expected_salary,
            availability_status=request.availability_status,
            city=request.city,
            state=request.state,
            latitude=request.latitude,
            longitude=request.longitude
        )
        return self.worker_repo.create_worker(worker)

    def get_my_profile(self, user_id: uuid.UUID) -> Worker:
        worker = self.worker_repo.get_by_user_id(user_id)
        if not worker:
            raise WorkerNotFoundError("Worker profile not found")
        return worker

    def update_my_profile(self, user_id: uuid.UUID, request: WorkerUpdate) -> Worker:
        worker = self.worker_repo.get_by_user_id(user_id)
        if not worker:
            raise WorkerNotFoundError("Worker profile not found")

        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(worker, key, value)
            
        return self.worker_repo.update_worker(worker)
