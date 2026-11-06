
# tests/conftest.py

import subprocess
import time
import logging
from typing import Generator, Dict, List
from contextlib import contextmanager

import pytest
import requests
from faker import Faker
from playwright.sync_api import sync_playwright, Browser
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base, get_engine, get_sessionmaker
from app.models.user import User
from app.config import settings
from app.database_init import init_db, drop_db


# ==========================================================
# Logging Configuration
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ==========================================================
# Database Configuration
# ==========================================================

fake = Faker()
Faker.seed(12345)

logger.info("Using configured test database")

test_engine = get_engine(database_url=settings.DATABASE_URL)
TestingSessionLocal = get_sessionmaker(engine=test_engine)


# ==========================================================
# Helper Functions
# ==========================================================

def create_fake_user() -> Dict[str, str]:
    """Generate fake user data for testing."""

    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.unique.email(),
        "username": fake.unique.user_name(),
        "password": fake.password(length=12)
    }


@contextmanager
def managed_db_session():
    """Manage database sessions safely."""

    session = TestingSessionLocal()

    try:
        yield session

    except SQLAlchemyError as error:
        logger.error("Database error: %s", error)
        session.rollback()
        raise

    finally:
        session.close()


# ==========================================================
# Server Startup / Health Check
# ==========================================================

def wait_for_server(url: str, timeout: int = 30) -> bool:
    """Wait until the FastAPI server becomes available."""

    start_time = time.monotonic()

    while time.monotonic() - start_time < timeout:

        try:
            response = requests.get(url, timeout=2)

            if response.status_code == 200:
                return True

        except requests.exceptions.RequestException:
            pass

        time.sleep(1)

    return False


class ServerStartupError(Exception):
    """Raised when the FastAPI server cannot start."""


# ==========================================================
# Primary Database Fixtures
# ==========================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_database(request):
    """Initialize and clean up the test database."""

    logger.info("Setting up test database...")

    Base.metadata.drop_all(bind=test_engine)
    logger.info("Dropped existing tables.")

    Base.metadata.create_all(bind=test_engine)
    logger.info("Created database tables.")

    init_db()
    logger.info("Database initialized.")

    yield

    preserve_db = request.config.getoption("--preserve-db")

    if preserve_db:
        logger.info("Preserving test database.")
    else:
        logger.info("Cleaning up test database...")
        drop_db()
        logger.info("Database cleanup completed.")


@pytest.fixture
def db_session(request) -> Generator[Session, None, None]:
    """Provide a database session for each test."""

    session = TestingSessionLocal()

    try:
        yield session

    finally:
        preserve_db = request.config.getoption("--preserve-db")

        try:
            if not preserve_db:

                for table in reversed(Base.metadata.sorted_tables):
                    logger.info("Cleaning table: %s", table.name)
                    session.execute(table.delete())

                session.commit()

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()


# ==========================================================
# Test Data Fixtures
# ==========================================================

@pytest.fixture
def fake_user_data() -> Dict[str, str]:
    """Provide fake user information."""

    return create_fake_user()


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create one test user."""

    user_data = create_fake_user()

    user = User(**user_data)

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    logger.info("Created test user with ID: %s", user.id)

    return user


@pytest.fixture
def seed_users(db_session: Session, request) -> List[User]:
    """Create multiple test users."""

    try:
        num_users = request.param

    except AttributeError:
        num_users = 5

    users = []

    for _ in range(num_users):

        user_data = create_fake_user()

        user = User(**user_data)

        db_session.add(user)
        users.append(user)

    db_session.commit()

    logger.info("Created %s test users.", len(users))

    return users


# ==========================================================
# FastAPI Server Fixture
# ==========================================================

@pytest.fixture(scope="session")
def fastapi_server():
    """Start and stop FastAPI for end-to-end tests."""

    server_url = "http://127.0.0.1:8000/"

    logger.info("Starting FastAPI test server...")

    process = subprocess.Popen(
        ["python", "main.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT
    )

    try:

        if not wait_for_server(server_url, timeout=30):
            raise ServerStartupError(
                "FastAPI server failed to start within 30 seconds."
            )

        logger.info("FastAPI test server is ready.")

        yield

    finally:

        logger.info("Stopping FastAPI test server...")

        if process.poll() is None:

            process.terminate()

            try:
                process.wait(timeout=5)
                logger.info("FastAPI server stopped.")

            except subprocess.TimeoutExpired:
                logger.warning("Force stopping FastAPI server.")
                process.kill()
                process.wait()


# ==========================================================
# Playwright Browser Fixtures
# ==========================================================

@pytest.fixture(scope="session")
def browser_context():
    """Launch Chromium for E2E testing."""

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        logger.info("Chromium browser launched.")

        try:
            yield browser

        finally:
            logger.info("Closing Chromium browser.")
            browser.close()


@pytest.fixture
def page(browser_context: Browser):
    """Create a fresh browser page for each test."""

    context = browser_context.new_context(
        viewport={
            "width": 1920,
            "height": 1080
        },
        ignore_https_errors=True
    )

    browser_page = context.new_page()

    browser_page.set_default_timeout(10000)
    browser_page.set_default_navigation_timeout(15000)

    logger.info("Created new browser page.")

    try:
        yield browser_page

    finally:
        logger.info("Closing browser page.")
        browser_page.close()
        context.close()


# ==========================================================
# Pytest Command-Line Options
# ==========================================================

def pytest_addoption(parser):
    """Register custom pytest options."""

    parser.addoption(
        "--preserve-db",
        action="store_true",
        default=False,
        help="Preserve the test database after testing."
    )

    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run tests marked as slow."
    )


def pytest_collection_modifyitems(config, items):
    """Skip slow tests unless explicitly requested."""

    if not config.getoption("--run-slow"):

        skip_slow = pytest.mark.skip(
            reason="Use --run-slow to run this test."
        )

        for item in items:

            if "slow" in item.keywords:
                item.add_marker(skip_slow)
