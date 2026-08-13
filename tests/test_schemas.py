from app.schemas.project import ProjectCreate
from app.schemas.requirement import (
    RequirementContent,
    RequirementCreate,
)
from app.schemas.prd import PRDContent, PRDCreate
from app.schemas.architecture import (
    ArchitectureCreate,
    ArchitectureDecisionCreate,
    ComponentCreate,
    ConnectionCreate,
)
from app.schemas.database_design import (
    DatabaseColumn,
    DatabaseDesignContent,
    DatabaseDesignCreate,
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
)

from app.schemas.roadmap import (
    RoadmapContent,
    RoadmapCreate,
    RoadmapPhase,
    RoadmapTask,
)

from app.schemas.generation import (
    GenerationCreate,
    GenerationStatus,
)

from app.schemas.clarification import (
    ClarificationAnswer,
    ClarificationCreate,
)

def test_generation_create_schema():
    generation = GenerationCreate(
        workflow="full_generation",
        model="gemini-2.5-flash",
    )

    assert generation.workflow == "full_generation"
    assert generation.model == "gemini-2.5-flash"


def test_generation_status():
    assert GenerationStatus.PENDING.value == "PENDING"
    assert GenerationStatus.RUNNING.value == "RUNNING"
    assert GenerationStatus.WAITING_FOR_INPUT.value == "WAITING_FOR_INPUT"
    assert GenerationStatus.COMPLETED.value == "COMPLETED"
    assert GenerationStatus.FAILED.value == "FAILED"


def test_clarification_create_schema():
    clarification = ClarificationCreate(
        question="Will the application require authentication?"
    )

    assert clarification.question == (
        "Will the application require authentication?"
    )


def test_clarification_answer_schema():
    answer = ClarificationAnswer(
        answer="Yes, users will authenticate using Google OAuth."
    )

    assert answer.answer == (
        "Yes, users will authenticate using Google OAuth."
    )

def test_roadmap_task_schema():
    task = RoadmapTask(
        title="Set up backend",
        description="Initialize the FastAPI project.",
        priority="high",
        estimated_effort="1 day",
        dependencies=[],
    )

    assert task.title == "Set up backend"
    assert task.priority == "high"
    assert task.estimated_effort == "1 day"
    assert task.dependencies == []


def test_roadmap_phase_schema():
    phase = RoadmapPhase(
        name="Foundation",
        description="Set up the initial infrastructure.",
        tasks=[
            RoadmapTask(
                title="Set up backend",
                priority="high",
            ),
            RoadmapTask(
                title="Set up database",
                priority="high",
                dependencies=[
                    "Set up backend",
                ],
            ),
        ],
    )

    assert phase.name == "Foundation"
    assert len(phase.tasks) == 2
    assert phase.tasks[1].dependencies == ["Set up backend"]


def test_roadmap_schema():
    roadmap = RoadmapCreate(
        content=RoadmapContent(
            phases=[
                RoadmapPhase(
                    name="Foundation",
                    tasks=[
                        RoadmapTask(
                            title="Set up backend",
                            priority="high",
                            estimated_effort="1 day",
                        ),
                    ],
                ),
                RoadmapPhase(
                    name="Core Features",
                    tasks=[
                        RoadmapTask(
                            title="Implement project generation",
                            priority="high",
                            estimated_effort="3 days",
                            dependencies=[
                                "Set up backend",
                            ],
                        ),
                    ],
                ),
            ]
        )
    )

    assert len(roadmap.content.phases) == 2
    assert roadmap.content.phases[0].name == "Foundation"
    assert roadmap.content.phases[1].tasks[0].priority == "high"

def test_api_parameter_schema():
    parameter = APIParameter(
        name="project_id",
        type="integer",
        required=True,
        description="Project identifier.",
    )

    assert parameter.name == "project_id"
    assert parameter.type == "integer"
    assert parameter.required is True


def test_api_request_schema():
    request = APIRequest(
        content_type="application/json",
        parameters=[
            APIParameter(
                name="project_id",
                type="integer",
                required=True,
            )
        ],
        body={
            "name": "string",
            "idea": "string",
        },
    )

    assert request.content_type == "application/json"
    assert len(request.parameters) == 1
    assert request.body["name"] == "string"


def test_api_response_schema():
    response = APIResponse(
        status_code=201,
        description="Project created successfully.",
        content_type="application/json",
        body={
            "id": "integer",
            "name": "string",
        },
    )

    assert response.status_code == 201
    assert response.description == "Project created successfully."
    assert response.body["id"] == "integer"


def test_api_endpoint_schema():
    endpoint = APIEndpoint(
        method="POST",
        path="/projects",
        summary="Create a project",
        description="Creates a new project.",
        authentication="Bearer JWT",
        request=APIRequest(
            content_type="application/json",
            body={
                "name": "string",
                "idea": "string",
            },
        ),
        responses=[
            APIResponse(
                status_code=201,
                description="Project created successfully.",
            ),
            APIResponse(
                status_code=400,
                description="Invalid request.",
            ),
        ],
    )

    assert endpoint.method == "POST"
    assert endpoint.path == "/projects"
    assert endpoint.authentication == "Bearer JWT"
    assert endpoint.request is not None
    assert len(endpoint.responses) == 2


def test_api_design_schema():
    design = APIDesignCreate(
        content=APIDesignContent(
            endpoints=[
                APIEndpoint(
                    method="GET",
                    path="/projects/{project_id}",
                    summary="Get project",
                    authentication="Bearer JWT",
                    responses=[
                        APIResponse(
                            status_code=200,
                            description="Project retrieved successfully.",
                        ),
                        APIResponse(
                            status_code=404,
                            description="Project not found.",
                        ),
                    ],
                ),
                APIEndpoint(
                    method="POST",
                    path="/projects",
                    summary="Create project",
                    request=APIRequest(
                        content_type="application/json",
                        body={
                            "name": "string",
                            "idea": "string",
                        },
                    ),
                    responses=[
                        APIResponse(
                            status_code=201,
                            description="Project created successfully.",
                        )
                    ],
                ),
            ],
            conventions=[
                "Use RESTful resource naming.",
                "Use JSON for request and response bodies.",
                "Use standard HTTP status codes.",
            ],
        )
    )

    assert len(design.content.endpoints) == 2
    assert design.content.endpoints[0].method == "GET"
    assert design.content.endpoints[1].path == "/projects"
    assert len(design.content.conventions) == 3

def test_database_column_schema():
    column = DatabaseColumn(
        name="id",
        type="UUID",
        nullable=False,
        primary_key=True,
        unique=True,
        default="gen_random_uuid()",
        description="Unique identifier.",
    )

    assert column.name == "id"
    assert column.type == "UUID"
    assert column.nullable is False
    assert column.primary_key is True
    assert column.unique is True


def test_database_table_schema():
    table = DatabaseTable(
        name="users",
        description="Application users.",
        columns=[
            DatabaseColumn(
                name="id",
                type="UUID",
                nullable=False,
                primary_key=True,
            ),
            DatabaseColumn(
                name="email",
                type="VARCHAR(255)",
                nullable=False,
                unique=True,
            ),
        ],
    )

    assert table.name == "users"
    assert len(table.columns) == 2
    assert table.columns[0].primary_key is True
    assert table.columns[1].unique is True


def test_database_relationship_schema():
    relationship = DatabaseRelationship(
        source_table="orders",
        source_column="user_id",
        target_table="users",
        target_column="id",
        relationship_type="many-to-one",
    )

    assert relationship.source_table == "orders"
    assert relationship.source_column == "user_id"
    assert relationship.target_table == "users"
    assert relationship.target_column == "id"
    assert relationship.relationship_type == "many-to-one"


def test_database_index_schema():
    index = DatabaseIndex(
        name="idx_users_email",
        table="users",
        columns=["email"],
        unique=True,
    )

    assert index.name == "idx_users_email"
    assert index.table == "users"
    assert index.columns == ["email"]
    assert index.unique is True


def test_database_design_schema():
    design = DatabaseDesignCreate(
        content=DatabaseDesignContent(
            tables=[
                DatabaseTable(
                    name="users",
                    description="Application users.",
                    columns=[
                        DatabaseColumn(
                            name="id",
                            type="UUID",
                            nullable=False,
                            primary_key=True,
                        ),
                        DatabaseColumn(
                            name="email",
                            type="VARCHAR(255)",
                            nullable=False,
                            unique=True,
                        ),
                    ],
                ),
                DatabaseTable(
                    name="projects",
                    description="User projects.",
                    columns=[
                        DatabaseColumn(
                            name="id",
                            type="UUID",
                            nullable=False,
                            primary_key=True,
                        ),
                        DatabaseColumn(
                            name="user_id",
                            type="UUID",
                            nullable=False,
                        ),
                    ],
                ),
            ],
            relationships=[
                DatabaseRelationship(
                    source_table="projects",
                    source_column="user_id",
                    target_table="users",
                    target_column="id",
                    relationship_type="many-to-one",
                )
            ],
            indexes=[
                DatabaseIndex(
                    name="idx_projects_user_id",
                    table="projects",
                    columns=["user_id"],
                )
            ],
        )
    )

    assert len(design.content.tables) == 2
    assert len(design.content.tables[0].columns) == 2
    assert len(design.content.relationships) == 1
    assert len(design.content.indexes) == 1

