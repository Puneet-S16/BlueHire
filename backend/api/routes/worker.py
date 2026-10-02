from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from models.user import User
from models.enums import RoleEnum
from schemas.worker import WorkerCreate, WorkerUpdate, WorkerResponse
from repositories.worker_repository import WorkerRepository
from services.worker_service import WorkerService
from core.exceptions import WorkerAlreadyExistsError, WorkerNotFoundError, InvalidWorkerRoleError

from api.routes.auth import get_current_user

router = APIRouter()

def get_worker_service(db: Session = Depends(get_db)) -> WorkerService:
    worker_repo = WorkerRepository(db)
    return WorkerService(worker_repo)

def require_worker_role(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.WORKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only users with the WORKER role can access this endpoint"
        )
    return current_user

@router.post("/me", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED, summary="Create my worker profile")
def create_worker_profile(
    request: WorkerCreate,
    current_user: User = Depends(require_worker_role),
    worker_service: WorkerService = Depends(get_worker_service)
) -> Any:
    """
    Create a worker profile for the authenticated user.
    """
    try:
        return worker_service.create_worker_profile(current_user, request)
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("/me", response_model=WorkerResponse, summary="Get my worker profile")
def get_my_profile(
    current_user: User = Depends(require_worker_role),
    worker_service: WorkerService = Depends(get_worker_service)
) -> Any:
    """
    Get the worker profile of the authenticated user.
    """
    try:
        return worker_service.get_my_profile(current_user.id)
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.patch("/me", response_model=WorkerResponse, summary="Update my worker profile")
def update_my_profile(
    request: WorkerUpdate,
    current_user: User = Depends(require_worker_role),
    worker_service: WorkerService = Depends(get_worker_service)
) -> Any:
    """
    Update the worker profile of the authenticated user.
    """
    try:
        return worker_service.update_my_profile(current_user.id, request)
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
