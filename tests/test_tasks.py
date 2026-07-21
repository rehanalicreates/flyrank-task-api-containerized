"""
Test suite for the Task API.

Covers the two things the assignment explicitly asks for:
  1. Error handling (404 on missing tasks, 400 on invalid input)
  2. Different responses with different status codes (200, 201, 204, 400, 404)

NOTE: these are now integration tests — they run against a real Postgres
database, not an in-memory store. Postgres must be running first:
    docker compose up -d db

Run with:
    pytest -v
"""

import pytest
from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app
from app.repository import task_repository


@pytest.fixture(autouse=True)
def reset_repository():
    """Ensure each test starts with a clean, empty tasks table."""
    init_db()
    task_repository.clear()
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint(client):
    """GET / returns API metadata."""
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Task API"
    assert body["version"] == "2.0"
    assert "/tasks" in body["endpoints"]


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_task_returns_201(client):
    response = client.post("/tasks", json={"title": "Write tests"})
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Write tests"
    assert body["completed"] is False
    assert "id" in body
    assert "created_at" in body


def test_create_task_missing_title_returns_400(client):
    response = client.post("/tasks", json={"description": "no title given"})
    assert response.status_code == 400
    body = response.json()
    assert "Title is required" in body["message"]


def test_create_task_empty_title_returns_400(client):
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 400
    body = response.json()
    assert "Title is required" in body["message"]


def test_list_tasks_empty_returns_200_and_empty_array(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_returns_created_tasks(client):
    client.post("/tasks", json={"title": "Task A"})
    client.post("/tasks", json={"title": "Task B"})
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_task_returns_200(client):
    created = client.post("/tasks", json={"title": "Find me"}).json()
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Find me"


def test_get_nonexistent_task_returns_404(client):
    response = client.get("/tasks/9999")
    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "task_not_found"


def test_update_task_returns_200_and_updated_fields(client):
    created = client.post("/tasks", json={"title": "Original"}).json()
    response = client.put(f"/tasks/{created['id']}", json={"completed": True})
    assert response.status_code == 200
    body = response.json()
    assert body["completed"] is True
    assert body["title"] == "Original"  # untouched field stays the same


def test_update_nonexistent_task_returns_404(client):
    response = client.put("/tasks/9999", json={"title": "Ghost"})
    assert response.status_code == 404


def test_delete_task_returns_204(client):
    created = client.post("/tasks", json={"title": "Delete me"}).json()
    response = client.delete(f"/tasks/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""

    # confirm it's actually gone
    follow_up = client.get(f"/tasks/{created['id']}")
    assert follow_up.status_code == 404


def test_delete_nonexistent_task_returns_404(client):
    response = client.delete("/tasks/9999")
    assert response.status_code == 404
