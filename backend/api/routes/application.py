import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from models.user import User
from models.enums import RoleEnum
from schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from repositories.application_repository import ApplicationRepository
from repositories.worker_repository import WorkerRepository
from repositories.employer_repository import EmployerRepository
from repositories.job_repository import JobRepository
from services.application_service import ApplicationService
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

from api.routes.auth import get_current_user

router = APIRouter()

def get_application_service(db: Session = Depends(get_db)) -> ApplicationService:
    return ApplicationService(
        ApplicationRepository(db),
        WorkerRepository(db),
        EmployerRepository(db),
        JobRepository(db)
    )

def require_worker_role(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.WORKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only workers can access this endpoint"
        )
    return current_user

def require_employer_role(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.EMPLOYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only employers can access this endpoint"
        )
    return current_user

@router.post("/jobs/{job_id}", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED, summary="Apply to a job")
def apply_to_job(
    job_id: uuid.UUID,
    request: ApplicationCreate,
    current_user: User = Depends(require_worker_role),
    application_service: ApplicationService = Depends(get_application_service)
) -> Any:
    """
    Apply to a specific job. Requires WORKER role.
    """
    try:
        return application_service.apply_to_job(current_user, job_id, request)
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except JobNotOpenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ApplicationAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("/me", response_model=List[ApplicationResponse], summary="Get my applications")
def get_my_applications(
    current_user: User = Depends(require_worker_role),
    application_service: ApplicationService = Depends(get_application_service)
) -> Any:
    """
    List applications submitted by the current worker. Requires WORKER role.
    """
    try:
        return application_service.get_my_applications(current_user)
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/jobs/{job_id}", response_model=List[ApplicationResponse], summary="Get applications for a job")
def get_job_applications(
    job_id: uuid.UUID,
    current_user: User = Depends(require_employer_role),
    application_service: ApplicationService = Depends(get_application_service)
) -> Any:
    """
    List applications for a specific job. Requires EMPLOYER role.
    """
    try:
        return application_service.get_job_applications(current_user, job_id)
    except InvalidEmployerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except EmployerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidApplicationOwnershipError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.patch("/{application_id}", response_model=ApplicationResponse, summary="Update an application")
def update_application(
    application_id: uuid.UUID,
    request: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service)
) -> Any:
    """
    Update an application. Employers update status, workers update cover_letter.
    """
    try:
        return application_service.update_application_status(current_user, application_id, request)
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except EmployerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidApplicationOwnershipError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Withdraw an application")
def withdraw_application(
    application_id: uuid.UUID,
    current_user: User = Depends(require_worker_role),
    application_service: ApplicationService = Depends(get_application_service)
) -> Any:
    """
    Withdraw an application. Requires WORKER role.
    """
    try:
        application_service.withdraw_application(current_user, application_id)
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidApplicationOwnershipError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
