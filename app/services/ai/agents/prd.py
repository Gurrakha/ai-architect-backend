from app.schemas.prd import PRDContent
from app.services.ai.provider import AIProvider


class PRDAgent:
    """Generates a structured product requirements document."""

    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    async def generate(
        self,
        project_name: str,
        project_idea: str,
        requirements: dict,
    ) -> PRDContent:
        prompt = f"""
            You are a senior product manager and software product analyst.

            Create a structured Product Requirements Document (PRD) for the
            following software project.

            Project name:
            {project_name}

            Project idea:
            {project_idea}

            Previously generated requirements:
            {requirements}

            Produce a clear, concise PRD containing:

            1. Title
            A concise name for the product.

            2. Problem statement
            Clearly describe the problem the product is intended to solve.

            3. Target users
            Identify the primary users or user groups.

            4. Goals
            Identify the key outcomes the product should achieve.

            5. Features
            Identify the major product features derived from the project idea
            and requirements.

            6. User stories
            Describe the important user interactions using concise
            "As a ..., I want ..., so that ..." statements.

            7. Assumptions
            List reasonable assumptions required to interpret the project.

            8. Out of scope
            Clearly identify functionality that should not be considered
            part of the initial product scope.

            Important rules:

            - Base the PRD primarily on the project idea and requirements.
            - Do not invent highly specific business requirements.
            - Keep the PRD implementation-independent where possible.
            - Do not introduce technologies unless they are explicitly present
            in the provided requirements.
            - Avoid duplicate features or user stories.
            - Keep each item concise and meaningful.
            - If information is genuinely unknown, make a reasonable high-level
            assumption rather than fabricating specific details.
        """

        return await self.provider.generate_structured(
            prompt=prompt,
            output_schema=PRDContent,
        )