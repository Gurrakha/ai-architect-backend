import pytest

from app.models.database_design import DatabaseDesign
from app.models.prd import PRD
from app.models.project import Project
from app.models.requirement import Requirement
from app.schemas.database_design import DatabaseDesignContent
from app.services.database_design.service import DatabaseDesignService


class FakeDatabaseDesignAgent:
    async def generate(
        self,
        project_name: str,
        project_idea: str,
        requirements: dict,
        prd: dict,
    ) -> DatabaseDesignContent:
        return DatabaseDesignContent(
            tables=[
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
                    ],
                },
            ],
            relationships=[],
            indexes=[],
        )


class FakeDB:
    def __init__(self):
        self.project = None
        self.requirements = []
        self.prds = []
        self.database_designs = []

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
        elif table_name == "database_designs":
            records = self.database_designs
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
        if isinstance(obj, DatabaseDesign):
            obj.id = len(self.database_designs) + 1
            self.database_designs.append(obj)

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
def agent():
    return FakeDatabaseDesignAgent()


@pytest.mark.anyio
async def test_generate_database_design(
    db,
    agent,
    project,
    requirements,
    prd,
):
    db.project = project
    db.requirements.append(requirements)
    db.prds.append(prd)

    service = DatabaseDesignService(
        db=db,
        agent=agent,
    )

    database_design = await service.generate(
        project_id=1,
    )

    assert database_design.project_id == 1
    assert database_design.version == 1

    assert database_design.content["tables"][0]["name"] == "projects"
    assert (
        database_design.content["tables"][0]["columns"][0]["name"]
        == "id"
    )


@pytest.mark.anyio
async def test_generate_database_design_increments_version(
    db,
    agent,
    project,
    requirements,
    prd,
):
    db.project = project
    db.requirements.append(requirements)
    db.prds.append(prd)

    service = DatabaseDesignService(
        db=db,
        agent=agent,
    )

    first = await service.generate(project_id=1)
    second = await service.generate(project_id=1)

    assert first.version == 1
    assert second.version == 2

    assert len(db.database_designs) == 2


@pytest.mark.anyio
async def test_generate_database_design_project_not_found(
    db,
    agent,
):
    service = DatabaseDesignService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="Project 999 not found",
    ):
        await service.generate(project_id=999)


@pytest.mark.anyio
async def test_generate_database_design_requirements_not_found(
    db,
    agent,
    project,
    prd,
):
    db.project = project
    db.prds.append(prd)

    service = DatabaseDesignService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="No requirements found for project 1",
    ):
        await service.generate(project_id=1)


@pytest.mark.anyio
async def test_generate_database_design_prd_not_found(
    db,
    agent,
    project,
    requirements,
):
    db.project = project
    db.requirements.append(requirements)

    service = DatabaseDesignService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="No PRD found for project 1",
    ):
        await service.generate(project_id=1)