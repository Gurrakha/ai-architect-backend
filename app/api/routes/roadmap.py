from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.roadmap import RoadmapResponse
from app.services.ai.agents.roadmap import RoadmapAgent
from app.services.ai.gemini import GeminiProvider
from app.services.roadmap.service import RoadmapService


router = APIRouter(
    prefix="/projects/{project_id}/roadmap",
    tags=["Roadmap"],
)


def get_roadmap_service(
    db: Session = Depends(get_db),
) -> RoadmapService:
    provider = GeminiProvider()
    agent = RoadmapAgent(provider)

    return RoadmapService(
        db=db,
        agent=agent,
    )


@router.post(
    "/generate",
    response_model=RoadmapResponse,
)
async def generate_roadmap(
    project_id: int,
    service: RoadmapService = Depends(
        get_roadmap_service,
    ),
) -> RoadmapResponse:
    try:
        return await service.generate(project_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
