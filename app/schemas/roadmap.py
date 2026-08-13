from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoadmapTask(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    priority: str = Field(min_length=1)
    estimated_effort: str | None = None
    dependencies: list[str] = Field(
        default_factory=list,
    )


class RoadmapPhase(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
    tasks: list[RoadmapTask] = Field(
        default_factory=list,
    )


class RoadmapContent(BaseModel):
    phases: list[RoadmapPhase] = Field(
        default_factory=list,
    )


class RoadmapCreate(BaseModel):
    content: RoadmapContent


class RoadmapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    version: int
    content: RoadmapContent
    created_at: datetime
    updated_at: datetime