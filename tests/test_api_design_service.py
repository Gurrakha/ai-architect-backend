import pytest

from app.models.api_design import APIDesign
from app.models.architecture import Architecture
from app.models.component import Component
from app.models.connection import Connection
from app.models.database_design import DatabaseDesign
from app.models.decision import ArchitectureDecision
from app.models.project import Project
from app.models.requirement import Requirement
from app.schemas.api_design import APIDesignContent
from app.services.api_design.service import APIDesignService

class FakeDB:
    def __init__(self):
        self.project = None
        self.requirements = []
        self.architectures = []
        self.database_designs = []
        self.api_designs = []

    def get(self, model, object_id):
        if model is Project:
            if self.project and self.project.id == object_id:
                return self.project

        return None

    def scalar(self, statement):
        column = statement.selected_columns[0]

        if column.table.name == "requirements":
            matching = self.requirements
        elif column.table.name == "architectures":
            matching = self.architectures
        elif column.table.name == "database_designs":
            matching = self.database_designs
        elif column.table.name == "api_designs":
            matching = self.api_designs
        else:
            return None

        if not matching:
            return None

        latest = max(
            matching,
            key=lambda obj: obj.version,
        )

        if column.name == "version":
            return latest.version

        return latest

    def add(self, obj):
        if isinstance(obj, APIDesign):
            obj.id = len(self.api_designs) + 1
            self.api_designs.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        pass

@pytest.fixture
def db():
    return FakeDB()


@pytest.fixture
def agent():
    return FakeAPIDesignAgent()


@pytest.fixture
def project(db):
    project = Project(
        id=1,
        name="AI Architect",
        idea=(
            "An AI system that turns product ideas "
            "into technical plans."
        ),
    )

    db.project = project

    return project


@pytest.fixture
def requirements(db):
    requirement = Requirement(
        id=1,
        project_id=1,
        version=1,
        content={
            "functional": [
                "Users can create projects",
            ],
            "non_functional": [
                "The system should be reliable",
            ],
            "constraints": [
                "The system should use PostgreSQL",
            ],
        },
    )

    db.requirements.append(requirement)

    return requirement

@pytest.fixture
def architecture(db):
    architecture = Architecture(
        id=1,
        project_id=1,
        version=1,
        overview="A modular web application architecture.",
    )

    api = Component(
        id=1,
        architecture_id=1,
        name="API",
        type="backend",
        technology="FastAPI",
        description="Handles application requests.",
    )

    database = Component(
        id=2,
        architecture_id=1,
        name="Database",
        type="database",
        technology="PostgreSQL",
        description="Stores application data.",
    )

    connection = Connection(
        id=1,
        architecture_id=1,
        source_component_id=1,
        target_component_id=2,
        protocol="SQL",
        description="API reads and writes application data.",
    )

    connection.source_component = api
    connection.target_component = database

    decision = ArchitectureDecision(
        id=1,
        architecture_id=1,
        decision="Use PostgreSQL.",
        rationale="The project requires relational storage.",
        alternatives=["MongoDB"],
        tradeoffs="Requires relational schema design.",
    )

    architecture.components = [api, database]
    architecture.connections = [connection]
    architecture.decisions = [decision]

    db.architectures.append(architecture)

    return architecture

@pytest.fixture
def database_design(db):
    design = DatabaseDesign(
        id=1,
        project_id=1,
        version=1,
        content={
            "tables": [
                {
                    "name": "projects",
                    "description": "Stores projects.",
                    "columns": [
                        {
                            "name": "id",
                            "type": "integer",
                            "nullable": False,
                            "primary_key": True,
                            "unique": True,
                        },
                        {
                            "name": "name",
                            "type": "varchar",
                            "nullable": False,
                        },
                    ],
                }
            ],
            "relationships": [],
            "indexes": [],
        },
    )

    db.database_designs.append(design)

    return design


class FakeAPIDesignAgent:
    def __init__(self):
        self.received = None

    async def generate(
        self,
        project_name: str,
        project_idea: str,
        requirements: dict,
        architecture: dict,
        database_design: dict,
    ) -> APIDesignContent:
        self.received = {
            "project_name": project_name,
            "project_idea": project_idea,
            "requirements": requirements,
            "architecture": architecture,
            "database_design": database_design,
        }

        return APIDesignContent(
            endpoints=[
                {
                    "method": "POST",
                    "path": "/projects",
                    "summary": "Create a project",
                    "description": "Create a new project.",
                    "authentication": None,
                    "request": {
                        "content_type": "application/json",
                        "parameters": [],
                        "body": {
                            "name": "string",
                            "idea": "string",
                        },
                    },
                    "responses": [
                        {
                            "status_code": 201,
                            "description": "Project created successfully.",
                            "content_type": "application/json",
                            "body": {
                                "id": 1,
                            },
                        }
                    ],
                }
            ],
            conventions=[
                "Use plural resource names.",
                "Use standard HTTP status codes.",
            ],
        )


@pytest.mark.anyio
async def test_generate_api_design(
    db,
    agent,
    project,
    requirements,
    architecture,
    database_design,
):
    service = APIDesignService(
        db=db,
        agent=agent,
    )

    api_design = await service.generate(
        project_id=1,
    )

    assert api_design.project_id == 1
    assert api_design.version == 1

    assert api_design.content["endpoints"][0]["method"] == "POST"
    assert api_design.content["endpoints"][0]["path"] == "/projects"

    assert len(db.api_designs) == 1

@pytest.mark.anyio
async def test_generate_api_design_passes_required_context(
    db,
    agent,
    project,
    requirements,
    architecture,
    database_design,
):
    service = APIDesignService(
        db=db,
        agent=agent,
    )

    await service.generate(project_id=1)

    assert agent.received["project_name"] == "AI Architect"

    assert agent.received["requirements"] == requirements.content

    assert agent.received["architecture"]["overview"] == (
        "A modular web application architecture."
    )

    assert len(agent.received["architecture"]["components"]) == 2

    assert (
        agent.received["architecture"]["components"][0]["name"]
        == "API"
    )

    assert agent.received["architecture"]["connections"][0][
        "source_component"
    ] == "API"

    assert agent.received["architecture"]["connections"][0][
        "target_component"
    ] == "Database"

    assert (
        agent.received["database_design"]
        == database_design.content
    )

@pytest.mark.anyio
async def test_generate_api_design_increments_version(
    db,
    agent,
    project,
    requirements,
    architecture,
    database_design,
):
    service = APIDesignService(
        db=db,
        agent=agent,
    )

    first = await service.generate(project_id=1)
    second = await service.generate(project_id=1)

    assert first.version == 1
    assert second.version == 2

    assert len(db.api_designs) == 2

@pytest.mark.anyio
async def test_generate_api_design_project_not_found(
    db,
    agent,
):
    service = APIDesignService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="Project 999 not found",
    ):
        await service.generate(project_id=999)


@pytest.mark.anyio
async def test_generate_api_design_without_requirements(
    db,
    agent,
    project,
):
    service = APIDesignService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="No requirements found for project 1",
    ):
        await service.generate(project_id=1)


@pytest.mark.anyio
async def test_generate_api_design_without_architecture(
    db,
    agent,
    project,
    requirements,
):
    service = APIDesignService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="No architecture found for project 1",
    ):
        await service.generate(project_id=1)


@pytest.mark.anyio
async def test_generate_api_design_without_database_design(
    db,
    agent,
    project,
    requirements,
    architecture,
):
    service = APIDesignService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="No database design found for project 1",
    ):
        await service.generate(project_id=1)