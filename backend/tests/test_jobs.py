"""
Integration tests for the jobs module.

Covers job creation, listing, retrieval, updates, deletion, authorization
boundaries (employer vs worker vs public), input validation, and error
responses. All tests run against the isolated ``bluehire_test`` database.
"""

import uuid

from fastapi.testclient import TestClient
from models.enums import JobStatusEnum, RoleEnum
from sqlalchemy.orm import Session
from tests.helpers import (
    auth_headers,
    create_category,
    create_company,
    create_job,
    setup_employer,
    setup_worker,
)


class TestJobCreate:
    def test_employer_can_create_job(self, client: TestClient, db_session: Session):
        _, company, category, token = setup_employer(db_session, client)

        r = client.post(
            "/api/v1/jobs/",
            json={
                "category_id": category.id,
                "title": "Plumber Needed",
                "description": "Looking for an experienced plumber",
                "job_type": "FULL_TIME",
                "vacancies": 2,
                "pay_type": "HOURLY",
                "pay_min": 25.00,
                "pay_max": 35.00,
            },
            headers=auth_headers(token),
        )
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["title"] == "Plumber Needed"
        assert body["company_id"] == str(company.id)
        assert body["status"] == "DRAFT"

    def test_worker_cannot_create_job(self, client: TestClient, db_session: Session):
        _, token = setup_worker(db_session, client)
        category = create_category(db_session)

        r = client.post(
            "/api/v1/jobs/",
            json={
                "category_id": category.id,
                "title": "Fake Job",
                "description": "Should not be allowed",
                "job_type": "FULL_TIME",
                "vacancies": 1,
                "pay_type": "HOURLY",
                "pay_min": 10.00,
                "pay_max": 20.00,
            },
            headers=auth_headers(token),
        )
        assert r.status_code == 403, r.text

    def test_unauthenticated_cannot_create_job(self, client: TestClient, db_session: Session):
        category = create_category(db_session)

        r = client.post(
            "/api/v1/jobs/",
            json={
                "category_id": category.id,
                "title": "No Auth Job",
                "description": "Should not be allowed",
                "job_type": "FULL_TIME",
                "vacancies": 1,
                "pay_type": "HOURLY",
                "pay_min": 10.00,
                "pay_max": 20.00,
            },
        )
        assert r.status_code == 401, r.text

    def test_create_job_invalid_pay_range(self, client: TestClient, db_session: Session):
        _, company, category, token = setup_employer(db_session, client)

        r = client.post(
            "/api/v1/jobs/",
            json={
                "category_id": category.id,
                "title": "Bad Pay Job",
                "description": "Pay min greater than max",
                "job_type": "FULL_TIME",
                "vacancies": 1,
                "pay_type": "HOURLY",
                "pay_min": 50.00,
                "pay_max": 30.00,
            },
            headers=auth_headers(token),
        )
        assert r.status_code == 422, r.text

    def test_create_job_missing_required_fields(self, client: TestClient, db_session: Session):
        _, company, category, token = setup_employer(db_session, client)

        r = client.post(
            "/api/v1/jobs/",
            json={
                "title": "Incomplete Job",
            },
            headers=auth_headers(token),
        )
        assert r.status_code == 422, r.text


class TestJobListAndGet:
    def test_public_can_list_jobs(self, client: TestClient, db_session: Session):
        _, company, category, _ = setup_employer(db_session, client)
        create_job(db_session, company, category, title="Job One")
        create_job(db_session, company, category, title="Job Two")

        r = client.get("/api/v1/jobs/")
        assert r.status_code == 200, r.text
        body = r.json()
        assert len(body) >= 2

    def test_public_can_get_job(self, client: TestClient, db_session: Session):
        _, company, category, _ = setup_employer(db_session, client)
        job = create_job(db_session, company, category, title="Retrievable Job")

        r = client.get(f"/api/v1/jobs/{job.id}")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["title"] == "Retrievable Job"
        assert body["id"] == str(job.id)

    def test_get_nonexistent_job(self, client: TestClient, db_session: Session):
        fake_id = uuid.uuid4()
        r = client.get(f"/api/v1/jobs/{fake_id}")
        assert r.status_code == 404, r.text


class TestJobUpdate:
    def test_employer_can_update_own_job(self, client: TestClient, db_session: Session):
        _, company, category, token = setup_employer(db_session, client)
        job = create_job(db_session, company, category, title="Original Title")

        r = client.patch(
            f"/api/v1/jobs/{job.id}",
            json={"title": "Updated Title", "pay_max": 40.00},
            headers=auth_headers(token),
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["title"] == "Updated Title"
        assert body["pay_max"] == 40.00

    def test_employer_cannot_update_another_employers_job(
        self, client: TestClient, db_session: Session
    ):
        _, owner_company, category, _ = setup_employer(db_session, client)
        job = create_job(db_session, owner_company, category, title="Owner Job")

        _, _, _, attacker_token = setup_employer(db_session, client)

        r = client.patch(
            f"/api/v1/jobs/{job.id}",
            json={"title": "Hacked Title"},
            headers=auth_headers(attacker_token),
        )
        assert r.status_code == 403, r.text

    def test_worker_cannot_update_job(self, client: TestClient, db_session: Session):
        _, company, category, _ = setup_employer(db_session, client)
        job = create_job(db_session, company, category, title="Job")

        _, worker_token = setup_worker(db_session, client)

        r = client.patch(
            f"/api/v1/jobs/{job.id}",
            json={"title": "Worker Edit"},
            headers=auth_headers(worker_token),
        )
        assert r.status_code == 403, r.text

    def test_update_nonexistent_job(self, client: TestClient, db_session: Session):
        _, _, _, token = setup_employer(db_session, client)

        fake_id = uuid.uuid4()
        r = client.patch(
            f"/api/v1/jobs/{fake_id}",
            json={"title": "Nope"},
            headers=auth_headers(token),
        )
        assert r.status_code == 404, r.text


class TestJobDelete:
    def test_employer_can_delete_own_job(self, client: TestClient, db_session: Session):
        _, company, category, token = setup_employer(db_session, client)
        job = create_job(db_session, company, category, title="To Be Deleted")

        r = client.delete(f"/api/v1/jobs/{job.id}", headers=auth_headers(token))
        assert r.status_code == 204, r.text

        r2 = client.get(f"/api/v1/jobs/{job.id}")
        assert r2.status_code == 404, r2.text

    def test_employer_cannot_delete_another_employers_job(
        self, client: TestClient, db_session: Session
    ):
        _, owner_company, category, _ = setup_employer(db_session, client)
        job = create_job(db_session, owner_company, category, title="Owner Job")

        _, _, _, attacker_token = setup_employer(db_session, client)

        r = client.delete(f"/api/v1/jobs/{job.id}", headers=auth_headers(attacker_token))
        assert r.status_code == 403, r.text

    def test_worker_cannot_delete_job(self, client: TestClient, db_session: Session):
        _, company, category, _ = setup_employer(db_session, client)
        job = create_job(db_session, company, category, title="Job")

        _, worker_token = setup_worker(db_session, client)

        r = client.delete(f"/api/v1/jobs/{job.id}", headers=auth_headers(worker_token))
        assert r.status_code == 403, r.text
