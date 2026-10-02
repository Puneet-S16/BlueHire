import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.employer import Employer

class EmployerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Employer]:
        return self.db.query(Employer).filter(Employer.user_id == user_id).first()

    def get_by_company_id(self, company_id: uuid.UUID) -> Optional[Employer]:
        return self.db.query(Employer).filter(Employer.company_id == company_id).first()

    def list_employers_by_company(self, company_id: uuid.UUID) -> List[Employer]:
        return self.db.query(Employer).filter(Employer.company_id == company_id).all()

    def create_employer(self, employer: Employer) -> Employer:
        try:
            self.db.add(employer)
            self.db.commit()
            self.db.refresh(employer)
            return employer
        except Exception:
            self.db.rollback()
            raise

    def update_employer(self, employer: Employer) -> Employer:
        try:
            self.db.commit()
            self.db.refresh(employer)
            return employer
        except Exception:
            self.db.rollback()
            raise

    def delete_employer(self, employer: Employer) -> None:
        try:
            self.db.delete(employer)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
