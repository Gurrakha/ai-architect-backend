from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RequirementContent(BaseModel):
    functional: list[str] = Field(default_factory=list)
    non_functional: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class RequirementCreate(BaseModel):
    content: RequirementContent


class RequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    version: int
    content: RequirementContent
    created_at: datetime
    updated_at: datetime