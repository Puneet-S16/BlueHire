import uuid
from typing import Optional
from models.user import User
from models.employer import Employer
from models.enums import RoleEnum
from schemas.employer import EmployerCreate, EmployerUpdate
from repositories.employer_repository import EmployerRepository
from repositories.company_repository import CompanyRepository
from core.exceptions import EmployerAlreadyExistsError, EmployerNotFoundError, InvalidEmployerRoleError, CompanyNotFoundError

class EmployerService:
    def __init__(self, employer_repo: EmployerRepository, company_repo: CompanyRepository):
        self.employer_repo = employer_repo
        self.company_repo = company_repo

    def create_employer_profile(self, user: User, request: EmployerCreate) -> Employer:
        if user.role != RoleEnum.EMPLOYER:
            raise InvalidEmployerRoleError("Only users with EMPLOYER role can create an employer profile")

        existing_employer = self.employer_repo.get_by_user_id(user.id)
        if existing_employer:
            raise EmployerAlreadyExistsError("User already has an employer profile")

        if request.company_id:
            company = self.company_repo.get_by_id(request.company_id)
            if not company:
                raise CompanyNotFoundError("Referenced company does not exist")

        employer = Employer(
            user_id=user.id,
            company_id=request.company_id,
            first_name=request.first_name,
            last_name=request.last_name,
            job_title=request.job_title,
            phone_number=request.phone_number
        )
        return self.employer_repo.create_employer(employer)

    def get_my_profile(self, user_id: uuid.UUID) -> Employer:
        employer = self.employer_repo.get_by_user_id(user_id)
        if not employer:
            raise EmployerNotFoundError("Employer profile not found")
        return employer

    def update_my_profile(self, user_id: uuid.UUID, request: EmployerUpdate) -> Employer:
        employer = self.employer_repo.get_by_user_id(user_id)
        if not employer:
            raise EmployerNotFoundError("Employer profile not found")

        update_data = request.model_dump(exclude_unset=True)
        if "company_id" in update_data and update_data["company_id"] is not None:
            company = self.company_repo.get_by_id(update_data["company_id"])
            if not company:
                raise CompanyNotFoundError("Referenced company does not exist")

        for key, value in update_data.items():
            setattr(employer, key, value)
            
        return self.employer_repo.update_employer(employer)
