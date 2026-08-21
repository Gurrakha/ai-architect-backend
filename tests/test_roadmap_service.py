import pytest

from app.models.api_design import APIDesign
from app.models.architecture import Architecture
from app.models.component import Component
from app.models.connection import Connection
from app.models.database_design import DatabaseDesign
from app.models.decision import ArchitectureDecision
from app.models.prd import PRD
from app.models.project import Project
from app.models.requirement import Requirement
from app.models.roadmap import Roadmap
from app.schemas.roadmap import RoadmapContent
from app.services.roadmap.service import RoadmapService


class FakeRoadmapAgent:
    def __init__(self):
        self.received_architecture = None

    async def generate(
        self,
        project_name: str,
        project_idea: str,
        requirements: dict,
        prd: dict,
        architecture: dict,
        database_design: dict,
        api_design: dict,
        clarifications: list[dict],
    ) -> RoadmapContent:
        self.received_architecture = architecture

        return RoadmapContent(
            phases=[
                {
                    "name": "Foundation",
                    "description": "Project foundation.",
                    "tasks": [
                        {
                            "title": "Set up backend",
                            "description": "Initialize backend services.",
                            "priority": "high",
                            "estimated_effort": "1 day",
                            "dependencies": [],
                        },
                    ],
                },
            ],
        )


class FakeDB:
    def __init__(self):
        self.project = None
        self.requirements = []
        self.prds = []
        self.architectures = []
        self.database_designs = []
        self.api_designs = []
        self.roadmaps = []

    def get(self, model, project_id):
        if model is Project and self.project:
            if self.project.id == project_id:
                return self.project

        return None

    def scalar(self, statement):
        column = statement.selected_columns[0]
        table_name = column.table.name

        if table_name == "requirements":
            records = self.requirements
        elif table_name == "prds":
            records = self.prds
        elif table_name == "architectures":
            records = self.architectures
        elif table_name == "database_designs":
            records = self.database_designs
        elif table_name == "api_designs":
            records = self.api_designs
        elif table_name == "roadmaps":
            records = self.roadmaps
        else:
            return None

        if not records:
            return None

        latest = max(
            records,
            key=lambda obj: obj.version,
        )

        if column.name == "version":
            return latest.version

        return latest

    def add(self, obj):
        if isinstance(obj, Roadmap):
            obj.id = len(self.roadmaps) + 1
            self.roadmaps.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        pass


@pytest.fixture
def db():
    return FakeDB()


@pytest.fixture
def project():
    return Project(
        id=1,
        name="AI Architect",
        idea=(
            "An AI system that turns product ideas "
            "into technical plans."
        ),
    )


@pytest.fixture
def requirements():
    return Requirement(
        id=1,
        project_id=1,
        version=1,
        content={
            "functional": ["Users can create projects"],
            "non_functional": ["The system should be reliable"],
            "constraints": ["Use PostgreSQL"],
        },
    )


@pytest.fixture
def prd():
    return PRD(
        id=1,
        project_id=1,
        version=1,
        content={
            "title": "AI Architect",
            "features": ["Project creation"],
        },
    )


@pytest.fixture
def architecture():
    architecture = Architecture(
        id=1,
        project_id=1,
        version=1,
        overview="A modular architecture.",
    )

    api = Component(
        id=1,
        architecture_id=1,
        name="API",
        type="backend",
        technology="FastAPI",
        description="Application API.",
    )

    database = Component(
        id=2,
        architecture_id=1,
        name="Database",
        type="database",
        technology="PostgreSQL",
        description="Application database.",
    )

    connection = Connection(
        id=1,
        architecture_id=1,
        source_component_id=1,
        target_component_id=2,
        protocol="SQL",
        description="API accesses database.",
    )

    decision = ArchitectureDecision(
        id=1,
        architecture_id=1,
        decision="Use PostgreSQL.",
        rationale="Relational data model.",
        alternatives=["MongoDB"],
        tradeoffs="Requires schema design.",
    )

    # Simulate SQLAlchemy relationships.
    connection.source_component = api
    connection.target_component = database

    architecture.components = [api, database]
    architecture.connections = [connection]
    architecture.decisions = [decision]

    return architecture


@pytest.fixture
def database_design():
    return DatabaseDesign(
        id=1,
        project_id=1,
        version=1,
        content={
            "tables": [
                {
                    "name": "projects",
                    "columns": [
                        {
                            "name": "id",
                            "type": "integer",
                        },
                    ],
                },
            ],
            "relationships": [],
            "indexes": [],
        },
    )


