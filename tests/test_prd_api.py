from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.api.routes.prd import get_prd_service
from app.main import app
from app.models.prd import PRD


class FakePRDService:
    async def generate(self, project_id: int) -> PRD:
        now = datetime.now(UTC)

        return PRD(
            id=1,
            project_id=project_id,
            version=1,
            content={
                "title": "AI Architect",
                "problem_statement": (
                    "Turn product ideas into technical plans."
                ),
                "target_users": [
                    "Software developers",
                ],
                "goals": [
                    "Reduce architecture planning effort",
                ],
                "features": [
                    "Project creation",
                    "Requirements generation",
                ],
                "user_stories": [
                    (
                        "As a user, I want to create a project "
                        "so that I can plan it."
                    ),
                ],
                "assumptions": [
                    "Users provide a project idea.",
                ],
                "out_of_scope": [
                    "Application implementation",
                ],
            },
            created_at=now,
            updated_at=now,
        )


class FakeNotFoundPRDService:
    async def generate(self, project_id: int) -> PRD:
        raise ValueError(
            f"Project {project_id} not found"
        )


@pytest.fixture
def client():
    app.dependency_overrides[get_prd_service] = (
        lambda: FakePRDService()
    )

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(
        get_prd_service,
        None,
    )


def test_generate_prd(client):
    response = client.post(
        "/projects/1/prd/generate",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["project_id"] == 1
    assert data["version"] == 1

    assert data["content"]["title"] == "AI Architect"

    assert data["content"]["features"] == [
        "Project creation",
        "Requirements generation",
    ]


def test_generate_prd_project_not_found():
    app.dependency_overrides[get_prd_service] = (
        lambda: FakeNotFoundPRDService()
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                "/projects/999/prd/generate",
            )

        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Project 999 not found"
        )

    finally:
        app.dependency_overrides.pop(
            get_prd_service,
            None,
        )