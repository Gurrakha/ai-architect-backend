import asyncio
import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.clarification import Clarification
from app.models.generation import Generation, GenerationStatus
from app.services.sse.manager import sse_manager


router = APIRouter(
    prefix="/projects/{project_id}/generations",
    tags=["generation-events"],
)


def format_sse(
    event: str,
    data: dict,
) -> str:
    return (
        f"event: {event}\n"
        f"data: {json.dumps(data)}\n\n"
    )


async def generation_events(
    request: Request,
    db: Session,
    project_id: int,
    generation_id: int,
) -> AsyncGenerator[str, None]:
    queue = await sse_manager.subscribe(generation_id)

    try:
        generation = db.get(
            Generation,
            generation_id,
        )

        if (
            generation is None
            or generation.project_id != project_id
        ):
            yield format_sse(
                "error",
                {
                    "detail": (
                        f"Generation {generation_id} not found"
                    ),
                },
            )
            return

        yield format_sse(
            "status",
            {
                "generation_id": generation.id,
                "status": generation.status.value,
            },
        )

        if generation.status == GenerationStatus.WAITING_FOR_INPUT:
            clarifications = (
                db.query(Clarification)
                .filter(
                    Clarification.project_id == project_id,
                    Clarification.generation_id == generation_id,
                )
                .all()
            )

            yield format_sse(
                "clarification_required",
                {
                    "generation_id": generation_id,
                    "clarifications": [
                        {
                            "id": clarification.id,
                            "question": clarification.question,
                            "reason": clarification.reason,
                            "answer": clarification.answer,
                        }
                        for clarification in clarifications
                    ],
                },
            )

        if generation.status == GenerationStatus.COMPLETED:
            yield format_sse(
                "completed",
                {
                    "generation_id": generation_id,
                },
            )
            return

        if generation.status == GenerationStatus.FAILED:
            yield format_sse(
                "failed",
                {
                    "generation_id": generation_id,
                    "error": generation.error,
                },
            )
            return

        while True:
            if await request.is_disconnected():
                return

            try:
                event = await asyncio.wait_for(
                    queue.get(),
                    timeout=15,
                )
            except asyncio.TimeoutError:
                yield ": keep-alive\n\n"
                continue

            yield format_sse(
                event["event"],
                event["data"],
            )

            if event["event"] in {
                "completed",
                "failed",
            }:
                return

    finally:
        await sse_manager.unsubscribe(
            generation_id,
            queue,
        )

@router.get("/{generation_id}/events")
async def generation_events_endpoint(
    request: Request,
    project_id: int,
    generation_id: int,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    generation = db.get(
        Generation,
        generation_id,
    )

    if (
        generation is None
        or generation.project_id != project_id
    ):
        raise HTTPException(
            status_code=404,
            detail=f"Generation {generation_id} not found",
        )

    return StreamingResponse(
        generation_events(
            request=request,
            db=db,
            project_id=project_id,
            generation_id=generation_id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )