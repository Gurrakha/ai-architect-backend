from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.prd import PRDResponse
from app.services.ai.agents.prd import PRDAgent
from app.services.ai.gemini import GeminiProvider
from app.services.prd.service import PRDService


router = APIRouter(
    prefix="/projects/{project_id}/prd",
    tags=["PRD"],
)


def get_prd_service(
    db: Session = Depends(get_db),
) -> PRDService:
    provider = GeminiProvider()
    agent = PRDAgent(provider)

    return PRDService(
        db=db,
        agent=agent,
    )


@router.post(
    "/generate",
    response_model=PRDResponse,
)
async def generate_prd(
    project_id: int,
    service: PRDService = Depends(get_prd_service),
) -> PRDResponse:
    try:
        return await service.generate(project_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc