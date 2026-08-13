from app.services.ai.schemas.architecture import ArchitectureGeneration
from app.services.ai.provider import AIProvider


class ArchitectureAgent:
    """Generates a structured software architecture."""

    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    async def generate(
        self,
        project_name: str,
        project_idea: str,
        requirements: dict,
        prd: dict,
    ) -> ArchitectureGeneration:
        prompt = f"""
            You are a senior software architect.

            Design a high-level software architecture for the following project.

            Project name:
            {project_name}

            Project idea:
            {project_idea}

            Previously generated requirements:
            {requirements}

            Previously generated PRD:
            {prd}

            Produce a structured architecture containing:

            1. Overview
            Provide a concise description of the proposed architecture and
            how its major parts interact.

            2. Components
            Identify the major architectural components.

            For each component provide:
            - name
            - type
            - technology, only when reasonably justified
            - description

            3. Connections
            Identify the important communication or dependency relationships
            between components.

            For each connection provide:
            - source component name
            - target component name
            - protocol, when applicable
            - description

            The source_component and target_component values must exactly
            match component names from the components list.

            4. Architecture decisions
            Identify important architectural decisions.

            For each decision provide:
            - decision
            - rationale
            - alternatives
            - tradeoffs

            Important rules:

            - Base the architecture primarily on the project idea,
              requirements, and PRD.
            - Do not invent highly specific requirements.
            - Prefer simple, maintainable architecture.
            - Do not introduce unnecessary components.
            - Technologies should only be suggested when reasonably justified.
            - Every connection must reference components that actually exist
              in the components list.
            - Avoid duplicate components and connections.
            - Keep the architecture at a high level.
        """

        return await self.provider.generate_structured(
            prompt=prompt,
            output_schema=ArchitectureGeneration,
        )