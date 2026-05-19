import pytest


def test_create_task_success(client):
    """Test successful task creation."""
    response = client.post(
        "/tasks",
        json={
            "title": "Подготовить тесты",
            "description": "Написать интеграционные тесты для основных сценариев",
            "status": "todo",
            "priority": 4,
        },
        headers={"X-User-Id": "10"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Подготовить тесты"
    assert data["owner_id"] == 10


def test_create_task_short_title(client):
    """Test that short title returns 422."""
    response = client.post(
        "/tasks",
        json={
            "title": "ab",
            "status": "todo",
            "priority": 1,
        },
        headers={"X-User-Id": "10"},
    )
    assert response.status_code == 422


def test_create_task_missing_header(client):
    """Test that missing X-User-Id returns 401."""
    response = client.post(
        "/tasks",
        json={
            "title": "Test task",
            "status": "todo",
            "priority": 1,
        },
    )
    assert response.status_code == 401


def test_user_sees_only_own_tasks(client):
    """Test that users only see their own tasks."""
    client.post(
        "/tasks",
        json={"title": "Task from user 10", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10"},
    )

    client.post(
        "/tasks",
        json={"title": "Task from user 20", "status": "todo", "priority": 1},
        headers={"X-User-Id": "20"},
    )

    response = client.get("/tasks", headers={"X-User-Id": "10"})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Task from user 10"


def test_filter_by_status(client):
    """Test filtering tasks by status."""
    client.post(
        "/tasks",
        json={"title": "Task 1", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10"},
    )
    client.post(
        "/tasks",
        json={"title": "Task 2", "status": "done", "priority": 1},
        headers={"X-User-Id": "10"},
    )

    response = client.get("/tasks?status=done", headers={"X-User-Id": "10"})
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "done"


def test_filter_by_min_priority(client):
    """Test filtering tasks by minimum priority."""
    client.post(
        "/tasks",
        json={"title": "Task 1", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10"},
    )
    client.post(
        "/tasks",
        json={"title": "Task 2", "status": "todo", "priority": 3},
        headers={"X-User-Id": "10"},
    )

    response = client.get("/tasks?min_priority=2", headers={"X-User-Id": "10"})
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["priority"] == 3


def test_update_task_status(client):
    """Test successful task status update."""
    create_response = client.post(
        "/tasks",
        json={"title": "Test task", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10"},
    )
    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "done"},
        headers={"X-User-Id": "10"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"


def test_get_nonexistent_task(client):
    """Test that getting nonexistent task returns 404."""
    response = client.get("/tasks/999", headers={"X-User-Id": "10"})
    assert response.status_code == 404


def test_delete_task_success(client):
    """Test successful task deletion."""
    create_response = client.post(
        "/tasks",
        json={"title": "Test task", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10"},
    )
    task_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert response.status_code == 204

    response = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert response.status_code == 404


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "env" in data
