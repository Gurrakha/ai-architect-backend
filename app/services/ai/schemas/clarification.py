from pydantic import BaseModel, Field


class ClarificationQuestionGeneration(BaseModel):
    question: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class ClarificationGeneration(BaseModel):
    needs_clarification: bool

    questions: list[ClarificationQuestionGeneration] = Field(
        default_factory=list,
    )