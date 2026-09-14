import uuid
from typing import List
from schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from repositories.company_repository import CompanyRepository
from core.exceptions import CompanyAlreadyExistsError, CompanyNotFoundError

class CompanyService:
    def __init__(self, company_repo: CompanyRepository):
        self.company_repo = company_repo

    def create_company(self, data: CompanyCreate) -> CompanyResponse:
        existing = self.company_repo.get_by_name(data.name)
        if existing:
            raise CompanyAlreadyExistsError(f"Company with name '{data.name}' already exists.")
        
        company = self.company_repo.create_company(data)
        return CompanyResponse.model_validate(company)

    def get_company(self, company_id: uuid.UUID) -> CompanyResponse:
        company = self.company_repo.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundError(f"Company with id {company_id} not found.")
        return CompanyResponse.model_validate(company)

    def list_companies(self, skip: int = 0, limit: int = 100) -> List[CompanyResponse]:
        companies = self.company_repo.list_companies(skip=skip, limit=limit)
        return [CompanyResponse.model_validate(c) for c in companies]

    def update_company(self, company_id: uuid.UUID, data: CompanyUpdate) -> CompanyResponse:
        company = self.company_repo.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundError(f"Company with id {company_id} not found.")
        
        if data.name and data.name != company.name:
            existing = self.company_repo.get_by_name(data.name)
            if existing:
                raise CompanyAlreadyExistsError(f"Company with name '{data.name}' already exists.")
                
        updated_company = self.company_repo.update_company(company, data)
        return CompanyResponse.model_validate(updated_company)