@pytest.fixture
def api_design():
    return APIDesign(
        id=1,
        project_id=1,
        version=1,
        content={
            "endpoints": [
                {
                    "method": "POST",
                    "path": "/projects",
                    "summary": "Create project",
                },
            ],
            "conventions": [],
        },
    )


@pytest.fixture
def agent():
    return FakeRoadmapAgent()


def populate_dependencies(
    db,
    project,
    requirements,
    prd,
    architecture,
    database_design,
    api_design,
):
    db.project = project
    db.requirements.append(requirements)
    db.prds.append(prd)
    db.architectures.append(architecture)
    db.database_designs.append(database_design)
    db.api_designs.append(api_design)


@pytest.mark.anyio
async def test_generate_roadmap(
    db,
    agent,
    project,
    requirements,
    prd,
    architecture,
    database_design,
    api_design,
):
    populate_dependencies(
        db,
        project,
        requirements,
        prd,
        architecture,
        database_design,
        api_design,
    )

    service = RoadmapService(
        db=db,
        agent=agent,
    )

    roadmap = await service.generate(
        project_id=1,
    )

    assert roadmap.project_id == 1
    assert roadmap.version == 1

    assert roadmap.content["phases"][0]["name"] == "Foundation"
    assert (
        roadmap.content["phases"][0]["tasks"][0]["title"]
        == "Set up backend"
    )


@pytest.mark.anyio
async def test_generate_roadmap_passes_component_names(
    db,
    agent,
    project,
    requirements,
    prd,
    architecture,
    database_design,
    api_design,
):
    populate_dependencies(
        db,
        project,
        requirements,
        prd,
        architecture,
        database_design,
        api_design,
    )

    service = RoadmapService(
        db=db,
        agent=agent,
    )

    await service.generate(project_id=1)

    received = agent.received_architecture

    assert received["components"][0]["name"] == "API"
    assert received["components"][1]["name"] == "Database"

    assert received["connections"][0]["source_component"] == "API"
    assert received["connections"][0]["target_component"] == "Database"

    assert "source_component_id" not in received["connections"][0]
    assert "target_component_id" not in received["connections"][0]


@pytest.mark.anyio
async def test_generate_roadmap_increments_version(
    db,
    agent,
    project,
    requirements,
    prd,
    architecture,
    database_design,
    api_design,
):
    populate_dependencies(
        db,
        project,
        requirements,
        prd,
        architecture,
        database_design,
        api_design,
    )

    service = RoadmapService(
        db=db,
        agent=agent,
    )

    first = await service.generate(project_id=1)
    second = await service.generate(project_id=1)

    assert first.version == 1
    assert second.version == 2
    assert len(db.roadmaps) == 2


@pytest.mark.anyio
async def test_generate_roadmap_project_not_found(
    db,
    agent,
):
    service = RoadmapService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="Project 999 not found",
    ):
        await service.generate(project_id=999)


@pytest.mark.anyio
async def test_generate_roadmap_requirements_not_found(
    db,
    agent,
    project,
):
    db.project = project

    service = RoadmapService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="No requirements found for project 1",
    ):
        await service.generate(project_id=1)


@pytest.mark.anyio
async def test_generate_roadmap_prd_not_found(
    db,
    agent,
    project,
    requirements,
):
    db.project = project
    db.requirements.append(requirements)

    service = RoadmapService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="No PRD found for project 1",
    ):
        await service.generate(project_id=1)


@pytest.mark.anyio
async def test_generate_roadmap_architecture_not_found(
    db,
    agent,
    project,
    requirements,
    prd,
):
    db.project = project
    db.requirements.append(requirements)
    db.prds.append(prd)

    service = RoadmapService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="No architecture found for project 1",
    ):
        await service.generate(project_id=1)


@pytest.mark.anyio
async def test_generate_roadmap_database_design_not_found(
    db,
    agent,
    project,
    requirements,
    prd,
    architecture,
):
    db.project = project
    db.requirements.append(requirements)
    db.prds.append(prd)
    db.architectures.append(architecture)

    service = RoadmapService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="No database design found for project 1",
    ):
        await service.generate(project_id=1)


@pytest.mark.anyio
async def test_generate_roadmap_api_design_not_found(
    db,
    agent,
    project,
    requirements,
    prd,
    architecture,
    database_design,
):
    db.project = project
    db.requirements.append(requirements)
    db.prds.append(prd)
    db.architectures.append(architecture)
    db.database_designs.append(database_design)

    service = RoadmapService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="No API design found for project 1",
    ):
        await service.generate(project_id=1)
