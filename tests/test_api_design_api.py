from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.api.routes.api_design import get_api_design_service
from app.main import app
from app.models.api_design import APIDesign


class FakeAPIDesignService:
    async def generate(self, project_id: int) -> APIDesign:
        now = datetime.now(UTC)

        return APIDesign(
            id=1,
            project_id=project_id,
            version=1,
            content={
                "endpoints": [
                    {
                        "method": "POST",
                        "path": "/projects",
                        "summary": "Create a project",
                        "description": "Create a new project.",
                        "authentication": None,
                        "request": {
                            "content_type": "application/json",
                            "parameters": [],
                            "body": {
                                "name": "string",
                                "idea": "string",
                            },
                        },
                        "responses": [
                            {
                                "status_code": 201,
                                "description": (
                                    "Project created successfully."
                                ),
                                "content_type": "application/json",
                                "body": {
                                    "id": 1,
                                },
                            }
                        ],
                    }
                ],
                "conventions": [
                    "Use plural resource names.",
                    "Use standard HTTP status codes.",
                ],
            },
            created_at=now,
            updated_at=now,
        )


class FakeNotFoundAPIDesignService:
    async def generate(self, project_id: int) -> APIDesign:
        raise ValueError(
            f"Project {project_id} not found"
        )


@pytest.fixture
def client():
    app.dependency_overrides[get_api_design_service] = (
        lambda: FakeAPIDesignService()
    )

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(
        get_api_design_service,
        None,
    )


def test_generate_api_design(client):
    response = client.post(
        "/projects/1/api-design/generate",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["project_id"] == 1
    assert data["version"] == 1

    assert data["content"]["endpoints"][0]["method"] == "POST"
    assert data["content"]["endpoints"][0]["path"] == "/projects"

    assert data["content"]["conventions"] == [
        "Use plural resource names.",
        "Use standard HTTP status codes.",
    ]


def test_generate_api_design_project_not_found():
    app.dependency_overrides[get_api_design_service] = (
        lambda: FakeNotFoundAPIDesignService()
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                "/projects/999/api-design/generate",
            )

        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Project 999 not found"
        )

    finally:
        app.dependency_overrides.pop(
            get_api_design_service,
            None,
        )