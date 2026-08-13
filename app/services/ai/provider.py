from abc import ABC, abstractmethod
from typing import TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class AIProvider(ABC):
    """Abstract interface for AI model providers."""

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        output_schema: type[T],
    ) -> T:
        """Generate a structured response from the AI model."""
        raise NotImplementedError