import itertools
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import main
from main import app, db


@pytest.fixture(autouse=True)
def reset_state():
    db.clear()
    main._id_seq = itertools.count(start=1)
    yield
    db.clear()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
class TestCreateUser:
    async def test_create_returns_201(self, client, faker):
        resp = await client.post("/users", json={"username": faker.user_name(), "age": faker.random_int(18, 80)})
        assert resp.status_code == 201

    async def test_create_response_structure(self, client, faker):
        username = faker.user_name()
        age = faker.random_int(18, 60)
        resp = await client.post("/users", json={"username": username, "age": age})
        data = resp.json()
        assert "id" in data
        assert data["username"] == username
        assert data["age"] == age


@pytest.mark.asyncio
class TestGetUser:
    async def test_get_existing(self, client, faker):
        created = (await client.post("/users", json={"username": faker.user_name(), "age": 25})).json()
        resp = await client.get(f"/users/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    async def test_get_missing_returns_404(self, client):
        resp = await client.get("/users/99999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User not found"


@pytest.mark.asyncio
class TestDeleteUser:
    async def test_delete_existing(self, client, faker):
        created = (await client.post("/users", json={"username": faker.user_name(), "age": 30})).json()
        resp = await client.delete(f"/users/{created['id']}")
        assert resp.status_code == 204

    async def test_delete_missing_returns_404(self, client):
        resp = await client.delete("/users/99999")
        assert resp.status_code == 404

    async def test_get_after_delete_returns_404(self, client, faker):
        created = (await client.post("/users", json={"username": faker.user_name(), "age": 27})).json()
        await client.delete(f"/users/{created['id']}")
        resp = await client.get(f"/users/{created['id']}")
        assert resp.status_code == 404
