import pytest

from app.models.clarification import Clarification
from app.models.generation import Generation, GenerationStatus
from app.models.prd import PRD
from app.models.project import Project
from app.models.requirement import Requirement
from app.services.ai.schemas.clarification import ClarificationGeneration
from app.services.clarification.service import ClarificationService


class FakeClarificationAgent:
    def __init__(self):
        self.project_name = None
        self.project_idea = None
        self.requirements = None
        self.prd = None

    async def generate(
        self,
        project_name: str,
        project_idea: str,
        requirements: dict,
        prd: dict,
    ) -> ClarificationGeneration:
        self.project_name = project_name
        self.project_idea = project_idea
        self.requirements = requirements
        self.prd = prd

        return ClarificationGeneration(
            needs_clarification=True,
            questions=[
                {
                    "question": "Who can create projects?",
                    "reason": (
                        "Authorization requirements are needed "
                        "for the architecture."
                    ),
                },
                {
                    "question": "Should projects be private?",
                    "reason": (
                        "Visibility affects authorization and "
                        "data-access design."
                    ),
                },
            ],
        )


class FakeDB:
    def __init__(self):
        self.project = None
        self.generations = []
        self.requirements = []
        self.prds = []
        self.clarifications = []

    def get(self, model, object_id):
        if model is Project:
            if self.project and self.project.id == object_id:
                return self.project

        elif model is Generation:
            for generation in self.generations:
                if generation.id == object_id:
                    return generation

        elif model is Clarification:
            for clarification in self.clarifications:
                if clarification.id == object_id:
                    return clarification

        return None

    def scalar(self, statement):
        column = statement.selected_columns[0]
        table_name = column.table.name

        if table_name == "requirements":
            records = self.requirements
        elif table_name == "prds":
            records = self.prds
        else:
            return None

        if not records:
            return None

        return max(
            records,
            key=lambda obj: obj.version,
        )

    def add(self, obj):
        if isinstance(obj, Clarification):
            obj.id = len(self.clarifications) + 1
            self.clarifications.append(obj)

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
def generation():
    return Generation(
        id=1,
        project_id=1,
        workflow="full_generation",
        status=GenerationStatus.RUNNING,
        model="gemini",
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
    return FakeClarificationAgent()


@pytest.mark.anyio
async def test_generate_clarifications(
    db,
    project,
    generation,
    requirements,
    prd,
    agent,
):
    db.project = project
    db.generations.append(generation)

    service = ClarificationService(
        db=db,
        agent=agent,
    )

    clarifications = await service.generate(
        project_id=1,
        generation_id=1,
        requirements=requirements.content,
        prd=prd.content,
    )

    assert len(clarifications) == 2

    first = clarifications[0]

    assert first.id == 1
    assert first.project_id == 1
    assert first.generation_id == 1
    assert first.question == "Who can create projects?"
    assert first.reason == (
        "Authorization requirements are needed "
        "for the architecture."
    )

    assert agent.project_name == project.name
    assert agent.project_idea == project.idea
    assert agent.requirements == requirements.content
    assert agent.prd == prd.content


@pytest.mark.anyio
async def test_generate_clarifications_when_not_needed(
    db,
    project,
    generation,
    requirements,
    prd,
):
    class NoClarificationAgent:
        async def generate(
            self,
            project_name: str,
            project_idea: str,
            requirements: dict,
            prd: dict,
        ) -> ClarificationGeneration:
            return ClarificationGeneration(
                needs_clarification=False,
            )

    db.project = project
    db.generations.append(generation)

    service = ClarificationService(
        db=db,
        agent=NoClarificationAgent(),
    )

    clarifications = await service.generate(
        project_id=1,
        generation_id=1,
        requirements=requirements.content,
        prd=prd.content,
    )

    assert clarifications == []
    assert db.clarifications == []


def test_answer_clarification(
    db,
    project,
):
    clarification = Clarification(
        id=1,
        project_id=1,
        generation_id=1,
        question="Who can create projects?",
        reason="Authorization is required.",
    )

    db.project = project
    db.clarifications.append(clarification)

    service = ClarificationService(
        db=db,
        agent=FakeClarificationAgent(),
    )

    result = service.answer(
        project_id=1,
        generation_id=1,
        clarification_id=1,
        answer="Only authenticated users.",
    )

    assert result.answer == "Only authenticated users."
    assert result.answered_at is not None


@pytest.mark.anyio
async def test_generate_project_not_found(
    db,
    agent,
):
    service = ClarificationService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="Project 999 not found",
    ):
        await service.generate(
            project_id=999,
            generation_id=1,
            requirements={},
            prd={},
        )


@pytest.mark.anyio
async def test_generate_generation_not_found(
    db,
    project,
    agent,
):
    db.project = project

    service = ClarificationService(
        db=db,
        agent=agent,
    )

    with pytest.raises(
        ValueError,
        match="Generation 999 not found",
    ):
        await service.generate(
            project_id=1,
            generation_id=999,
            requirements={},
            prd={},
        )


def test_answer_clarification_not_found(
    db,
):
    service = ClarificationService(
        db=db,
        agent=FakeClarificationAgent(),
    )

    with pytest.raises(
        ValueError,
        match="Clarification 999 not found",
    ):
        service.answer(
            project_id=1,
            generation_id=1,
            clarification_id=999,
            answer="Answer",
        )

def test_answer_clarification_wrong_generation(
    db,
    project,
):
    clarification = Clarification(
        id=1,
        project_id=1,
        generation_id=2,
        question="Who can create projects?",
        reason="Authorization is required.",
    )

    db.project = project
    db.clarifications.append(clarification)

    service = ClarificationService(
        db=db,
        agent=FakeClarificationAgent(),
    )

    with pytest.raises(
        ValueError,
        match="Clarification 1 not found",
    ):
        service.answer(
            project_id=1,
            generation_id=1,
            clarification_id=1,
            answer="Only authenticated users.",
        )