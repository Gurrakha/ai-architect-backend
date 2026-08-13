from app.schemas.architecture import (
    ArchitectureCreate,
    ArchitectureDecisionCreate,
    ArchitectureDecisionResponse,
    ArchitectureResponse,
    ComponentCreate,
    ComponentResponse,
    ConnectionCreate,
    ConnectionResponse,
)

from app.schemas.prd import (
    PRDContent,
    PRDCreate,
    PRDResponse,
)

from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)

from app.schemas.requirement import (
    RequirementContent,
    RequirementCreate,
    RequirementResponse,
)

from app.schemas.database_design import (
    DatabaseColumn,
    DatabaseDesignContent,
    DatabaseDesignCreate,
    DatabaseDesignResponse,
    DatabaseIndex,
    DatabaseRelationship,
    DatabaseTable,
)

from app.schemas.api_design import (
    APIEndpoint,
    APIParameter,
    APIRequest,
    APIResponse,
    APIDesignContent,
    APIDesignCreate,
    APIDesignResponse,
)

from app.schemas.roadmap import (
    RoadmapContent,
    RoadmapCreate,
    RoadmapPhase,
    RoadmapResponse,
    RoadmapTask,
)

from app.schemas.generation import (
    GenerationCreate,
    GenerationResponse,
    GenerationStatus,
)

from app.schemas.clarification import (
    ClarificationAnswer,
    ClarificationCreate,
    ClarificationResponse,
)

__all__ = [
    # Project
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",

    # Requirements
    "RequirementContent",
    "RequirementCreate",
    "RequirementResponse",

    # PRD
    "PRDContent",
    "PRDCreate",
    "PRDResponse",

    # Architecture
    "ArchitectureCreate",
    "ArchitectureResponse",
    "ComponentCreate",
    "ComponentResponse",
    "ConnectionCreate",
    "ConnectionResponse",
    "ArchitectureDecisionCreate",
    "ArchitectureDecisionResponse",

    # Database Design
    "DatabaseColumn",
    "DatabaseTable",
    "DatabaseRelationship",
    "DatabaseIndex",
    "DatabaseDesignContent",
    "DatabaseDesignCreate",
    "DatabaseDesignResponse",

    # API Design
    "APIParameter",
    "APIRequest",
    "APIResponse",
    "APIEndpoint",
    "APIDesignContent",
    "APIDesignCreate",
    "APIDesignResponse",

    # Roadmap
    "RoadmapTask",
    "RoadmapPhase",
    "RoadmapContent",
    "RoadmapCreate",
    "RoadmapResponse",

    # Generation
    "GenerationStatus",
    "GenerationCreate",
    "GenerationResponse",

    # Clarification
    "ClarificationCreate",
    "ClarificationAnswer",
    "ClarificationResponse",
]