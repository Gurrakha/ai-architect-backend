from app.schemas.requirement import RequirementContent
from app.services.ai.provider import AIProvider


class RequirementsAgent:
    """Generates structured software requirements from a project idea."""

    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    async def generate(
        self,
        project_name: str,
        project_idea: str,
    ) -> RequirementContent:
        prompt = f"""
            You are a senior software requirements analyst.

            Analyze the following software project idea and produce a structured
            requirements specification.

            Project name:
            {project_name}

            Project idea:
            {project_idea}

            Identify:

            1. Functional requirements:
            What the system must be able to do.

            2. Non-functional requirements:
            Performance, scalability, security, reliability, usability,
            maintainability, or other quality requirements that are reasonably
            implied by the project.

            3. Constraints:
            Explicit technical, business, platform, budget, compliance, or
            implementation constraints mentioned or strongly implied by the idea.

            Important rules:

            - Do not invent highly specific business requirements that are not
            reasonably supported by the project idea.
            - Keep requirements concrete and implementation-independent where possible.
            - Avoid duplicates.
            - Return concise, meaningful requirements.
            - If something is genuinely unknown, do not fabricate it.
        """

        return await self.provider.generate_structured(
            prompt=prompt,
            output_schema=RequirementContent,
        )