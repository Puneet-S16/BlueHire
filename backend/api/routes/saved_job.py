import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from models.user import User
from schemas.saved_job import SavedJobResponse, SavedJobListResponse
from repositories.saved_job_repository import SavedJobRepository
from repositories.worker_repository import WorkerRepository
from repositories.job_repository import JobRepository
from services.saved_job_service import SavedJobService
from core.exceptions import (
    SavedJobAlreadyExistsError,
    SavedJobNotFoundError,
    InvalidWorkerRoleError,
    WorkerNotFoundError,
    JobNotFoundError,
    JobNotOpenError
)

from api.routes.auth import get_current_user

router = APIRouter()

def get_saved_job_service(db: Session = Depends(get_db)) -> SavedJobService:
    return SavedJobService(
        SavedJobRepository(db),
        WorkerRepository(db),
        JobRepository(db)
    )

@router.get("/me", response_model=SavedJobListResponse, summary="Get my saved jobs")
def get_my_saved_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    saved_job_service: SavedJobService = Depends(get_saved_job_service)
) -> Any:
    try:
        total, results = saved_job_service.get_saved_jobs(current_user, page, page_size)
        return SavedJobListResponse(
            total=total,
            page=page,
            page_size=page_size,
            results=results
        )
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{job_id}", response_model=SavedJobResponse, status_code=status.HTTP_201_CREATED, summary="Save a job")
def save_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    saved_job_service: SavedJobService = Depends(get_saved_job_service)
) -> Any:
    try:
        return saved_job_service.save_job(current_user, job_id)
    except (InvalidWorkerRoleError, JobNotOpenError) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except (WorkerNotFoundError, JobNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SavedJobAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Unsave a job")
def unsave_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    saved_job_service: SavedJobService = Depends(get_saved_job_service)
) -> Any:
    try:
        saved_job_service.unsave_job(current_user, job_id)
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except (WorkerNotFoundError, SavedJobNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
