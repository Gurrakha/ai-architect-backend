from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.api.routes.requirements import get_requirements_service
from app.main import app
from app.models.requirement import Requirement


class FakeRequirementsService:
    async def generate(self, project_id: int) -> Requirement:
        now = datetime.now(UTC)

        return Requirement(
            id=1,
            project_id=project_id,
            version=1,
            content={
                "functional": [
                    "Users can create projects",
                    "Users can generate requirements",
                ],
                "non_functional": [
                    "The system should be reliable",
                ],
                "constraints": [
                    "The system should use PostgreSQL",
                ],
            },
            created_at=now,
            updated_at=now,
        )


class FakeNotFoundRequirementsService:
    async def generate(self, project_id: int) -> Requirement:
        raise ValueError(
            f"Project {project_id} not found"
        )


@pytest.fixture
def client():
    app.dependency_overrides[get_requirements_service] = (
        lambda: FakeRequirementsService()
    )

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(
        get_requirements_service,
        None,
    )


def test_generate_requirements(client):
    response = client.post(
        "/projects/1/requirements/generate",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["project_id"] == 1
    assert data["version"] == 1

    assert data["content"]["functional"] == [
        "Users can create projects",
        "Users can generate requirements",
    ]

    assert data["content"]["non_functional"] == [
        "The system should be reliable",
    ]

    assert data["content"]["constraints"] == [
        "The system should use PostgreSQL",
    ]


def test_generate_requirements_project_not_found():
    app.dependency_overrides[get_requirements_service] = (
        lambda: FakeNotFoundRequirementsService()
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                "/projects/999/requirements/generate",
            )

        assert response.status_code == 404
        assert response.json()["detail"] == "Project 999 not found"

    finally:
        app.dependency_overrides.pop(
            get_requirements_service,
            None,
        )