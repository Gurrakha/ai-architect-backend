from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.requirement import RequirementResponse
from app.services.ai.agents.requirements import RequirementsAgent
from app.services.ai.gemini import GeminiProvider
from app.services.requirements.service import RequirementsService


router = APIRouter(
    prefix="/projects/{project_id}/requirements",
    tags=["Requirements"],
)


def get_requirements_service(
    db: Session = Depends(get_db),
) -> RequirementsService:
    provider = GeminiProvider()
    agent = RequirementsAgent(provider)

    return RequirementsService(
        db=db,
        agent=agent,
    )


@router.post(
    "/generate",
    response_model=RequirementResponse,
)
async def generate_requirements(
    project_id: int,
    service: RequirementsService = Depends(get_requirements_service),
) -> RequirementResponse:
    try:
        requirement = await service.generate(project_id)

        return requirement

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc