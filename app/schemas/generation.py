from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field
from app.models.generation import GenerationStatus


class GenerationCreate(BaseModel):
    workflow: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)


class GenerationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    workflow: str
    status: GenerationStatus
    model: str
    started_at: datetime | None
    completed_at: datetime | None
    error: str | None
    created_at: datetime