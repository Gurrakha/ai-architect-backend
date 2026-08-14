from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.api.routes.roadmap import get_roadmap_service
from app.main import app
from app.models.roadmap import Roadmap


class FakeRoadmapService:
    async def generate(self, project_id: int) -> Roadmap:
        now = datetime.now(UTC)

        return Roadmap(
            id=1,
            project_id=project_id,
            version=1,
            content={
                "phases": [
                    {
                        "name": "Foundation",
                        "description": "Project foundation.",
                        "tasks": [
                            {
                                "title": "Set up backend",
                                "description": (
                                    "Initialize backend services."
                                ),
                                "priority": "high",
                                "estimated_effort": "1 day",
                                "dependencies": [],
                            },
                        ],
                    },
                ],
            },
            created_at=now,
            updated_at=now,
        )


class FakeNotFoundRoadmapService:
    async def generate(self, project_id: int) -> Roadmap:
        raise ValueError(
            f"Project {project_id} not found"
        )


@pytest.fixture
def client():
    app.dependency_overrides[get_roadmap_service] = (
        lambda: FakeRoadmapService()
    )

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(
        get_roadmap_service,
        None,
    )


def test_generate_roadmap(client):
    response = client.post(
        "/projects/1/roadmap/generate",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["project_id"] == 1
    assert data["version"] == 1

    assert data["content"]["phases"][0]["name"] == "Foundation"

    assert (
        data["content"]["phases"][0]["tasks"][0]["title"]
        == "Set up backend"
    )


def test_generate_roadmap_project_not_found():
    app.dependency_overrides[get_roadmap_service] = (
        lambda: FakeNotFoundRoadmapService()
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                "/projects/999/roadmap/generate",
            )

        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Project 999 not found"
        )

    finally:
        app.dependency_overrides.pop(
            get_roadmap_service,
            None,
        )
