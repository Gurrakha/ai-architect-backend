from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.api_design import APIDesignResponse
from app.services.ai.agents.api_design import APIDesignAgent
from app.services.ai.gemini import GeminiProvider
from app.services.api_design.service import APIDesignService


router = APIRouter(
    prefix="/projects/{project_id}/api-design",
    tags=["API Design"],
)


def get_api_design_service(
    db: Session = Depends(get_db),
) -> APIDesignService:
    provider = GeminiProvider()
    agent = APIDesignAgent(provider)

    return APIDesignService(
        db=db,
        agent=agent,
    )


@router.post(
    "/generate",
    response_model=APIDesignResponse,
)
async def generate_api_design(
    project_id: int,
    service: APIDesignService = Depends(
        get_api_design_service,
    ),
) -> APIDesignResponse:
    try:
        return await service.generate(project_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc