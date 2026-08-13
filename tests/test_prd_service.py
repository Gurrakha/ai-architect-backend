import pytest

from app.models.prd import PRD
from app.models.project import Project
from app.models.requirement import Requirement
from app.schemas.prd import PRDContent
from app.services.prd.service import PRDService


class FakePRDAgent:
    async def generate(
        self,
        project_name: str,
        project_idea: str,
        requirements: dict,
    ) -> PRDContent:
        assert project_name == "AI Architect"
        assert project_idea == (
            "An AI system that turns product ideas into technical plans."
        )

        assert requirements["functional"] == [
            "Users can create projects",
            "Users can generate requirements",
        ]

        return PRDContent(
            title="AI Architect",
            problem_statement="Turn product ideas into technical plans.",
            target_users=["Software developers"],
            goals=["Reduce architecture planning effort"],
            features=["Project creation", "Requirements generation"],
            user_stories=[
                "As a user, I want to create a project so that I can plan it."
            ],
            assumptions=["Users provide a project idea."],
            out_of_scope=["Application implementation"],
        )


class FakeScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar(self):
        return self.value


class FakeDB:
    def __init__(self):
        self.project = None
        self.requirements = []
        self.prds = []
        self.added = []

    def get(self, model, project_id):
        if model is Project and self.project:
            if self.project.id == project_id:
                return self.project

        return None

    def scalar(self, statement):
        # Requirement lookup
        if "requirements" in str(statement):
            if not self.requirements:
                return None

            return max(
                self.requirements,
                key=lambda requirement: requirement.version,
            )

        # PRD version lookup
        if not self.prds:
            return None

        return max(
            prd.version
            for prd in self.prds
        )

    def add(self, obj):
        self.added.append(obj)

        if isinstance(obj, PRD):
            obj.id = len(self.prds) + 1
            self.prds.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        pass


def create_project():
    return Project(
        id=1,
        name="AI Architect",
        idea="An AI system that turns product ideas into technical plans.",
    )


def create_requirement(version=1):
    return Requirement(
        id=version,
        project_id=1,
        version=version,
        content={
            "functional": [
                "Users can create projects",
                "Users can generate requirements",
            ],
            "non_functional": [
                "The system should be reliable",
            ],
            "constraints": [
                "The system should use PostgreSQL",
            ],
        },
    )


@pytest.mark.anyio
async def test_generate_prd():
    db = FakeDB()
    db.project = create_project()
    db.requirements.append(create_requirement())

    service = PRDService(
        db=db,
        agent=FakePRDAgent(),
    )

    prd = await service.generate(project_id=1)

    assert prd.project_id == 1
    assert prd.version == 1

    assert prd.content["title"] == "AI Architect"

    assert prd.content["features"] == [
        "Project creation",
        "Requirements generation",
    ]


@pytest.mark.anyio
async def test_generate_prd_increments_version():
    db = FakeDB()
    db.project = create_project()
    db.requirements.append(create_requirement())

    service = PRDService(
        db=db,
        agent=FakePRDAgent(),
    )

    first = await service.generate(project_id=1)
    second = await service.generate(project_id=1)

    assert first.version == 1
    assert second.version == 2

    assert len(db.prds) == 2


@pytest.mark.anyio
async def test_generate_prd_uses_latest_requirements():
    db = FakeDB()
    db.project = create_project()

    db.requirements.append(
        create_requirement(version=1)
    )

    db.requirements.append(
        create_requirement(version=2)
    )

    service = PRDService(
        db=db,
        agent=FakePRDAgent(),
    )

    prd = await service.generate(project_id=1)

    assert prd.version == 1


@pytest.mark.anyio
async def test_generate_prd_project_not_found():
    db = FakeDB()

    service = PRDService(
        db=db,
        agent=FakePRDAgent(),
    )

    with pytest.raises(
        ValueError,
        match="Project 999 not found",
    ):
        await service.generate(project_id=999)


@pytest.mark.anyio
async def test_generate_prd_requirements_not_found():
    db = FakeDB()
    db.project = create_project()

    service = PRDService(
        db=db,
        agent=FakePRDAgent(),
    )

    with pytest.raises(
        ValueError,
        match="No requirements found for project 1",
    ):
        await service.generate(project_id=1)