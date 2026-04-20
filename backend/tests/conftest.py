import sys
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings
from src.core.security import hash_password
from src.database import Base, get_db
from src.main import app
from src.models import *  # noqa: F401, F403 — ensure all models are imported

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Fixture file paths
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

# Test database URL — uses a separate test database
TEST_DATABASE_URL = settings.database_url.replace(
    "/legalanalyzer", "/legalanalyzer_test"
)

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a test database session."""
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def async_client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP client for testing."""

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def create_user(test_db: AsyncSession):
    """Factory fixture to create a test user."""
    from src.models.user import User

    async def _create_user(email: str, password: str) -> User:
        user = User(
            email=email,
            password_hash=hash_password(password),
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    return _create_user


@pytest_asyncio.fixture
async def auth_headers(async_client: AsyncClient, create_user):
    """Factory fixture returning auth headers for a user."""

    async def _auth_headers(email: str, password: str) -> dict:
        await create_user(email, password)
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _auth_headers


@pytest.fixture
def sample_txt_path() -> Path:
    """Path to the sample employment offer letter (plain text)."""
    return FIXTURES_DIR / "sample_employment.txt"


@pytest.fixture
def sample_pdf_path() -> Path:
    """Path to the sample NDA (placeholder PDF)."""
    return FIXTURES_DIR / "sample_nda.pdf"


@pytest.fixture
def sample_docx_path() -> Path:
    """Path to the sample contract (placeholder DOCX)."""
    return FIXTURES_DIR / "sample_contract.docx"
