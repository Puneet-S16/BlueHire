"""
Reusable test helpers for backend integration tests.

Users are created via the API signup endpoint (the proven working code path)
rather than direct DB inserts, to avoid session/transaction isolation issues
between the test fixture and API dependency override. Companies, categories,
jobs and other non-user entities are created directly via the database
session.

The ``db_session`` fixture rolls back the enclosing transaction after each
test, preserving isolation.
"""

import uuid
from typing import Optional

from core.security import create_access_token, hash_password
from fastapi.testclient import TestClient
from models.company import Company
from models.employer import Employer
from models.enums import JobStatusEnum, JobTypeEnum, PayTypeEnum, RoleEnum
from models.job import Job
from models.skill import Category
from models.worker import Worker
from sqlalchemy.orm import Session


def create_user_via_api(
    client: TestClient,
    email: str | None = None,
    role: RoleEnum = RoleEnum.WORKER,
    password: str = "StrongPassword123!",
) -> dict:
    """Create a user via the API signup endpoint and return the response body.

    This is the preferred method for user creation because it exercises the
    same code path as production and avoids transaction isolation issues
    between direct DB inserts and the API's get_db dependency override.
    """
    if email is None:
        email = f"user_{uuid.uuid4().hex}@example.com"
    r = client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "password": password,
            "confirm_password": password,
            "role": role.value,
            "accept_terms": True,
        },
    )
    assert r.status_code == 201, f"Signup failed: {r.text}"
    return r.json()


def create_user_direct(
    db: Session,
    email: str | None = None,
    role: RoleEnum = RoleEnum.WORKER,
    is_active: bool = True,
    password: str = "StrongPassword123!",
) -> object:
    """Create and commit a user directly in the DB session.

    Use this only when the user will not need to authenticate via the API
    in the same test (e.g., for creating employer/worker profiles where the
    user is referenced by ID only).
    """
    if email is None:
        email = f"user_{uuid.uuid4().hex}@example.com"
    from models.user import User

    user = User(
        email=email,
        password_hash=hash_password(password),
        role=role,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_company(db: Session, name: str | None = None) -> Company:
    """Create and commit a company."""
    if name is None:
        name = f"Test Company {uuid.uuid4().hex[:8]}"
    company = Company(
        name=name,
        industry="Construction",
        city="Test City",
        state="TS",
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def create_employer_profile(
    db: Session, user_id: uuid.UUID, company: Company | None = None
) -> Employer:
    """Create and commit an employer profile linked to a company and user ID."""
    if company is None:
        company = create_company(db)
    employer = Employer(
        user_id=user_id,
        company_id=company.id,
        first_name="Employer",
        last_name="User",
        job_title="Hiring Manager",
    )
    db.add(employer)
    db.commit()
    db.refresh(employer)
    return employer


def create_worker_profile(db: Session, user_id: uuid.UUID) -> Worker:
    """Create and commit a worker profile linked to a user ID."""
    worker = Worker(
        user_id=user_id,
        first_name="Worker",
        last_name="User",
        phone_number=f"+1555{uuid.uuid4().hex[:7]}",
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker


def create_category(db: Session, name: str | None = None) -> Category:
    """Create and commit a job category."""
    if name is None:
        name = f"Category {uuid.uuid4().hex[:8]}"
    category = Category(name=name, description="Test category")
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def create_job(
    db: Session,
    company: Company,
    category: Category,
    title: str | None = None,
    status: JobStatusEnum = JobStatusEnum.ACTIVE,
    posted_by_id: uuid.UUID | None = None,
) -> Job:
    """Create and commit a job posting."""
    if title is None:
        title = f"Test Job {uuid.uuid4().hex[:8]}"
    job = Job(
        company_id=company.id,
        posted_by_id=posted_by_id,
        category_id=category.id,
        title=title,
        description="A test job description",
        job_type=JobTypeEnum.FULL_TIME,
        vacancies=1,
        status=status,
        pay_type=PayTypeEnum.HOURLY,
        pay_min=20.00,
        pay_max=30.00,
        city="Test City",
        state="TS",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def auth_headers(token: str) -> dict:
    """Return Bearer authorization headers for a JWT token."""
    return {"Authorization": f"Bearer {token}"}


def make_access_token(user_id: uuid.UUID) -> str:
    """Create a short-lived access token for a user ID."""
    return create_access_token(user_id)


def setup_employer(db: Session, client: TestClient) -> tuple:
    """Create an employer user via API, plus company, employer profile, and category.

    Returns (user_dict, company, category, token).
    """
    user = create_user_via_api(client, role=RoleEnum.EMPLOYER)
    company = create_company(db)
    create_employer_profile(db, uuid.UUID(user["id"]), company)
    category = create_category(db)
    token = make_access_token(uuid.UUID(user["id"]))
    return user, company, category, token


def setup_worker(db: Session, client: TestClient) -> tuple:
    """Create a worker user via API, plus worker profile.

    Returns (user_dict, token).
    """
    user = create_user_via_api(client, role=RoleEnum.WORKER)
    create_worker_profile(db, uuid.UUID(user["id"]))
    token = make_access_token(uuid.UUID(user["id"]))
    return user, token
