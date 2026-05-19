import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.room_manager import room_manager


@pytest.fixture
def client():
    """Create a test client and reset room manager."""
    # Reset room manager
    room_manager.rooms = {}
    return TestClient(app)
