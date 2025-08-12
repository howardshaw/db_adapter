import asyncio
import os
import tempfile
from typing import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import get_settings
from container import Container
from infras.repositories.base_po import BasePO
from main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings():
    """Get test settings."""
    # Override settings for testing
    os.environ["USE_ASYNC_DB"] = "false"
    os.environ["REPO_DRIVER"] = "sync_db"
    os.environ["USE_ASYNC_ROUTER"] = "false"
    os.environ["DB_URL_SYNC"] = "sqlite:///:memory:"
    os.environ["ECHO"] = "false"
    os.environ["POOL_SIZE"] = "5"
    os.environ["MAX_OVERFLOW"] = "2"
    os.environ["POOL_RECYCLE"] = "1800"
    os.environ["POOL_TIMEOUT"] = "5"

    return get_settings()


@pytest.fixture(scope="session")
def test_engine(test_settings):
    """Create test database engine."""
    engine = create_engine(
        test_settings.DB_URL_SYNC,
        echo=test_settings.ECHO,
        pool_size=test_settings.POOL_SIZE,
        max_overflow=test_settings.MAX_OVERFLOW,
        pool_recycle=test_settings.POOL_RECYCLE,
        pool_timeout=test_settings.POOL_TIMEOUT,
    )

    # Create tables
    BasePO.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    BasePO.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def test_session(test_engine):
    """Create test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def test_container(test_settings):
    """Create test container."""
    container = Container()
    container.config.from_dict({
        "USE_ASYNC_DB": test_settings.USE_ASYNC_DB,
        "REPO_DRIVER": test_settings.REPO_DRIVER,
        "USE_ASYNC_ROUTER": test_settings.USE_ASYNC_ROUTER,
        "DB_URL_SYNC": test_settings.DB_URL_SYNC,
        "DB_URL_ASYNC": test_settings.DB_URL_ASYNC,
        "ECHO": test_settings.ECHO,
        "POOL_SIZE": test_settings.POOL_SIZE,
        "MAX_OVERFLOW": test_settings.MAX_OVERFLOW,
        "POOL_RECYCLE": test_settings.POOL_RECYCLE,
        "POOL_TIMEOUT": test_settings.POOL_TIMEOUT,
    })

    return container


@pytest.fixture
def test_client(test_container) -> Generator[TestClient, None, None]:
    """Create test client."""
    app.container = test_container
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_async_service():
    """Create mock async service."""
    mock_service = AsyncMock()
    mock_service.list.return_value = []
    mock_service.get.return_value = None
    mock_service.create.return_value = None
    mock_service.update.return_value = None
    mock_service.delete.return_value = False
    return mock_service


@pytest.fixture
def mock_sync_service():
    """Create mock sync service."""
    mock_service = MagicMock()
    mock_service.list.return_value = []
    mock_service.get.return_value = None
    mock_service.create.return_value = None
    mock_service.update.return_value = None
    mock_service.delete.return_value = False
    return mock_service


@pytest.fixture
def sample_item_data():
    """Sample item data for testing."""
    return {
        "name": "Test Item",
        "description": "A test item for testing purposes",
        "price": 99.99,
        "category": "test"
    }


@pytest.fixture
def sample_items_data():
    """Sample items data for testing."""
    return [
        {
            "name": "Item 1",
            "description": "First test item",
            "price": 10.99,
            "category": "electronics"
        },
        {
            "name": "Item 2",
            "description": "Second test item",
            "price": 25.50,
            "category": "books"
        },
        {
            "name": "Item 3",
            "description": "Third test item",
            "price": 5.99,
            "category": "food"
        }
    ]


@pytest.fixture
def temp_db_file():
    """Create temporary database file."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    yield db_path

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


# Markers for different test types
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )
    config.addinivalue_line(
        "markers", "async_test: mark test as async"
    )
