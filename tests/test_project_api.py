from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.api.routes.projects import get_project_service
from app.main import app
from app.models.project import Project, ProjectStatus


class FakeProjectService:
    def create_project(self, data):
        now = datetime.now(UTC)

        return Project(
            id=1,
            name=data.name,
            idea=data.idea,
            status=ProjectStatus.DRAFT,
            created_at=now,
            updated_at=now,
        )


@pytest.fixture
def client():
    app.dependency_overrides[get_project_service] = (
        lambda: FakeProjectService()
    )

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(
        get_project_service,
        None,
    )


def test_create_project(client):
    response = client.post(
        "/projects/",
        json={
            "name": "AI Architect",
            "idea": "An AI system that turns product ideas into technical plans.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "AI Architect"
    assert data["idea"] == (
        "An AI system that turns product ideas into technical plans."
    )
    assert data["status"] == "DRAFT"
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_create_project_missing_name(client):
    response = client.post(
        "/projects/",
        json={
            "idea": "An AI system.",
        },
    )

    assert response.status_code == 422


def test_create_project_missing_idea(client):
    response = client.post(
        "/projects/",
        json={
            "name": "AI Architect",
        },
    )

    assert response.status_code == 422