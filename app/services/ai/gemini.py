import asyncio

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.services.ai.provider import AIProvider


class GeminiProvider(AIProvider):
    MAX_ATTEMPTS = 3
    RETRY_DELAYS = (1, 2)

    def __init__(self) -> None:
        self.model = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0,
        )

    async def generate_structured(
        self,
        prompt: str,
        output_schema: type,
    ):
        structured_model = self.model.with_structured_output(
            output_schema,
            method="json_schema",
        )

        for attempt in range(self.MAX_ATTEMPTS):
            try:
                print(
                    f"[Gemini] Request attempt {attempt + 1}/{self.MAX_ATTEMPTS} "
                    f"model={settings.GEMINI_MODEL} "
                    f"schema={output_schema.__name__}"
                )
                response = await structured_model.ainvoke(prompt)
                print(
                    f"[Gemini] Success "
                    f"model={settings.GEMINI_MODEL} "
                    f"schema={output_schema.__name__}"
                )
                return response

            except Exception as exc:
                if not self._is_retryable(exc):
                    raise

                # Last attempt: let the original exception propagate.
                if attempt == self.MAX_ATTEMPTS - 1:
                    raise

                await asyncio.sleep(self.RETRY_DELAYS[attempt])

    @staticmethod
    def _is_retryable(exc: Exception) -> bool:
        message = str(exc).lower()

        retryable_statuses = (
            "500",
            "502",
            "503",
            "504",
            "service unavailable",
            "internal server error",
            "bad gateway",
            "gateway timeout",
            "timeout",
            "timed out",
            "temporarily unavailable",
        )

        return any(status in message for status in retryable_statuses)