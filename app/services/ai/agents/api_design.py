from app.schemas.api_design import APIDesignContent
from app.services.ai.provider import AIProvider


class APIDesignAgent:
    """Generates a structured API design from project artifacts."""

    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    async def generate(
        self,
        project_name: str,
        project_idea: str,
        requirements: dict,
        architecture: dict,
        database_design: dict,
    ) -> APIDesignContent:
        prompt = f"""
            You are a senior backend architect and API designer.

            Design a clear, consistent API for the following software project.

            Project name:
            {project_name}

            Project idea:
            {project_idea}

            Functional and non-functional requirements:
            {requirements}

            System architecture:
            {architecture}

            Database design:
            {database_design}

            Produce a structured API design containing:

            1. Endpoints
            Define the HTTP endpoints required to support the project's
            functional requirements.

            For each endpoint specify:
            - HTTP method
            - resource path
            - concise summary
            - description
            - authentication requirements when applicable
            - request parameters and request body when applicable
            - expected responses and status codes

            2. API conventions
            Define important conventions such as:
            - resource naming
            - HTTP method usage
            - error response conventions
            - pagination conventions when applicable
            - authentication conventions when applicable
            - versioning conventions when applicable

            Important rules:

            - Derive endpoints primarily from the requirements.
            - Use the architecture to understand system boundaries and
              component interactions.
            - Use the database design to understand the data exposed or
              modified by the API.
            - Do not automatically expose CRUD endpoints for every database
              table.
            - Do not invent functionality that is not reasonably supported
              by the provided requirements.
            - Keep endpoint paths and methods consistent.
            - Avoid duplicate endpoints.
            - Keep descriptions concise and meaningful.
            - Do not introduce technologies unless they are explicitly
              supported by the provided project artifacts.
            - If authentication requirements are genuinely unknown, do not
              fabricate a specific authentication mechanism.
        """

        return await self.provider.generate_structured(
            prompt=prompt,
            output_schema=APIDesignContent,
        )