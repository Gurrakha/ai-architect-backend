from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# -------------------------
# Component
# -------------------------

class ComponentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: str = Field(min_length=1, max_length=100)
    technology: str | None = Field(
        default=None,
        max_length=255,
    )
    description: str | None = None


class ComponentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    architecture_id: int
    name: str
    type: str
    technology: str | None
    description: str | None
    created_at: datetime


# -------------------------
# Connection
# -------------------------

class ConnectionCreate(BaseModel):
    source_component_id: int
    target_component_id: int
    protocol: str | None = Field(
        default=None,
        max_length=100,
    )
    description: str | None = None


class ConnectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    architecture_id: int
    source_component_id: int
    target_component_id: int
    protocol: str | None
    description: str | None
    created_at: datetime


# -------------------------
# Architecture Decision
# -------------------------

class ArchitectureDecisionCreate(BaseModel):
    decision: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    alternatives: list[str] = Field(default_factory=list)
    tradeoffs: str | None = None


class ArchitectureDecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    architecture_id: int
    decision: str
    rationale: str
    alternatives: list[str]
    tradeoffs: str | None
    created_at: datetime


# -------------------------
# Architecture
# -------------------------

class ArchitectureCreate(BaseModel):
    overview: str = Field(min_length=1)

    components: list[ComponentCreate] = Field(
        default_factory=list,
    )

    connections: list[ConnectionCreate] = Field(
        default_factory=list,
    )

    decisions: list[ArchitectureDecisionCreate] = Field(
        default_factory=list,
    )


class ArchitectureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    version: int
    overview: str

    components: list[ComponentResponse] = Field(
        default_factory=list,
    )

    connections: list[ConnectionResponse] = Field(
        default_factory=list,
    )

    decisions: list[ArchitectureDecisionResponse] = Field(
        default_factory=list,
    )

    created_at: datetime
    updated_at: datetime