import pytest
from fastapi.testclient import TestClient

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app, db, _id_seq, _id_lock
import itertools

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    db.clear()
    # reset id sequence
    global _id_seq
    import main
    main._id_seq = itertools.count(start=1)
    yield
    db.clear()


class TestCreateUser:
    def test_create_returns_201(self):
        resp = client.post("/users", json={"username": "alice", "age": 25})
        assert resp.status_code == 201

    def test_create_response_structure(self):
        resp = client.post("/users", json={"username": "bob", "age": 30})
        data = resp.json()
        assert "id" in data
        assert data["username"] == "bob"
        assert data["age"] == 30


class TestGetUser:
    def test_get_existing_user(self):
        created = client.post("/users", json={"username": "carol", "age": 22}).json()
        resp = client.get(f"/users/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["username"] == "carol"

    def test_get_missing_user_returns_404(self):
        resp = client.get("/users/9999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User not found"


class TestDeleteUser:
    def test_delete_existing_user(self):
        created = client.post("/users", json={"username": "dave", "age": 28}).json()
        resp = client.delete(f"/users/{created['id']}")
        assert resp.status_code == 204

    def test_delete_missing_user_returns_404(self):
        resp = client.delete("/users/9999")
        assert resp.status_code == 404

    def test_get_after_delete_returns_404(self):
        created = client.post("/users", json={"username": "eve", "age": 35}).json()
        client.delete(f"/users/{created['id']}")
        resp = client.get(f"/users/{created['id']}")
        assert resp.status_code == 404
