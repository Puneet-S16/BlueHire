import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from models.user import User
from models.enums import RoleEnum
from schemas.skill import SkillCreate, SkillUpdate, SkillResponse, WorkerSkillResponse
from repositories.skill_repository import SkillRepository, WorkerSkillRepository
from repositories.worker_repository import WorkerRepository
from repositories.category_repository import CategoryRepository
from services.skill_service import SkillService
from core.exceptions import (
    SkillAlreadyExistsError,
    SkillNotFoundError,
    WorkerSkillAlreadyExistsError,
    WorkerSkillNotFoundError,
    WorkerNotFoundError,
    InvalidWorkerRoleError,
    CategoryNotFoundError
)

from api.routes.auth import get_current_user

router = APIRouter()

def get_skill_service(db: Session = Depends(get_db)) -> SkillService:
    return SkillService(
        SkillRepository(db),
        WorkerSkillRepository(db),
        WorkerRepository(db),
        CategoryRepository(db)
    )

def require_worker_role(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.WORKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only workers can access this endpoint"
        )
    return current_user

def require_admin_role(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only admins can access this endpoint"
        )
    return current_user

# Public endpoints
@router.get("", response_model=List[SkillResponse], summary="List all skills")
def list_skills(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    skill_service: SkillService = Depends(get_skill_service)
) -> Any:
    return skill_service.list_skills(skip=skip, limit=limit)

# Protected (WORKER) endpoints
@router.get("/me", response_model=List[WorkerSkillResponse], summary="Get my skills")
def get_my_skills(
    current_user: User = Depends(require_worker_role),
    skill_service: SkillService = Depends(get_skill_service)
) -> Any:
    try:
        return skill_service.get_my_skills(current_user)
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/me/{skill_id}", response_model=WorkerSkillResponse, status_code=status.HTTP_201_CREATED, summary="Add skill to my profile")
def assign_skill(
    skill_id: int,
    current_user: User = Depends(require_worker_role),
    skill_service: SkillService = Depends(get_skill_service)
) -> Any:
    try:
        return skill_service.assign_skill_to_worker(current_user, skill_id)
    except SkillNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except WorkerSkillAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/me/{skill_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove skill from my profile")
def remove_skill(
    skill_id: int,
    current_user: User = Depends(require_worker_role),
    skill_service: SkillService = Depends(get_skill_service)
) -> Any:
    try:
        skill_service.remove_skill_from_worker(current_user, skill_id)
    except WorkerSkillNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{skill_id}", response_model=SkillResponse, summary="Get skill details")
def get_skill(
    skill_id: int,
    skill_service: SkillService = Depends(get_skill_service)
) -> Any:
    try:
        return skill_service.get_skill(skill_id)
    except SkillNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# Protected (ADMIN) endpoints
@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED, summary="Create a new skill")
def create_skill(
    request: SkillCreate,
    current_user: User = Depends(require_admin_role),
    skill_service: SkillService = Depends(get_skill_service)
) -> Any:
    try:
        return skill_service.create_skill(request)
    except SkillAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.patch("/{skill_id}", response_model=SkillResponse, summary="Update a skill")
def update_skill(
    skill_id: int,
    request: SkillUpdate,
    current_user: User = Depends(require_admin_role),
    skill_service: SkillService = Depends(get_skill_service)
) -> Any:
    try:
        return skill_service.update_skill(skill_id, request)
    except SkillNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SkillAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a skill")
def delete_skill(
    skill_id: int,
    current_user: User = Depends(require_admin_role),
    skill_service: SkillService = Depends(get_skill_service)
) -> Any:
    try:
        skill_service.delete_skill(skill_id)
    except SkillNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
