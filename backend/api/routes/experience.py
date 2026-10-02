import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from models.user import User
from models.enums import RoleEnum
from schemas.experience import ExperienceCreate, ExperienceUpdate, ExperienceResponse
from repositories.experience_repository import ExperienceRepository
from repositories.worker_repository import WorkerRepository
from services.experience_service import ExperienceService
from core.exceptions import ExperienceNotFoundError, InvalidExperienceOwnershipError, WorkerNotFoundError, InvalidWorkerRoleError

from api.routes.auth import get_current_user

router = APIRouter()

def get_experience_service(db: Session = Depends(get_db)) -> ExperienceService:
    return ExperienceService(
        ExperienceRepository(db),
        WorkerRepository(db)
    )

def require_worker_role(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.WORKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only users with the WORKER role can access this endpoint"
        )
    return current_user

@router.get("/me", response_model=List[ExperienceResponse], summary="Get my work experience")
def get_my_experience(
    current_user: User = Depends(require_worker_role),
    experience_service: ExperienceService = Depends(get_experience_service)
) -> Any:
    try:
        return experience_service.get_my_experience(current_user)
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED, summary="Add work experience entry")
def create_experience(
    request: ExperienceCreate,
    current_user: User = Depends(require_worker_role),
    experience_service: ExperienceService = Depends(get_experience_service)
) -> Any:
    try:
        return experience_service.create_experience(current_user, request)
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.patch("/{experience_id}", response_model=ExperienceResponse, summary="Update work experience entry")
def update_experience(
    experience_id: uuid.UUID,
    request: ExperienceUpdate,
    current_user: User = Depends(require_worker_role),
    experience_service: ExperienceService = Depends(get_experience_service)
) -> Any:
    try:
        return experience_service.update_experience(current_user, experience_id, request)
    except ExperienceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidExperienceOwnershipError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete work experience entry")
def delete_experience(
    experience_id: uuid.UUID,
    current_user: User = Depends(require_worker_role),
    experience_service: ExperienceService = Depends(get_experience_service)
) -> Any:
    try:
        experience_service.delete_experience(current_user, experience_id)
    except ExperienceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidExperienceOwnershipError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
