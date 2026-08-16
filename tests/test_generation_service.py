import pytest

from app.models.generation import Generation, GenerationStatus
from app.services.generation.service import GenerationService


class FakeDB:
    def __init__(self):
        self.generations = []

    def get(self, model, object_id):
        if model is Generation:
            for generation in self.generations:
                if generation.id == object_id:
                    return generation

        return None

    def add(self, obj):
        if isinstance(obj, Generation):
            obj.id = len(self.generations) + 1
            self.generations.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        pass


@pytest.fixture
def db():
    return FakeDB()


@pytest.fixture
def service(db):
    return GenerationService(db=db)


@pytest.fixture
def generation():
    return Generation(
        id=1,
        project_id=1,
        workflow="full_generation",
        status=GenerationStatus.PENDING,
        model="gemini",
    )


def test_create_generation(
    service,
    db,
):
    generation = service.create(
        project_id=1,
        workflow="full_generation",
        model="gemini",
    )

    assert generation.id == 1
    assert generation.project_id == 1
    assert generation.workflow == "full_generation"
    assert generation.model == "gemini"
    assert generation.status == GenerationStatus.PENDING


def test_start_generation(
    service,
    db,
    generation,
):
    db.generations.append(generation)

    result = service.start(
        generation_id=1,
    )

    assert result.status == GenerationStatus.RUNNING
    assert result.started_at is not None


def test_wait_for_input(
    service,
    db,
    generation,
):
    db.generations.append(generation)

    result = service.wait_for_input(
        generation_id=1,
    )

    assert result.status == GenerationStatus.WAITING_FOR_INPUT


def test_complete_generation(
    service,
    db,
    generation,
):
    db.generations.append(generation)

    result = service.complete(
        generation_id=1,
    )

    assert result.status == GenerationStatus.COMPLETED
    assert result.completed_at is not None


def test_fail_generation(
    service,
    db,
    generation,
):
    db.generations.append(generation)

    result = service.fail(
        generation_id=1,
        error="Generation failed.",
    )

    assert result.status == GenerationStatus.FAILED
    assert result.error == "Generation failed."


def test_start_generation_not_found(
    service,
):
    with pytest.raises(
        ValueError,
        match="Generation 999 not found",
    ):
        service.start(
            generation_id=999,
        )


def test_wait_for_input_not_found(
    service,
):
    with pytest.raises(
        ValueError,
        match="Generation 999 not found",
    ):
        service.wait_for_input(
            generation_id=999,
        )


def test_complete_generation_not_found(
    service,
):
    with pytest.raises(
        ValueError,
        match="Generation 999 not found",
    ):
        service.complete(
            generation_id=999,
        )


def test_fail_generation_not_found(
    service,
):
    with pytest.raises(
        ValueError,
        match="Generation 999 not found",
    ):
        service.fail(
            generation_id=999,
            error="Generation failed.",
        )