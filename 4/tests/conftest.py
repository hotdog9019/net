import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import reset_storage


@pytest.fixture
def client():
    """Create a test client and reset storage."""
    reset_storage()
    return TestClient(app)
