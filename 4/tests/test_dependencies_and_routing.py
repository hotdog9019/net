import pytest


def test_get_current_user_me(client):
    """Test /users/me returns current user."""
    response = client.get(
        "/users/me",
        headers={"X-User-Id": "10", "X-User-Role": "user"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 10
    assert data["role"] == "user"


def test_missing_x_user_id_returns_401(client):
    """Test that missing X-User-Id returns 401."""
    response = client.get("/users/me")
    assert response.status_code == 401


def test_admin_access_to_stats(client):
    """Test that admin can access /admin/stats."""
    # Create a task
    client.post(
        "/tasks",
        json={"title": "Test task", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10", "X-User-Role": "admin"},
    )
    
    # Get stats
    response = client.get(
        "/admin/stats",
        headers={"X-User-Id": "10", "X-User-Role": "admin"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 1
    assert data["by_status"]["todo"] == 1


def test_user_cannot_access_stats(client):
    """Test that regular user gets 403 for /admin/stats."""
    response = client.get(
        "/admin/stats",
        headers={"X-User-Id": "10", "X-User-Role": "user"},
    )
    assert response.status_code == 403


def test_user_cannot_delete_other_user_task(client):
    """Test that user cannot delete another user's task."""
    # User 10 creates task
    create_response = client.post(
        "/tasks",
        json={"title": "User 10 task", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10", "X-User-Role": "user"},
    )
    task_id = create_response.json()["id"]
    
    # User 20 tries to delete it
    response = client.delete(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "20", "X-User-Role": "user"},
    )
    assert response.status_code == 404


def test_admin_can_delete_other_user_task(client):
    """Test that admin can delete any task."""
    # User 10 creates task
    create_response = client.post(
        "/tasks",
        json={"title": "User 10 task", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10", "X-User-Role": "user"},
    )
    task_id = create_response.json()["id"]
    
    # Admin deletes it
    response = client.delete(
        f"/admin/tasks/{task_id}",
        headers={"X-User-Id": "20", "X-User-Role": "admin"},
    )
    assert response.status_code == 204
    
    # Verify it's deleted
    response = client.get(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "10", "X-User-Role": "user"},
    )
    assert response.status_code == 404


def test_swagger_tags_grouping(client):
    """Test that Swagger groups routes by tags."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    
    # Check tags exist
    tags = {tag["name"] for tag in spec.get("tags", [])}
    assert "tasks" in tags
    assert "users" in tags
    assert "admin" in tags


def test_admin_stats_with_multiple_statuses(client):
    """Test admin stats with tasks in different statuses."""
    admin_headers = {"X-User-Id": "10", "X-User-Role": "admin"}
    
    # Create tasks with different statuses
    client.post(
        "/tasks",
        json={"title": "Task 1", "status": "todo", "priority": 1},
        headers=admin_headers,
    )
    client.post(
        "/tasks",
        json={"title": "Task 2", "status": "todo", "priority": 1},
        headers=admin_headers,
    )
    client.post(
        "/tasks",
        json={"title": "Task 3", "status": "in_progress", "priority": 1},
        headers=admin_headers,
    )
    client.post(
        "/tasks",
        json={"title": "Task 4", "status": "done", "priority": 1},
        headers=admin_headers,
    )
    client.post(
        "/tasks",
        json={"title": "Task 5", "status": "done", "priority": 1},
        headers=admin_headers,
    )
    
    # Get stats
    response = client.get("/admin/stats", headers=admin_headers)
    data = response.json()
    
    assert data["total_tasks"] == 5
    assert data["by_status"]["todo"] == 2
    assert data["by_status"]["in_progress"] == 1
    assert data["by_status"]["done"] == 2


def test_create_and_retrieve_task(client):
    """Test full task lifecycle."""
    headers = {"X-User-Id": "10", "X-User-Role": "user"}
    
    # Create task
    create_response = client.post(
        "/tasks",
        json={
            "title": "Complete project",
            "description": "Finish FAPI_KR5",
            "status": "in_progress",
            "priority": 5,
        },
        headers=headers,
    )
    assert create_response.status_code == 201
    task = create_response.json()
    task_id = task["id"]
    
    # Get task
    get_response = client.get(f"/tasks/{task_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Complete project"
    
    # Update status
    update_response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "done"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "done"
    
    # Delete task
    delete_response = client.delete(f"/tasks/{task_id}", headers=headers)
    assert delete_response.status_code == 204


def test_get_user_info(client):
    """Test getting user information."""
    response = client.get(
        "/users/42",
        headers={"X-User-Id": "10", "X-User-Role": "user"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 42
    assert data["role"] == "user"


def test_default_role_is_user(client):
    """Test that default role is 'user' if not provided."""
    response = client.get(
        "/users/me",
        headers={"X-User-Id": "10"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "user"
