from unittest.mock import AsyncMock, Mock

from fastapi.testclient import TestClient

from app.core.utils import utc_now
from app.main import app
from app.api.routes.generation import (
    get_generation_orchestrator,
    get_generation_service,
    get_project_service,
    get_clarification_service
)
from app.models.generation import Generation, GenerationStatus
from app.models.project import Project
from app.models.clarification import Clarification


def test_create_generation():
    project_service = Mock()
    generation_service = Mock()
    orchestrator = Mock()

    project = Project(
        id=1,
        name="AI Architect",
        idea="An AI system for generating technical plans.",
    )

    generation = Generation(
        id=1,
        project_id=1,
        workflow="full_generation",
        model="gemini",
        status=GenerationStatus.PENDING,
        created_at= utc_now()
    )

    project_service.get_project_by_id.return_value = project
    generation_service.create.return_value = generation

    app.dependency_overrides[get_project_service] = (
        lambda: project_service
    )
    app.dependency_overrides[get_generation_service] = (
        lambda: generation_service
    )
    app.dependency_overrides[get_generation_orchestrator] = (
        lambda: orchestrator
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/projects/1/generations",
            json={
                "workflow": "full_generation",
                "model": "gemini",
            },
        )

    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201

    assert response.json()["id"] == 1
    assert response.json()["project_id"] == 1
    assert response.json()["workflow"] == "full_generation"
    assert response.json()["model"] == "gemini"
    assert response.json()["status"] == "PENDING"

    project_service.get_project_by_id.assert_called_once_with(
        1,
    )

    generation_service.create.assert_called_once_with(
        project_id=1,
        workflow="full_generation",
        model="gemini",
    )

    orchestrator.run.assert_called_once_with(
        generation_id=1,
        project_id=1,
        project_name="AI Architect",
        project_idea=(
            "An AI system for generating technical plans."
        ),
    )

def test_create_generation_project_not_found():
    project_service = Mock()
    generation_service = Mock()
    orchestrator = Mock()

    project_service.get_project_by_id.return_value = None

    app.dependency_overrides[get_project_service] = (
        lambda: project_service
    )
    app.dependency_overrides[get_generation_service] = (
        lambda: generation_service
    )
    app.dependency_overrides[get_generation_orchestrator] = (
        lambda: orchestrator
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/projects/999/generations",
            json={
                "workflow": "full_generation",
                "model": "gemini",
            },
        )

    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Project 999 not found",
    }

    generation_service.create.assert_not_called()

def test_answer_clarification():
    clarification_service = Mock()
    orchestrator = Mock()
    orchestrator.resume = AsyncMock()

    clarification = Clarification(
        id=1,
        project_id=1,
        generation_id=1,
        question="Who can create projects?",
        reason="Authorization is required.",
        answer="Only authenticated users.",
        answered_at=utc_now(),
        created_at=utc_now(),
    )

    clarification_service.answer.return_value = clarification

    app.dependency_overrides[get_clarification_service] = (
        lambda: clarification_service
    )
    app.dependency_overrides[get_generation_orchestrator] = (
        lambda: orchestrator
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/projects/1/generations/1/clarifications/1",
            json={
                "answer": "Only authenticated users.",
            },
        )

    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    assert response.json()["id"] == 1
    assert response.json()["project_id"] == 1
    assert response.json()["generation_id"] == 1
    assert response.json()["question"] == "Who can create projects?"
    assert response.json()["answer"] == "Only authenticated users."

    clarification_service.answer.assert_called_once_with(
        project_id=1,
        generation_id=1,
        clarification_id=1,
        answer="Only authenticated users.",
    )

    orchestrator.resume.assert_called_once_with(
        generation_id=1,
        answers=[
            {
                "id": 1,
                "answer": "Only authenticated users.",
            }
        ],
    )


def test_answer_clarification_not_found():
    clarification_service = Mock()
    orchestrator = Mock()
    orchestrator.resume = AsyncMock()

    clarification_service.answer.side_effect = ValueError(
        "Clarification 999 not found"
    )

    app.dependency_overrides[get_clarification_service] = (
        lambda: clarification_service
    )
    app.dependency_overrides[get_generation_orchestrator] = (
        lambda: orchestrator
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/projects/1/generations/1/clarifications/999",
            json={
                "answer": "Only authenticated users.",
            },
        )

    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Clarification 999 not found",
    }

    clarification_service.answer.assert_called_once_with(
        project_id=1,
        generation_id=1,
        clarification_id=999,
        answer="Only authenticated users.",
    )

    orchestrator.resume.assert_not_called()
