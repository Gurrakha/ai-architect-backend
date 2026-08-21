from app.schemas.database_design import DatabaseDesignContent
from app.services.ai.provider import AIProvider


class DatabaseDesignAgent:
    """Generates a structured database design from project context."""

    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    async def generate(
        self,
        project_name: str,
        project_idea: str,
        requirements: dict,
        prd: dict,
        clarifications: list[dict]
    ) -> DatabaseDesignContent:
        prompt = f"""
            You are a senior database architect.

            Design a logical database schema for the following software
            project.

            Project name:
            {project_name}

            Project idea:
            {project_idea}

            Previously generated requirements:
            {requirements}

            Previously generated PRD:
            {prd}

            User-provided clarifications:
            {clarifications}

            Produce a structured database design containing:

            1. Tables
            Identify the core tables required by the product.

            For each table provide:
            - A clear table name.
            - Its purpose.
            - The columns required to support the product.
            - Appropriate data types.
            - Whether each column is nullable.
            - Primary key and uniqueness constraints where appropriate.
            - Reasonable defaults where appropriate.
            - A concise description of each column.

            2. Relationships
            Identify relationships between tables.

            For each relationship provide:
            - Source table and column.
            - Target table and column.
            - Relationship type.

            3. Indexes
            Identify indexes that are reasonably justified by the requirements
            and expected access patterns.

            Important rules:

            - Base the database design primarily on the project idea,
              requirements, PRD, architecture, and user-provided clarifications.
            - Treat answered clarifications as explicit user requirements
              and incorporate them into the database design where relevant.
            - Do not invent highly specific business requirements.
            - Avoid unnecessary tables or columns.
            - Use conventional relational database design principles.
            - Avoid redundant data where possible.
            - Every relationship must reference columns that actually exist
              in the generated tables.
            - Every index must reference a table and columns that actually
              exist.
            - Use clear and consistent naming.
            - Do not introduce a specific database technology unless it is
              explicitly required by the project.
            - Keep the design implementation-independent where possible.
            - Do not fabricate unknown business rules.
        """

        return await self.provider.generate_structured(
            prompt=prompt,
            output_schema=DatabaseDesignContent,
        )