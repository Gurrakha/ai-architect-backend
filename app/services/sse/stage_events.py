from app.services.sse.manager import sse_manager


async def publish_stage_started(
    generation_id: int,
    stage: str,
) -> None:
    await sse_manager.publish(
        generation_id,
        {
            "event": "stage_started",
            "data": {
                "generation_id": generation_id,
                "stage": stage,
            },
        },
    )


async def publish_stage_completed(
    generation_id: int,
    stage: str,
) -> None:
    await sse_manager.publish(
        generation_id,
        {
            "event": "stage_completed",
            "data": {
                "generation_id": generation_id,
                "stage": stage,
            },
        },
    )


async def publish_stage_waiting(
    generation_id: int,
    stage: str,
) -> None:
    await sse_manager.publish(
        generation_id,
        {
            "event": "stage_waiting",
            "data": {
                "generation_id": generation_id,
                "stage": stage,
            },
        },
    )


async def publish_stage_failed(
    generation_id: int,
    stage: str,
    error: str,
) -> None:
    await sse_manager.publish(
        generation_id,
        {
            "event": "stage_failed",
            "data": {
                "generation_id": generation_id,
                "stage": stage,
                "error": error,
            },
        },
    )