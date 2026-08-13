from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.api.routes.architecture import get_architecture_service
from app.main import app
from app.models.architecture import Architecture


class FakeArchitectureService:
    async def generate(self, project_id: int) -> Architecture:
        now = datetime.now(UTC)

        architecture = Architecture(
            id=1,
            project_id=project_id,
            version=1,
            overview="A modular web application architecture.",
            created_at=now,
            updated_at=now,
        )

        return architecture


class FakeNotFoundArchitectureService:
    async def generate(self, project_id: int) -> Architecture:
        raise ValueError(
            f"Project {project_id} not found"
        )


@pytest.fixture
def client():
    app.dependency_overrides[get_architecture_service] = (
        lambda: FakeArchitectureService()
    )

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(
        get_architecture_service,
        None,
    )


def test_generate_architecture(client):
    response = client.post(
        "/projects/1/architectures/generate",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["project_id"] == 1
    assert data["version"] == 1
    assert data["overview"] == (
        "A modular web application architecture."
    )


def test_generate_architecture_project_not_found():
    app.dependency_overrides[get_architecture_service] = (
        lambda: FakeNotFoundArchitectureService()
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                "/projects/999/architectures/generate",
            )

        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Project 999 not found"
        )

    finally:
        app.dependency_overrides.pop(
            get_architecture_service,
            None,
        )