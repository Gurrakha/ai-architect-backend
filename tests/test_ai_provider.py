from pydantic import BaseModel

from app.services.ai.provider import AIProvider


class AIProviderOutput(BaseModel):
    message: str


def test_ai_provider_is_abstract():
    try:
        AIProvider()
        assert False, "AIProvider should not be directly instantiable"
    except TypeError:
        pass