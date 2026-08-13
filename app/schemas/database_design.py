from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DatabaseColumn(BaseModel):
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    default: str | None = None
    description: str | None = None


class DatabaseTable(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
    columns: list[DatabaseColumn] = Field(
        default_factory=list,
    )


class DatabaseRelationship(BaseModel):
    source_table: str = Field(min_length=1)
    source_column: str = Field(min_length=1)
    target_table: str = Field(min_length=1)
    target_column: str = Field(min_length=1)
    relationship_type: str = Field(min_length=1)


class DatabaseIndex(BaseModel):
    name: str = Field(min_length=1)
    table: str = Field(min_length=1)
    columns: list[str] = Field(default_factory=list)
    unique: bool = False


class DatabaseDesignContent(BaseModel):
    tables: list[DatabaseTable] = Field(
        default_factory=list,
    )

    relationships: list[DatabaseRelationship] = Field(
        default_factory=list,
    )

    indexes: list[DatabaseIndex] = Field(
        default_factory=list,
    )


class DatabaseDesignCreate(BaseModel):
    content: DatabaseDesignContent


class DatabaseDesignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    version: int
    content: DatabaseDesignContent
    created_at: datetime
    updated_at: datetime