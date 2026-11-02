"""
Authentication test suite.

All tests run against an isolated test database (``bluehire_test``). The
development/production database is never touched. Each test runs inside a
rolled-back transaction for isolation.

Coverage:
- Signup (success, duplicate, invalid email, weak password, missing terms)
- Login (valid, wrong password, unknown email, inactive user)
- Email enumeration resistance (same error for unknown email and wrong password)
- Refresh token rotation (valid, invalid, revoked, reuse detection)
- Refresh token reuse (rotate then reuse old token → reject + revoke all)
- Logout (revokes token, idempotent on invalid token)
- Password change (revokes all sessions, rejects wrong current password)
- Protected route (get_me with/without token)
- Rate limiting on login/signup
"""

import os
import uuid
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient  # noqa: F401  (used via fixture)

from conftest import TEST_DATABASE_URL  # noqa: E402

VALID_PASSWORD = "StrongPassword123!"
WEAK_PASSWORD = "weak"


def _signup_payload(client, email, password=VALID_PASSWORD, role="WORKER"):
    return client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "password": password,
            "confirm_password": password,
            "role": role,
            "accept_terms": True,
        },
    )


def _login(client, email, password):
    return client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )


def _tokens(client, email, password=VALID_PASSWORD):
    r = _login(client, email, password)
    assert r.status_code == 200, f"login failed: {r.text}"
    return r.json()


class TestSignup:
    def test_signup_success(self, client: TestClient):
        email = f"signup_{uuid.uuid4().hex}@example.com"
        r = _signup_payload(client, email)
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["email"] == email
        assert body["role"] == "WORKER"
        assert "password_hash" not in body

    def test_signup_duplicate_email(self, client: TestClient):
        email = f"dup_{uuid.uuid4().hex}@example.com"
        _signup_payload(client, email)
        r = _signup_payload(client, email)
        assert r.status_code == 409, r.text

    def test_signup_invalid_email(self, client: TestClient):
        r = _signup_payload(client, "not-an-email")
        assert r.status_code == 422, r.text

    def test_signup_weak_password(self, client: TestClient):
        r = _signup_payload(client, f"weak_{uuid.uuid4().hex}@example.com", password=WEAK_PASSWORD)
        assert r.status_code == 422, r.text

    def test_signup_password_mismatch(self, client: TestClient):
        email = f"mismatch_{uuid.uuid4().hex}@example.com"
        r = client.post(
            "/api/v1/auth/signup",
            json={
                "email": email,
                "password": VALID_PASSWORD,
                "confirm_password": "Different123!",
                "role": "WORKER",
                "accept_terms": True,
            },
        )
        assert r.status_code == 422, r.text

    def test_signup_terms_not_accepted(self, client: TestClient):
        email = f"terms_{uuid.uuid4().hex}@example.com"
        r = client.post(
            "/api/v1/auth/signup",
            json={
                "email": email,
                "password": VALID_PASSWORD,
                "confirm_password": VALID_PASSWORD,
                "role": "WORKER",
                "accept_terms": False,
            },
        )
        assert r.status_code == 422, r.text


class TestLogin:
    def test_login_valid(self, client: TestClient):
        email = f"login_{uuid.uuid4().hex}@example.com"
        _signup_payload(client, email)
        r = _login(client, email, VALID_PASSWORD)
        assert r.status_code == 200, r.text
        body = r.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"
        assert body["expires_in"] > 0

    def test_login_wrong_password(self, client: TestClient):
        email = f"wrongpwd_{uuid.uuid4().hex}@example.com"
        _signup_payload(client, email)
        r = _login(client, email, "WrongPassword123!")
        assert r.status_code == 401, r.text

    def test_login_unknown_email(self, client: TestClient):
        r = _login(client, f"nonexistent_{uuid.uuid4().hex}@example.com", VALID_PASSWORD)
        assert r.status_code == 401, r.text

    def test_login_inactive_user(self, client: TestClient):
        from models.user import User
        from core.security import hash_password
        from models.enums import RoleEnum
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        email = f"inactive_{uuid.uuid4().hex}@example.com"
        # Create the inactive user via a standalone session committed to the
        # database so the API (which uses its own db_session) can see it.
        engine = create_engine(TEST_DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        user = User(
            email=email,
            password_hash=hash_password(VALID_PASSWORD),
            role=RoleEnum.WORKER,
            is_active=False,
        )
        session.add(user)
        session.commit()
        session.close()
        engine.dispose()

        r = _login(client, email, VALID_PASSWORD)
        assert r.status_code == 403, r.text

    def test_email_enumeration_resistance(self, client: TestClient):
        # Unknown email and wrong password must return the same status/message.
        r_unknown = _login(client, f"nope_{uuid.uuid4().hex}@example.com", VALID_PASSWORD)
        assert r_unknown.status_code == 401

        email = f"enum_{uuid.uuid4().hex}@example.com"
        _signup_payload(client, email)
        r_wrong = _login(client, email, "WrongPassword123!")
        assert r_wrong.status_code == 401
        assert r_unknown.json()["detail"] == r_wrong.json()["detail"]


class TestRefresh:
    def test_refresh_valid_rotation(self, client: TestClient):
        email = f"rotate_{uuid.uuid4().hex}@example.com"
        _signup_payload(client, email)
        tokens = _tokens(client, email)
        old_refresh = tokens["refresh_token"]

        r = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": old_refresh},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        new_access = body["access_token"]
        new_refresh = body["refresh_token"]
        # Rotation must issue different tokens.
        assert new_access != tokens["access_token"]
        assert new_refresh != old_refresh

        # Old refresh token must now be rejected.
        r2 = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": old_refresh},
        )
        assert r2.status_code == 401, r2.text

    def test_refresh_invalid_token(self, client: TestClient):
        r = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "not.a.real.token"},
        )
        assert r.status_code == 401, r.text

    def test_refresh_wrong_token_type(self, client: TestClient):
        email = f"type_{uuid.uuid4().hex}@example.com"
        _signup_payload(client, email)
        tokens = _tokens(client, email)
        # Using an access token as a refresh token must be rejected.
        r = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["access_token"]},
        )
        assert r.status_code == 401, r.text

    def test_refresh_reuse_revokes_all_sessions(self, client: TestClient):
        """Rotate, then reuse the old token → rejected and all sessions revoked."""
        email = f"reuse_{uuid.uuid4().hex}@example.com"
        _signup_payload(client, email)
        tokens = _tokens(client, email)
        original_refresh = tokens["refresh_token"]

        # First rotation succeeds.
        r1 = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": original_refresh},
        )
        assert r1.status_code == 200, r1.text
        rotated = r1.json()

        # Reuse the ORIGINAL (now revoked) token → must be rejected.
        r2 = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": original_refresh},
        )
        assert r2.status_code == 401, r2.text

        # The rotated refresh token should also now be unusable for the
        # original session (all sessions revoked due to reuse).
        r3 = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": rotated["refresh_token"]},
        )
        assert r3.status_code == 401, r3.text

    def test_refresh_expired_token(self, client: TestClient):
        """An already-expired refresh token must be rejected."""
        from core.security import create_refresh_token

        email = f"expired_{uuid.uuid4().hex}@example.com"
        _signup_payload(client, email)
        # Create a refresh token that is already expired.
        expired_token = create_refresh_token(
            uuid.uuid4(), expires_delta=timedelta(days=-1)
        )
        r = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": expired_token},
        )
        assert r.status_code == 401, r.text


class TestLogout:
    def test_logout_revokes_token(self, client: TestClient):
        email = f"logout_{uuid.uuid4().hex}@example.com"
        _signup_payload(client, email)
        tokens = _tokens(client, email)

        r = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert r.status_code == 200, r.text

        # Refresh token is now revoked.
        r2 = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert r2.status_code == 401, r2.text

    def test_logout_idempotent_invalid_token(self, client: TestClient):
        # Logging out with an invalid token still returns success (no leak).
        r = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": "invalid.token.here"},
        )
        assert r.status_code == 200, r.text


