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