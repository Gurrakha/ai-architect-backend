
from datetime import UTC, datetime
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.api.routes.events import get_db
from app.main import app
from app.models.generation import Generation, GenerationStatus
from app.services.sse.manager import sse_manager


def test_generation_events_completed():
    generation = Generation(
        id=1,
        project_id=1,
        workflow="full_generation",
        model="gemini",
        status=GenerationStatus.COMPLETED,
        created_at=datetime.now(UTC),
    )

    db = Mock()
    db.get.return_value = generation

    app.dependency_overrides[get_db] = lambda: db

    try:
        # The endpoint subscribes first and then waits for an event.
        # Publish a terminal event through the manager so the stream
        # terminates cleanly.
        async def publish_completed():
            await sse_manager.publish(
                generation_id=1,
                event={
                    "event": "completed",
                    "data": {
                        "generation_id": 1,
                    },
                },
            )

        import asyncio

        asyncio.run(publish_completed())

        with TestClient(app) as client:
            response = client.get(
                "/projects/1/generations/1/events",
            )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith(
            "text/event-stream"
        )

        assert (
            'event: status\n'
            'data: {"generation_id": 1, "status": "COMPLETED"}\n\n'
        ) in response.text

        assert (
            'event: completed\n'
            'data: {"generation_id": 1}\n\n'
        ) in response.text

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )


def test_generation_events_not_found():
    db = Mock()
    db.get.return_value = None

    app.dependency_overrides[get_db] = lambda: db

    try:
        with TestClient(app) as client:
            response = client.get(
                "/projects/1/generations/999/events",
            )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Generation 999 not found",
        }

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )
