import pytest

from app.main import app


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_list_tasks(client):
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
    assert len(response.get_json()) >= 1


def test_get_single_task(client):
    response = client.get("/api/tasks/1")
    assert response.status_code == 200
    assert response.get_json()["id"] == 1


def test_get_unknown_task_returns_404(client):
    response = client.get("/api/tasks/9999")
    assert response.status_code == 404


def test_create_task(client):
    response = client.post("/api/tasks", json={"title": "Nouvelle tâche"})
    assert response.status_code == 201
    assert response.get_json()["title"] == "Nouvelle tâche"
    assert response.get_json()["done"] is False


def test_create_task_without_title_returns_400(client):
    response = client.post("/api/tasks", json={})
    assert response.status_code == 400
