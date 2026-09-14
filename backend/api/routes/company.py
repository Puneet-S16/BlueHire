import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import SessionLocal, get_db
from repositories.company_repository import CompanyRepository
from services.company_service import CompanyService
from schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from core.exceptions import CompanyAlreadyExistsError, CompanyNotFoundError

from api.routes.auth import get_current_user
from models.user import User

router = APIRouter()

def get_company_repository(db: Session = Depends(get_db)) -> CompanyRepository:
    return CompanyRepository(db)

def get_company_service(company_repo: CompanyRepository = Depends(get_company_repository)) -> CompanyService:
    return CompanyService(company_repo)

@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED, summary="Create a new company")
def create_company(
    request: CompanyCreate,
    company_service: CompanyService = Depends(get_company_service),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new company. Requires authentication.
    """
    try:
        return company_service.create_company(request)
    except CompanyAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("", response_model=List[CompanyResponse], summary="List companies")
def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    company_service: CompanyService = Depends(get_company_service)
) -> Any:
    """
    List companies with pagination.
    """
    return company_service.list_companies(skip=skip, limit=limit)

@router.get("/{company_id}", response_model=CompanyResponse, summary="Get company by ID")
def get_company(
    company_id: uuid.UUID,
    company_service: CompanyService = Depends(get_company_service)
) -> Any:
    """
    Get a specific company by its UUID.
    """
    try:
        return company_service.get_company(company_id)
    except CompanyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.patch("/{company_id}", response_model=CompanyResponse, summary="Update company")
def update_company(
    company_id: uuid.UUID,
    request: CompanyUpdate,
    company_service: CompanyService = Depends(get_company_service),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update a company's details. Requires authentication.
    """
    try:
        return company_service.update_company(company_id, request)
    except CompanyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CompanyAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
