from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.generation import GenerationCreate, GenerationResponse
from app.services.generation.orchestrator import GenerationOrchestrator
from app.services.generation.service import GenerationService
from app.services.projects.service import ProjectService

from app.schemas.clarification import (
    ClarificationAnswer,
    ClarificationResponse,
)
from app.services.clarification.service import ClarificationService
from app.services.ai.agents.clarification import ClarificationAgent
from app.services.ai.gemini import GeminiProvider

def get_clarification_service(
    db: Session = Depends(get_db),
) -> ClarificationService:
    provider = GeminiProvider()
    agent = ClarificationAgent(provider)

    return ClarificationService(
        db=db,
        agent=agent,
    )


router = APIRouter(
    prefix="/projects/{project_id}/generations",
    tags=["generations"],
)


def get_project_service(
    db: Session = Depends(get_db),
) -> ProjectService:
    return ProjectService(
        db=db,
    )


def get_generation_service(
    db: Session = Depends(get_db),
) -> GenerationService:
    return GenerationService(
        db=db,
    )


def get_generation_orchestrator(
    request: Request,
    db: Session = Depends(get_db),
) -> GenerationOrchestrator:
    generation_service = GenerationService(
        db=db,
    )

    return GenerationOrchestrator(
        generation_service=generation_service,
        checkpointer=request.app.state.checkpointer,
    )


@router.post(
    "",
    response_model=GenerationResponse,
    status_code=201,
)
async def create_generation(
    project_id: int,
    data: GenerationCreate,
    background_tasks: BackgroundTasks,
    project_service: ProjectService = Depends(
        get_project_service,
    ),
    generation_service: GenerationService = Depends(
        get_generation_service,
    ),
    orchestrator: GenerationOrchestrator = Depends(
        get_generation_orchestrator,
    ),
) -> GenerationResponse:
    project = project_service.get_project_by_id(
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail=f"Project {project_id} not found",
        )

    generation = generation_service.create(
        project_id=project_id,
        workflow=data.workflow,
        model=data.model,
    )

    background_tasks.add_task(
        orchestrator.run,
        generation_id=generation.id,
        project_id=project.id,
        project_name=project.name,
        project_idea=project.idea,
    )

    return generation

@router.post(
    "/{generation_id}/clarifications/{clarification_id}",
    response_model=ClarificationResponse,
)
async def answer_clarification(
    project_id: int,
    generation_id: int,
    clarification_id: int,
    data: ClarificationAnswer,
    clarification_service: ClarificationService = Depends(
        get_clarification_service,
    ),
    orchestrator: GenerationOrchestrator = Depends(
        get_generation_orchestrator,
    ),
) -> ClarificationResponse:
    try:
        clarification = clarification_service.answer(
            project_id=project_id,
            generation_id=generation_id,
            clarification_id=clarification_id,
            answer=data.answer,
        )

        await orchestrator.resume(
            generation_id=generation_id,
            answers=[
                {
                    "id": clarification_id,
                    "answer": data.answer,
                }
            ],
        )

        return clarification

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get(
    "/{generation_id}",
    response_model=GenerationResponse,
)
async def get_generation(
    project_id: int,
    generation_id: int,
    generation_service: GenerationService = Depends(
        get_generation_service,
    ),
) -> GenerationResponse:
    generation = generation_service.get_by_id(
        project_id=project_id,
        generation_id=generation_id,
    )

    if generation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Generation {generation_id} not found",
        )

    return generation


@router.get(
    "",
    response_model=list[GenerationResponse],
)
async def get_generations(
    project_id: int,
    generation_service: GenerationService = Depends(
        get_generation_service,
    ),
) -> list[GenerationResponse]:
    return generation_service.get_for_project(project_id)


@router.get(
    "/{generation_id}/clarifications",
    response_model=list[ClarificationResponse],
)
async def get_clarifications(
    project_id: int,
    generation_id: int,
    clarification_service: ClarificationService = Depends(
        get_clarification_service,
    ),
) -> list[ClarificationResponse]:
    try:
        return clarification_service.get_for_generation(
            project_id=project_id,
            generation_id=generation_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc