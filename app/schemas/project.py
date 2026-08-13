from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.project import ProjectStatus

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    idea: str = Field(min_length=1)

class ProjectUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    idea: str | None = Field(
        default=None,
        min_length=1,
    )


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    idea: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime