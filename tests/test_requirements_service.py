import pytest

from app.models.project import Project
from app.models.requirement import Requirement
from app.schemas.requirement import RequirementContent
from app.services.requirements.service import RequirementsService


class FakeRequirementsAgent:
    async def generate(
        self,
        project_name: str,
        project_idea: str,
    ) -> RequirementContent:
        return RequirementContent(
            functional=[
                "Users can create projects",
                "Users can generate requirements",
            ],
            non_functional=[
                "The system should be reliable",
            ],
            constraints=[
                "The system should use PostgreSQL",
            ],
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
        self.added = []

    def get(self, model, project_id):
        if model is Project and self.project:
            if self.project.id == project_id:
                return self.project

        return None

    def scalar(self, statement):
        if not self.requirements:
            return None

        return max(
            requirement.version
            for requirement in self.requirements
        )

    def add(self, obj):
        self.added.append(obj)

        if isinstance(obj, Requirement):
            obj.id = len(self.requirements) + 1
            self.requirements.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        pass


@pytest.mark.anyio
async def test_generate_requirements():
    db = FakeDB()

    project = Project(
        id=1,
        name="AI Architect",
        idea="An AI system that turns product ideas into technical plans.",
    )

    db.project = project

    service = RequirementsService(
        db=db,
        agent=FakeRequirementsAgent(),
    )

    requirement = await service.generate(
        project_id=1,
    )

    assert requirement.project_id == 1
    assert requirement.version == 1

    assert requirement.content["functional"] == [
        "Users can create projects",
        "Users can generate requirements",
    ]

    assert requirement.content["non_functional"] == [
        "The system should be reliable",
    ]

    assert requirement.content["constraints"] == [
        "The system should use PostgreSQL",
    ]


@pytest.mark.anyio
async def test_generate_requirements_increments_version():
    db = FakeDB()

    project = Project(
        id=1,
        name="AI Architect",
        idea="An AI system that turns product ideas into technical plans.",
    )

    db.project = project

    service = RequirementsService(
        db=db,
        agent=FakeRequirementsAgent(),
    )

    first = await service.generate(project_id=1)
    second = await service.generate(project_id=1)

    assert first.version == 1
    assert second.version == 2

    assert len(db.requirements) == 2


@pytest.mark.anyio
async def test_generate_requirements_project_not_found():
    db = FakeDB()

    service = RequirementsService(
        db=db,
        agent=FakeRequirementsAgent(),
    )

    with pytest.raises(ValueError, match="Project 999 not found"):
        await service.generate(project_id=999)