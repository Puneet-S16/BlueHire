from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from models.user import User
from models.enums import RoleEnum
from schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from repositories.category_repository import CategoryRepository
from services.category_service import CategoryService
from core.exceptions import CategoryAlreadyExistsError, CategoryNotFoundError

from api.routes.auth import get_current_user

router = APIRouter()

def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(CategoryRepository(db))

def require_admin_role(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only admins can access this endpoint"
        )
    return current_user

# Public endpoints
@router.get("", response_model=List[CategoryResponse], summary="List all categories")
def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category_service: CategoryService = Depends(get_category_service)
) -> Any:
    return category_service.list_categories(skip=skip, limit=limit)

@router.get("/{category_id}", response_model=CategoryResponse, summary="Get category details")
def get_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service)
) -> Any:
    try:
        return category_service.get_category(category_id)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# Protected (ADMIN) endpoints
@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, summary="Create a new category")
def create_category(
    request: CategoryCreate,
    current_user: User = Depends(require_admin_role),
    category_service: CategoryService = Depends(get_category_service)
) -> Any:
    try:
        return category_service.create_category(request)
    except CategoryAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.patch("/{category_id}", response_model=CategoryResponse, summary="Update a category")
def update_category(
    category_id: int,
    request: CategoryUpdate,
    current_user: User = Depends(require_admin_role),
    category_service: CategoryService = Depends(get_category_service)
) -> Any:
    try:
        return category_service.update_category(category_id, request)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CategoryAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a category")
def delete_category(
    category_id: int,
    current_user: User = Depends(require_admin_role),
    category_service: CategoryService = Depends(get_category_service)
) -> Any:
    try:
        category_service.delete_category(category_id)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
