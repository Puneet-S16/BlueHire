from typing import List, Tuple

from core.exceptions import InvalidWorkerRoleError, WorkerNotFoundError
from models.enums import RoleEnum
from models.user import User
from repositories.recommendation_repository import RecommendationRepository
from repositories.worker_repository import WorkerRepository


class RecommendationService:
    def __init__(
        self, recommendation_repo: RecommendationRepository, worker_repo: WorkerRepository
    ):
        self.recommendation_repo = recommendation_repo
        self.worker_repo = worker_repo

    def calculate_recommendations(
        self, user: User, page: int = 1, page_size: int = 20
    ) -> Tuple[int, List[dict]]:
        if user.role != RoleEnum.WORKER:
            raise InvalidWorkerRoleError("User must have WORKER role to get recommendations")

        worker = self.worker_repo.get_by_user_id(user.id)
        if not worker:
            raise WorkerNotFoundError("Worker profile not found")

        return self.recommendation_repo.get_recommended_jobs(worker, page, page_size)
