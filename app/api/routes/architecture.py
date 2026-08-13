from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.architecture import ArchitectureResponse
from app.services.ai.agents.architecture import ArchitectureAgent
from app.services.ai.gemini import GeminiProvider
from app.services.architecture.service import ArchitectureService


router = APIRouter(
    prefix="/projects/{project_id}/architectures",
    tags=["Architecture"],
)


def get_architecture_service(
    db: Session = Depends(get_db),
) -> ArchitectureService:
    provider = GeminiProvider()
    agent = ArchitectureAgent(provider)

    return ArchitectureService(
        db=db,
        agent=agent,
    )


@router.post(
    "/generate",
    response_model=ArchitectureResponse,
)
async def generate_architecture(
    project_id: int,
    service: ArchitectureService = Depends(
        get_architecture_service,
    ),
) -> ArchitectureResponse:
    try:
        return await service.generate(project_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc