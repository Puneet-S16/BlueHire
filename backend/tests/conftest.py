"""
Isolated authentication test configuration.

Tests run against a dedicated test database (``bluehire_test``), never
against the development or production database. Each test runs inside a
transaction that is rolled back afterward, so tests are isolated and the
schema is created/dropped once per session.
"""

import os
import sys

# SECRET_KEY must be set before importing the app, because core.config
# validates it at import time (rejects the "CHANGE_ME" placeholder).
os.environ["SECRET_KEY"] = "test-secret-key-that-is-at-least-32-chars-long!!"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_PASSWORD"] = "postgres"
os.environ["POSTGRES_SERVER"] = "localhost"
# Force the test database name. Override any pre-existing POSTGRES_DB so tests
# can never accidentally target the development or production database.
os.environ["POSTGRES_DB"] = "bluehire_test"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402
from core.rate_limit import limiter  # noqa: E402
from db.session import get_db  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402
from models import Base  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

TEST_DATABASE_NAME = "bluehire_test"
TEST_DATABASE_URL = (
    f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
    f"@{os.environ['POSTGRES_SERVER']}/{TEST_DATABASE_NAME}"
)


def _assert_test_database_isolation() -> None:
    """Refuse to run tests against any database other than bluehire_test.

    This is a safety guard: if the application configuration resolves to a
    database name other than the dedicated test database, abort before any
    schema is created or any data is touched.
    """
    import urllib.parse as urlparse

    parsed = urlparse.urlparse(TEST_DATABASE_URL)
    actual_db = (parsed.path or "").lstrip("/")
    if actual_db != TEST_DATABASE_NAME:
        raise RuntimeError(
            f"Test database isolation violated: resolved database "
            f"'{actual_db}' is not the dedicated test database "
            f"'{TEST_DATABASE_NAME}'. Refusing to run tests against a "
            f"non-test database."
        )


_assert_test_database_isolation()

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables once per test session, drop them at the end."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session():
    """
    Provide a transactional SQLAlchemy session for a single test.

    All changes are rolled back after the test completes, keeping tests
    isolated without mutating the shared test schema.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    """
    Provide a FastAPI TestClient whose get_db dependency uses the test
    session. Dependency overrides are cleared after the test.
    """

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset slowapi's in-memory hit counters before each test so rate
    limiting in one test does not bleed into another."""
    try:
        storage = limiter._storage
        reset = getattr(storage, "reset", None)
        if callable(reset):
            reset()
        else:
            hits = getattr(storage, "storage", None)
            if hits is not None:
                hits.clear()
    except AttributeError:
        pass
    yield
