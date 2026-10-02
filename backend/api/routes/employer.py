from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from models.user import User
from models.enums import RoleEnum
from schemas.employer import EmployerCreate, EmployerUpdate, EmployerResponse
from repositories.employer_repository import EmployerRepository
from repositories.company_repository import CompanyRepository
from services.employer_service import EmployerService
from core.exceptions import EmployerAlreadyExistsError, EmployerNotFoundError, InvalidEmployerRoleError, CompanyNotFoundError

from api.routes.auth import get_current_user

router = APIRouter()

def get_employer_service(db: Session = Depends(get_db)) -> EmployerService:
    employer_repo = EmployerRepository(db)
    company_repo = CompanyRepository(db)
    return EmployerService(employer_repo, company_repo)

def require_employer_role(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.EMPLOYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only users with the EMPLOYER role can access this endpoint"
        )
    return current_user

@router.post("/me", response_model=EmployerResponse, status_code=status.HTTP_201_CREATED, summary="Create my employer profile")
def create_employer_profile(
    request: EmployerCreate,
    current_user: User = Depends(require_employer_role),
    employer_service: EmployerService = Depends(get_employer_service)
) -> Any:
    """
    Create an employer profile for the authenticated user.
    """
    try:
        return employer_service.create_employer_profile(current_user, request)
    except InvalidEmployerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except EmployerAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except CompanyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/me", response_model=EmployerResponse, summary="Get my employer profile")
def get_my_profile(
    current_user: User = Depends(require_employer_role),
    employer_service: EmployerService = Depends(get_employer_service)
) -> Any:
    """
    Get the employer profile of the authenticated user.
    """
    try:
        return employer_service.get_my_profile(current_user.id)
    except EmployerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.patch("/me", response_model=EmployerResponse, summary="Update my employer profile")
def update_my_profile(
    request: EmployerUpdate,
    current_user: User = Depends(require_employer_role),
    employer_service: EmployerService = Depends(get_employer_service)
) -> Any:
    """
    Update the employer profile of the authenticated user.
    """
    try:
        return employer_service.update_my_profile(current_user.id, request)
    except EmployerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CompanyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
