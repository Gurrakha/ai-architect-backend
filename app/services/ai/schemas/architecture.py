from pydantic import BaseModel, Field

from app.schemas.architecture import (
    ArchitectureDecisionCreate,
    ComponentCreate,
)


class ArchitectureConnectionGeneration(BaseModel):
    source_component: str = Field(min_length=1)
    target_component: str = Field(min_length=1)

    protocol: str | None = Field(
        default=None,
        max_length=100,
    )

    description: str | None = None


class ArchitectureGeneration(BaseModel):
    overview: str = Field(min_length=1)

    components: list[ComponentCreate] = Field(
        default_factory=list,
    )

    connections: list[ArchitectureConnectionGeneration] = Field(
        default_factory=list,
    )

    decisions: list[ArchitectureDecisionCreate] = Field(
        default_factory=list,
    )