import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.core.config import settings

# Create test database engine using PostgreSQL _test DB
TEST_SQLALCHEMY_DATABASE_URL = str(settings.SQLALCHEMY_DATABASE_URL).replace(
    settings.POSTGRES_DB,  # Replace the database name
    f"{settings.POSTGRES_DB}_test"  # Add _test suffix
)

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    # Create test database tables
    Base.metadata.create_all(bind=engine)
    yield engine
    # Clean up after all tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client 