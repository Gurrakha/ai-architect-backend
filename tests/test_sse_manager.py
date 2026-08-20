
import pytest

from app.services.sse.manager import SSEManager


@pytest.mark.anyio
async def test_subscribe_publish_and_receive_event():
    manager = SSEManager()

    queue = await manager.subscribe(
        generation_id=1,
    )

    event = {
        "event": "status",
        "data": {
            "generation_id": 1,
            "status": "RUNNING",
        },
    }

    await manager.publish(
        generation_id=1,
        event=event,
    )

    received = await queue.get()

    assert received == event


@pytest.mark.anyio
async def test_unsubscribe_stops_receiving_events():
    manager = SSEManager()

    queue = await manager.subscribe(
        generation_id=1,
    )

    await manager.unsubscribe(
        generation_id=1,
        queue=queue,
    )

    await manager.publish(
        generation_id=1,
        event={
            "event": "completed",
            "data": {
                "generation_id": 1,
            },
        },
    )

    assert queue.empty()
