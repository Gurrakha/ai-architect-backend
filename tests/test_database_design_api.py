from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.api.routes.database_design import (
    get_database_design_service,
)
from app.main import app
from app.models.database_design import DatabaseDesign


class FakeDatabaseDesignService:
    async def generate(
        self,
        project_id: int,
    ) -> DatabaseDesign:
        now = datetime.now(UTC)

        return DatabaseDesign(
            id=1,
            project_id=project_id,
            version=1,
            content={
                "tables": [
                    {
                        "name": "projects",
                        "description": "Stores projects.",
                        "columns": [
                            {
                                "name": "id",
                                "type": "integer",
                                "nullable": False,
                                "primary_key": True,
                                "unique": True,
                                "default": None,
                                "description": None,
                            },
                        ],
                    },
                ],
                "relationships": [],
                "indexes": [],
            },
            created_at=now,
            updated_at=now,
        )


class FakeNotFoundDatabaseDesignService:
    async def generate(
        self,
        project_id: int,
    ) -> DatabaseDesign:
        raise ValueError(
            f"Project {project_id} not found"
        )


@pytest.fixture
def client():
    app.dependency_overrides[get_database_design_service] = (
        lambda: FakeDatabaseDesignService()
    )

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(
        get_database_design_service,
        None,
    )


def test_generate_database_design(client):
    response = client.post(
        "/projects/1/database-design/generate",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["project_id"] == 1
    assert data["version"] == 1

    assert data["content"]["tables"][0]["name"] == "projects"

    assert (
        data["content"]["tables"][0]["columns"][0]["name"]
        == "id"
    )


def test_generate_database_design_project_not_found():
    app.dependency_overrides[get_database_design_service] = (
        lambda: FakeNotFoundDatabaseDesignService()
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                "/projects/999/database-design/generate",
            )

        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Project 999 not found"
        )

    finally:
        app.dependency_overrides.pop(
            get_database_design_service,
            None,
        )