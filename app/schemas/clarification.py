from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClarificationCreate(BaseModel):
    question: str = Field(min_length=1)


class ClarificationAnswer(BaseModel):
    answer: str = Field(min_length=1)


class ClarificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    generation_id: int
    question: str
    answer: str | None
    reason: str | None
    created_at: datetime
    answered_at: datetime | None