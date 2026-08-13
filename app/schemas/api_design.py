from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class APIParameter(BaseModel):
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)
    required: bool = False
    description: str | None = None


class APIRequest(BaseModel):
    content_type: str | None = None
    parameters: list[APIParameter] = Field(
        default_factory=list,
    )
    body: dict | None = None


class APIResponse(BaseModel):
    status_code: int = Field(ge=100, le=599)
    description: str = Field(min_length=1)
    content_type: str | None = None
    body: dict | None = None


class APIEndpoint(BaseModel):
    method: str = Field(min_length=1)
    path: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    description: str | None = None
    authentication: str | None = None
    request: APIRequest | None = None
    responses: list[APIResponse] = Field(
        default_factory=list,
    )


class APIDesignContent(BaseModel):
    endpoints: list[APIEndpoint] = Field(
        default_factory=list,
    )
    conventions: list[str] = Field(
        default_factory=list,
    )


class APIDesignCreate(BaseModel):
    content: APIDesignContent


class APIDesignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    version: int
    content: APIDesignContent
    created_at: datetime
    updated_at: datetime