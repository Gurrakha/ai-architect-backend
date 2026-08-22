from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.database_design import DatabaseDesignResponse
from app.services.ai.agents.database_design import DatabaseDesignAgent
from app.services.ai.gemini import GeminiProvider
from app.services.database_design.service import DatabaseDesignService


router = APIRouter(
    prefix="/projects/{project_id}/database-design",
    tags=["Database Design"],
)


def get_database_design_service(
    db: Session = Depends(get_db),
) -> DatabaseDesignService:
    provider = GeminiProvider()
    agent = DatabaseDesignAgent(provider)

    return DatabaseDesignService(
        db=db,
        agent=agent,
    )


@router.post(
    "/generate",
    response_model=DatabaseDesignResponse,
)
async def generate_database_design(
    project_id: int,
    service: DatabaseDesignService = Depends(
        get_database_design_service,
    ),
) -> DatabaseDesignResponse:
    try:
        return await service.generate(project_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get(
    "/latest",
    response_model=DatabaseDesignResponse,
)
async def get_latest_database_design(
    project_id: int,
    service: DatabaseDesignService = Depends(
        get_database_design_service,
    ),
) -> DatabaseDesignResponse:
    try:
        database_design = service.get_latest(project_id)

        if database_design is None:
            raise ValueError(
                f"No database design found for project {project_id}"
            )

        return database_design

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc