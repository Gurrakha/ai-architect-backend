from typing import TypeVar

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from app.core.config import settings
from app.services.ai.provider import AIProvider

T = TypeVar("T", bound=BaseModel)


class GeminiProvider(AIProvider):
    """Gemini implementation of the AI provider."""

    def __init__(self) -> None:
        self.model = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0,
        )

    async def generate_structured(
        self,
        prompt: str,
        output_schema: type[T],
    ) -> T:
        structured_model = self.model.with_structured_output(
            output_schema,
            method="json_schema",
        )

        response = await structured_model.ainvoke(prompt)

        return response