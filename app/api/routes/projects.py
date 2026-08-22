from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.projects.service import ProjectService


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


def get_project_service(
    db: Session = Depends(get_db),
) -> ProjectService:
    return ProjectService(db)


@router.post(
    "/",
    response_model=ProjectResponse,
)
def create_project(
    data: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    return service.create_project(data)

@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    project = service.get_project_by_id(project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail=f"Project {project_id} not found",
        )

    return project