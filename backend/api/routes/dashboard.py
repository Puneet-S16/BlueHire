from typing import Any

from api.routes.auth import get_current_user
from core.exceptions import (
    EmployerNotFoundError,
    InvalidEmployerRoleError,
    InvalidWorkerRoleError,
    WorkerNotFoundError,
)
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.user import User
from repositories.dashboard_repository import DashboardRepository
from repositories.employer_repository import EmployerRepository
from repositories.worker_repository import WorkerRepository
from schemas.dashboard import EmployerDashboardResponse, WorkerDashboardResponse
from services.dashboard_service import DashboardService
from sqlalchemy.orm import Session

router = APIRouter()


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(DashboardRepository(db), WorkerRepository(db), EmployerRepository(db))


@router.get("/worker", response_model=WorkerDashboardResponse, summary="Get worker dashboard stats")
def get_worker_dashboard(
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> Any:
    try:
        return dashboard_service.get_worker_dashboard(current_user)
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/employer", response_model=EmployerDashboardResponse, summary="Get employer dashboard stats"
)
def get_employer_dashboard(
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> Any:
    try:
        return dashboard_service.get_employer_dashboard(current_user)
    except InvalidEmployerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except EmployerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
