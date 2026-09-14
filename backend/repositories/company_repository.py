import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from models.company import Company
from schemas.company import CompanyCreate, CompanyUpdate

class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, company_id: uuid.UUID) -> Optional[Company]:
        return self.db.execute(select(Company).where(Company.id == company_id)).scalar_one_or_none()

    def get_by_name(self, name: str) -> Optional[Company]:
        return self.db.execute(select(Company).where(Company.name == name)).scalar_one_or_none()

    def create_company(self, company_data: CompanyCreate) -> Company:
        company = Company(**company_data.model_dump())
        self.db.add(company)
        try:
            self.db.commit()
            self.db.refresh(company)
        except IntegrityError:
            self.db.rollback()
            raise
        return company

    def update_company(self, company: Company, update_data: CompanyUpdate) -> Company:
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(company, key, value)
        try:
            self.db.commit()
            self.db.refresh(company)
        except IntegrityError:
            self.db.rollback()
            raise
        return company

    def delete_company(self, company: Company) -> None:
        self.db.delete(company)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise

    def list_companies(self, skip: int = 0, limit: int = 100) -> List[Company]:
        return list(self.db.execute(select(Company).offset(skip).limit(limit)).scalars().all())
