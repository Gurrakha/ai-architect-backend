import pytest

from app.models.architecture import Architecture
from app.models.component import Component
from app.models.connection import Connection
from app.models.decision import ArchitectureDecision
from app.models.prd import PRD
from app.models.project import Project
from app.models.requirement import Requirement
from app.services.ai.schemas.architecture import ArchitectureGeneration
from app.services.architecture.service import ArchitectureService


class FakeArchitectureAgent:
    async def generate(
        self,
        project_name: str,
        project_idea: str,
        requirements: dict,
        prd: dict,
    ) -> ArchitectureGeneration:
        return ArchitectureGeneration(
            overview="A modular web application architecture.",
            components=[
                {
                    "name": "API",
                    "type": "backend",
                    "technology": "FastAPI",
                    "description": "Handles application requests.",
                },
                {
                    "name": "Database",
                    "type": "database",
                    "technology": "PostgreSQL",
                    "description": "Stores application data.",
                },
            ],
            connections=[
                {
                    "source_component": "API",
                    "target_component": "Database",
                    "protocol": "SQL",
                    "description": "API reads and writes application data.",
                },
            ],
            decisions=[
                {
                    "decision": "Use PostgreSQL.",
                    "rationale": "The project requires relational storage.",
                    "alternatives": ["MongoDB"],
                    "tradeoffs": "Requires relational schema design.",
                },
            ],
        )

class FakeDB:
    def __init__(self):
        self.project = None
        self.requirements = []
        self.prds = []
        self.architectures = []
        self.components = []
        self.connections = []
        self.decisions = []

    def get(self, model, object_id):
        if model is Project:
            if self.project and self.project.id == object_id:
                return self.project

        return None

    def scalar(self, statement):
        column = statement.selected_columns[0]

        if column.table.name == "requirements":
            matching = self.requirements

        elif column.table.name == "prds":
            matching = self.prds

        elif column.table.name == "architectures":
            matching = self.architectures

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
        if isinstance(obj, Architecture):
            obj.id = len(self.architectures) + 1
            self.architectures.append(obj)

        elif isinstance(obj, Component):
            obj.id = len(self.components) + 1
            self.components.append(obj)

        elif isinstance(obj, Connection):
            obj.id = len(self.connections) + 1
            self.connections.append(obj)

        elif isinstance(obj, ArchitectureDecision):
            obj.id = len(self.decisions) + 1
            self.decisions.append(obj)

    def flush(self):
        pass

    def commit(self):
        pass

    def refresh(self, obj):
        pass


@pytest.fixture
def db():
    return FakeDB()


@pytest.fixture
def agent():
    return FakeArchitectureAgent()


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
def prd(db):
    prd = PRD(
        id=1,
        project_id=1,
        version=1,
        content={
            "title": "AI Architect",
            "problem_statement": (
                "Turn product ideas into technical plans."
            ),
        },
    )

    db.prds.append(prd)

    return prd


@pytest.mark.anyio
async def test_generate_architecture(
    db,
    agent,
    project,
    requirements,
    prd,
):
    service = ArchitectureService(
        db=db,
        agent=agent,
    )

    architecture = await service.generate(
        project_id=1,
    )

    assert architecture.project_id == 1
    assert architecture.version == 1
    assert architecture.overview == (
        "A modular web application architecture."
    )

    assert len(db.architectures) == 1
    assert len(db.components) == 2
    assert len(db.connections) == 1
    assert len(db.decisions) == 1


@pytest.mark.anyio
async def test_generate_architecture_creates_components(
    db,
    agent,
    project,
    requirements,
    prd,
):
    service = ArchitectureService(
        db=db,
        agent=agent,
    )

    await service.generate(project_id=1)

    api = db.components[0]
    database = db.components[1]

    assert api.id == 1
    assert api.architecture_id == 1
    assert api.name == "API"
    assert api.type == "backend"
    assert api.technology == "FastAPI"

    assert database.id == 2
    assert database.architecture_id == 1
    assert database.name == "Database"
    assert database.technology == "PostgreSQL"


@pytest.mark.anyio
async def test_generate_architecture_resolves_connections(
    db,
    agent,
    project,
    requirements,
    prd,
):
    service = ArchitectureService(
        db=db,
        agent=agent,
    )

    await service.generate(project_id=1)

    connection = db.connections[0]

    assert connection.architecture_id == 1
    assert connection.source_component_id == 1
    assert connection.target_component_id == 2
    assert connection.protocol == "SQL"


@pytest.mark.anyio
async def test_generate_architecture_creates_decisions(
    db,
    agent,
    project,
    requirements,
    prd,
):
    service = ArchitectureService(
        db=db,
        agent=agent,
    )

    await service.generate(project_id=1)

    decision = db.decisions[0]

    assert decision.architecture_id == 1
    assert decision.decision == "Use PostgreSQL."
    assert decision.rationale == (
        "The project requires relational storage."
    )
    assert decision.alternatives == ["MongoDB"]
    assert decision.tradeoffs == (
        "Requires relational schema design."
    )


@pytest.mark.anyio
async def test_generate_architecture_increments_version(
    db,
    agent,
    project,
    requirements,
    prd,
):
    service = ArchitectureService(
        db=db,
        agent=agent,
    )

    first = await service.generate(project_id=1)
    second = await service.generate(project_id=1)

    assert first.version == 1
    assert second.version == 2

    assert len(db.architectures) == 2


@pytest.mark.anyio
async def test_generate_architecture_project_not_found(
    db,
    agent,
):
    service = ArchitectureService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="Project 999 not found",
    ):
        await service.generate(project_id=999)


@pytest.mark.anyio
async def test_generate_architecture_without_requirements(
    db,
    agent,
    project,
):
    service = ArchitectureService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="No requirements found for project 1",
    ):
        await service.generate(project_id=1)


@pytest.mark.anyio
async def test_generate_architecture_without_prd(
    db,
    agent,
    project,
    requirements,
):
    service = ArchitectureService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="No PRD found for project 1",
    ):
        await service.generate(project_id=1)