class TestChangePassword:
    def test_change_password_revokes_sessions(self, client: TestClient):
        email = f"chpwd_{uuid.uuid4().hex}@example.com"
        _signup_payload(client, email)
        tokens = _tokens(client, email)
        refresh_before = tokens["refresh_token"]

        r = client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "current_password": VALID_PASSWORD,
                "new_password": "NewStrongPassword123!",
                "confirm_password": "NewStrongPassword123!",
            },
        )
        assert r.status_code == 200, r.text

        # Old refresh token must be revoked.
        r2 = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_before},
        )
        assert r2.status_code == 401, r2.text

    def test_change_password_wrong_current(self, client: TestClient):
        email = f"chpwd2_{uuid.uuid4().hex}@example.com"
        _signup_payload(client, email)
        tokens = _tokens(client, email)

        r = client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewStrongPassword123!",
                "confirm_password": "NewStrongPassword123!",
            },
        )
        assert r.status_code == 401, r.text

    def test_change_password_weak_new(self, client: TestClient):
        email = f"chpwd3_{uuid.uuid4().hex}@example.com"
        _signup_payload(client, email)
        tokens = _tokens(client, email)

        r = client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "current_password": VALID_PASSWORD,
                "new_password": "weak",
                "confirm_password": "weak",
            },
        )
        assert r.status_code == 422, r.text


class TestProtectedRoutes:
    def test_get_me_valid(self, client: TestClient):
        email = f"me_{uuid.uuid4().hex}@example.com"
        _signup_payload(client, email)
        tokens = _tokens(client, email)

        r = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert r.status_code == 200, r.text
        assert r.json()["email"] == email

    def test_get_me_no_token(self, client: TestClient):
        r = client.get("/api/v1/auth/me")
        assert r.status_code == 401, r.text

    def test_get_me_invalid_token(self, client: TestClient):
        r = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert r.status_code == 401, r.text


class TestRateLimiting:
    def test_login_rate_limited(self, client: TestClient):
        email = f"ratelimit_{uuid.uuid4().hex}@example.com"
        _signup_payload(client, email)

        # Make more than 5 login attempts rapidly; the 6th should be 429.
        statuses = []
        for i in range(6):
            r = _login(client, email, "WrongPassword" + str(i))
            statuses.append(r.status_code)
        assert 429 in statuses, f"Expected a 429, got {statuses}"

    def test_signup_rate_limited(self, client: TestClient):
        # Make more than 5 signup attempts rapidly; expect a 429.
        statuses = []
        for i in range(6):
            r = client.post(
                "/api/v1/auth/signup",
                json={
                    "email": f"rl_signup_{i}_{uuid.uuid4().hex}@example.com",
                    "password": VALID_PASSWORD,
                    "confirm_password": VALID_PASSWORD,
                    "role": "WORKER",
                    "accept_terms": True,
                },
            )
            statuses.append(r.status_code)
        assert 429 in statuses, f"Expected a 429, got {statuses}"


class TestDatabaseIsolation:
    """Safety tests proving tests never target dev/prod databases."""

    def test_database_url_resolves_to_bluehire_test(self):
        """TEST_DATABASE_URL must always point at the dedicated test DB."""
        from urllib.parse import urlparse

        parsed = urlparse(TEST_DATABASE_URL)
        assert parsed.path.lstrip("/") == "bluehire_test"
        assert "bluehire_test" in TEST_DATABASE_URL
        assert parsed.path.lstrip("/") != "bluehire", "Must not point at dev DB 'bluehire'"

    def test_postgres_db_env_is_forced(self):
        """conftest forces POSTGRES_DB=bluehire_test regardless of pre-set env."""
        assert os.environ.get("POSTGRES_DB") == "bluehire_test"
