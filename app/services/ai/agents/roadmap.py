from app.schemas.roadmap import RoadmapContent
from app.services.ai.provider import AIProvider


class RoadmapAgent:
    """Generates a structured implementation roadmap."""

    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    async def generate(
        self,
        project_name: str,
        project_idea: str,
        requirements: dict,
        prd: dict,
        architecture: dict,
        database_design: dict,
        api_design: dict,
        clarifications: list[dict],
    ) -> RoadmapContent:
        prompt = f"""
            You are a senior software engineering project planner.

            Create a structured implementation roadmap for the following
            software project.

            Project name:
            {project_name}

            Project idea:
            {project_idea}

            Requirements:
            {requirements}

            Product Requirements Document:
            {prd}

            System Architecture:
            {architecture}

            Database Design:
            {database_design}

            API Design:
            {api_design}

            User-provided clarifications:
            {clarifications}

            Produce a practical implementation roadmap organized into
            logical development phases.

            Each phase should contain implementation tasks.

            For each task provide:

            - title
            - description
            - priority
            - estimated effort
            - dependencies

            Important rules:

            - Base the roadmap primarily on the project idea,
              requirements, PRD, architecture, database design,
              API design, and user-provided clarifications.
            - Treat answered clarifications as explicit user requirements
              and account for them when prioritizing and sequencing roadmap work.
            - Order phases and tasks according to sensible implementation
              dependencies.
            - Do not invent highly specific requirements.
            - Do not introduce technologies that are not supported by the
              provided architecture and database/API designs.
            - Keep tasks concrete enough that a development team could use
              them for implementation planning.
            - Avoid duplicate tasks.
            - Keep descriptions concise.
            - Dependencies should refer to task titles when applicable.
            - Do not include application implementation code.
        """

        return await self.provider.generate_structured(
            prompt=prompt,
            output_schema=RoadmapContent,
        )