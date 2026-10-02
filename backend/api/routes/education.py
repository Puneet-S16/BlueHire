import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from models.user import User
from models.enums import RoleEnum
from schemas.education import EducationCreate, EducationUpdate, EducationResponse
from repositories.education_repository import EducationRepository
from repositories.worker_repository import WorkerRepository
from services.education_service import EducationService
from core.exceptions import EducationNotFoundError, InvalidEducationOwnershipError, WorkerNotFoundError, InvalidWorkerRoleError

from api.routes.auth import get_current_user

router = APIRouter()

def get_education_service(db: Session = Depends(get_db)) -> EducationService:
    return EducationService(
        EducationRepository(db),
        WorkerRepository(db)
    )

def require_worker_role(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.WORKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only users with the WORKER role can access this endpoint"
        )
    return current_user

@router.get("/me", response_model=List[EducationResponse], summary="Get my education history")
def get_my_education(
    current_user: User = Depends(require_worker_role),
    education_service: EducationService = Depends(get_education_service)
) -> Any:
    try:
        return education_service.get_my_education(current_user)
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("", response_model=EducationResponse, status_code=status.HTTP_201_CREATED, summary="Add education entry")
def create_education(
    request: EducationCreate,
    current_user: User = Depends(require_worker_role),
    education_service: EducationService = Depends(get_education_service)
) -> Any:
    try:
        return education_service.create_education(current_user, request)
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.patch("/{education_id}", response_model=EducationResponse, summary="Update education entry")
def update_education(
    education_id: uuid.UUID,
    request: EducationUpdate,
    current_user: User = Depends(require_worker_role),
    education_service: EducationService = Depends(get_education_service)
) -> Any:
    try:
        return education_service.update_education(current_user, education_id, request)
    except EducationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidEducationOwnershipError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

@router.delete("/{education_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete education entry")
def delete_education(
    education_id: uuid.UUID,
    current_user: User = Depends(require_worker_role),
    education_service: EducationService = Depends(get_education_service)
) -> Any:
    try:
        education_service.delete_education(current_user, education_id)
    except EducationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidEducationOwnershipError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
