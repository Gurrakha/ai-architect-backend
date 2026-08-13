from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PRDContent(BaseModel):
    title: str = Field(min_length=1)
    problem_statement: str = Field(min_length=1)
    target_users: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    features: list[str] = Field(default_factory=list)
    user_stories: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    out_of_scope: list[str] = Field(default_factory=list)


class PRDCreate(BaseModel):
    content: PRDContent


class PRDResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    version: int
    content: PRDContent
    created_at: datetime
    updated_at: datetime