def test_component_create_schema():
    component = ComponentCreate(
        name="API Server",
        type="backend",
        technology="FastAPI",
        description="Handles REST API requests.",
    )

    assert component.name == "API Server"
    assert component.type == "backend"
    assert component.technology == "FastAPI"
    assert component.description == "Handles REST API requests."


def test_component_optional_fields():
    component = ComponentCreate(
        name="Load Balancer",
        type="infrastructure",
    )

    assert component.technology is None
    assert component.description is None


def test_connection_create_schema():
    connection = ConnectionCreate(
        source_component_id=1,
        target_component_id=2,
        protocol="HTTPS",
        description="Frontend communicates with the API server.",
    )

    assert connection.source_component_id == 1
    assert connection.target_component_id == 2
    assert connection.protocol == "HTTPS"
    assert connection.description == (
        "Frontend communicates with the API server."
    )


def test_architecture_decision_create_schema():
    decision = ArchitectureDecisionCreate(
        decision="Use PostgreSQL",
        rationale="The application requires relational data and transactions.",
        alternatives=[
            "MongoDB",
            "MySQL",
        ],
        tradeoffs="Requires a relational schema and migrations.",
    )

    assert decision.decision == "Use PostgreSQL"
    assert len(decision.alternatives) == 2
    assert decision.alternatives[0] == "MongoDB"
    assert decision.tradeoffs is not None


def test_architecture_create_schema():
    architecture = ArchitectureCreate(
        overview="A scalable web application architecture.",
        components=[
            ComponentCreate(
                name="Frontend",
                type="web",
                technology="Next.js",
                description="User-facing web application.",
            ),
            ComponentCreate(
                name="Backend",
                type="api",
                technology="FastAPI",
                description="Backend API service.",
            ),
            ComponentCreate(
                name="Database",
                type="database",
                technology="PostgreSQL",
            ),
        ],
        connections=[
            ConnectionCreate(
                source_component_id=1,
                target_component_id=2,
                protocol="HTTPS",
                description="Frontend calls backend API.",
            ),
            ConnectionCreate(
                source_component_id=2,
                target_component_id=3,
                protocol="PostgreSQL",
                description="Backend accesses the database.",
            ),
        ],
        decisions=[
            ArchitectureDecisionCreate(
                decision="Use FastAPI",
                rationale="Strong Python ecosystem and good async support.",
                alternatives=[
                    "Express.js",
                    "Django",
                ],
                tradeoffs="The team needs Python expertise.",
            )
        ],
    )

    assert architecture.overview == (
        "A scalable web application architecture."
    )

    assert len(architecture.components) == 3
    assert architecture.components[0].technology == "Next.js"
    assert architecture.components[2].technology == "PostgreSQL"

    assert len(architecture.connections) == 2
    assert architecture.connections[0].protocol == "HTTPS"
    assert architecture.connections[1].target_component_id == 3

    assert len(architecture.decisions) == 1
    assert architecture.decisions[0].decision == "Use FastAPI"
    assert len(architecture.decisions[0].alternatives) == 2


def test_prd_content_schema():
    content = PRDContent(
        title="AI Architect",
        problem_statement="Turning ideas into technical plans is time-consuming.",
        target_users=[
            "Software developers",
            "Startup founders",
        ],
        goals=[
            "Generate requirements",
            "Generate architecture",
        ],
        features=[
            "Requirements generation",
            "Architecture generation",
        ],
        user_stories=[
            "As a user, I want to describe my product idea."
        ],
        assumptions=[
            "The user can provide a basic product idea."
        ],
        out_of_scope=[
            "Generating production application code."
        ],
    )

    assert content.title == "AI Architect"
    assert len(content.target_users) == 2
    assert len(content.features) == 2


def test_prd_create_schema():
    prd = PRDCreate(
        content=PRDContent(
            title="AI Architect",
            problem_statement="Generate technical plans from ideas.",
        )
    )

    assert prd.content.title == "AI Architect"
    assert prd.content.target_users == []


def test_project_create_schema():
    project = ProjectCreate(
        name="AI Architect",
        idea="An AI system that turns product ideas into technical plans.",
    )

    assert project.name == "AI Architect"
    assert project.idea.startswith("An AI system")


def test_requirement_content_schema():
    content = RequirementContent(
        functional=[
            "Users can create projects",
            "Users can generate architecture",
        ],
        non_functional=[
            "API responses should be fast",
        ],
        constraints=[
            "Must use PostgreSQL",
        ],
    )

    assert len(content.functional) == 2
    assert len(content.non_functional) == 1
    assert len(content.constraints) == 1


def test_requirement_create_schema():
    requirement = RequirementCreate(
        content=RequirementContent(
            functional=["Users can create projects"],
        )
    )

    assert requirement.content.functional == [
        "Users can create projects"
    ]