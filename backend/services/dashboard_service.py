from typing import Dict, Any
from models.user import User
from models.enums import RoleEnum
from repositories.dashboard_repository import DashboardRepository
from repositories.worker_repository import WorkerRepository
from repositories.employer_repository import EmployerRepository
from core.exceptions import InvalidWorkerRoleError, InvalidEmployerRoleError, WorkerNotFoundError, EmployerNotFoundError

class DashboardService:
    def __init__(self, dashboard_repo: DashboardRepository, worker_repo: WorkerRepository, employer_repo: EmployerRepository):
        self.dashboard_repo = dashboard_repo
        self.worker_repo = worker_repo
        self.employer_repo = employer_repo

    def get_worker_dashboard(self, user: User) -> Dict[str, Any]:
        if user.role != RoleEnum.WORKER:
            raise InvalidWorkerRoleError("User must have WORKER role")
            
        worker = self.worker_repo.get_by_user_id(user.id)
        if not worker:
            raise WorkerNotFoundError("Worker profile not found")
            
        return self.dashboard_repo.get_worker_dashboard_stats(user.id)

    def get_employer_dashboard(self, user: User) -> Dict[str, Any]:
        if user.role != RoleEnum.EMPLOYER:
            raise InvalidEmployerRoleError("User must have EMPLOYER role")
            
        employer = self.employer_repo.get_by_user_id(user.id)
        if not employer:
            raise EmployerNotFoundError("Employer profile not found")
            
        return self.dashboard_repo.get_employer_dashboard_stats(employer.company_id, user.id)
