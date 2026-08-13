from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate


class ProjectService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_project(self, data: ProjectCreate) -> Project:
        project = Project(
            name=data.name,
            idea=data.idea,
        )

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        return project