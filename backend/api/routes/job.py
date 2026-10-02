import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from models.user import User
from models.enums import RoleEnum
from schemas.job import JobCreate, JobUpdate, JobResponse
from repositories.job_repository import JobRepository
from repositories.employer_repository import EmployerRepository
from services.job_service import JobService
from core.exceptions import JobNotFoundError, InvalidJobOwnershipError, EmployerNotFoundError, InvalidEmployerRoleError

from api.routes.auth import get_current_user

router = APIRouter()

def get_job_service(db: Session = Depends(get_db)) -> JobService:
    job_repo = JobRepository(db)
    employer_repo = EmployerRepository(db)
    return JobService(job_repo, employer_repo)

def require_employer_role(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.EMPLOYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only users with the EMPLOYER role can access this endpoint"
        )
    return current_user

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED, summary="Create a new job")
def create_job(
    request: JobCreate,
    current_user: User = Depends(require_employer_role),
    job_service: JobService = Depends(get_job_service)
) -> Any:
    """
    Create a new job posting. Requires EMPLOYER role.
    """
    try:
        return job_service.create_job(current_user, request)
    except InvalidEmployerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except EmployerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidJobOwnershipError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.get("", response_model=List[JobResponse], summary="List jobs")
def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    job_service: JobService = Depends(get_job_service)
) -> Any:
    """
    List all jobs. Public endpoint.
    """
    return job_service.list_jobs(skip=skip, limit=limit)

@router.get("/{job_id}", response_model=JobResponse, summary="Get job details")
def get_job(
    job_id: uuid.UUID,
    job_service: JobService = Depends(get_job_service)
) -> Any:
    """
    Get details of a specific job. Public endpoint.
    """
    try:
        return job_service.get_job(job_id)
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.patch("/{job_id}", response_model=JobResponse, summary="Update a job")
def update_job(
    job_id: uuid.UUID,
    request: JobUpdate,
    current_user: User = Depends(require_employer_role),
    job_service: JobService = Depends(get_job_service)
) -> Any:
    """
    Update an existing job posting. Requires EMPLOYER role.
    """
    try:
        return job_service.update_job(current_user, job_id, request)
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidEmployerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except EmployerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidJobOwnershipError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a job")
def delete_job(
    job_id: uuid.UUID,
    current_user: User = Depends(require_employer_role),
    job_service: JobService = Depends(get_job_service)
) -> Any:
    """
    Delete an existing job posting. Requires EMPLOYER role.
    """
    try:
        job_service.delete_job(current_user, job_id)
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidEmployerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except EmployerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidJobOwnershipError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
