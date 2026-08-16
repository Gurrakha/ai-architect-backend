from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.db.session import SessionLocal
from app.services.ai.agents.api_design import APIDesignAgent
from app.services.ai.agents.architecture import ArchitectureAgent
from app.services.ai.agents.database_design import DatabaseDesignAgent
from app.services.ai.agents.prd import PRDAgent
from app.services.ai.agents.requirements import RequirementsAgent
from app.services.ai.agents.roadmap import RoadmapAgent
from app.services.ai.gemini import GeminiProvider
from app.services.api_design.service import APIDesignService
from app.services.architecture.service import ArchitectureService
from app.services.database_design.service import DatabaseDesignService
from app.services.prd.service import PRDService
from app.services.requirements.service import RequirementsService
from app.services.roadmap.service import RoadmapService


class GenerationState(TypedDict):
    project_id: int
    generation_id: int

    project_name: str
    project_idea: str

    requirements: dict | None
    prd: dict | None
    architecture: dict | None
    database_design: dict | None
    api_design: dict | None
    roadmap: dict | None

    clarifications: list[dict]


async def generate_requirements(
    state: GenerationState,
) -> dict:
    db = SessionLocal()

    try:
        provider = GeminiProvider()
        agent = RequirementsAgent(provider)
        service = RequirementsService(db, agent)

        requirement = await service.generate(
            project_id=state["project_id"],
        )

        return {
            "requirements": requirement.content,
        }

    finally:
        db.close()


async def generate_prd(
    state: GenerationState,
) -> dict:
    db = SessionLocal()

    try:
        provider = GeminiProvider()
        agent = PRDAgent(provider)
        service = PRDService(db, agent)

        prd = await service.generate(
            project_id=state["project_id"],
            requirements=state["requirements"],
        )

        return {
            "prd": prd.content,
        }

    finally:
        db.close()


async def generate_architecture(
    state: GenerationState,
) -> dict:
    db = SessionLocal()

    try:
        provider = GeminiProvider()
        agent = ArchitectureAgent(provider)
        service = ArchitectureService(db, agent)

        architecture = await service.generate(
            project_id=state["project_id"],
            requirements=state["requirements"],
            prd=state["prd"],
        )

        return {
            "architecture": {
                "overview": architecture.overview,
                "components": [
                    {
                        "name": component.name,
                        "type": component.type,
                        "technology": component.technology,
                        "description": component.description,
                    }
                    for component in architecture.components
                ],
                "connections": [
                    {
                        "source_component": connection.source_component.name,
                        "target_component": connection.target_component.name,
                        "protocol": connection.protocol,
                        "description": connection.description,
                    }
                    for connection in architecture.connections
                ],
                "decisions": [
                    {
                        "decision": decision.decision,
                        "rationale": decision.rationale,
                        "alternatives": decision.alternatives,
                        "tradeoffs": decision.tradeoffs,
                    }
                    for decision in architecture.decisions
                ],
            }
        }

    finally:
        db.close()


async def generate_database_design(
    state: GenerationState,
) -> dict:
    db = SessionLocal()

    try:
        provider = GeminiProvider()
        agent = DatabaseDesignAgent(provider)
        service = DatabaseDesignService(db, agent)

        database_design = await service.generate(
            project_id=state["project_id"],
            requirements=state["requirements"],
            prd=state["prd"],
        )

        return {
            "database_design": database_design.content,
        }

    finally:
        db.close()

async def generate_api_design(
    state: GenerationState,
) -> dict:
    db = SessionLocal()

    try:
        provider = GeminiProvider()
        agent = APIDesignAgent(provider)
        service = APIDesignService(db, agent)

        api_design = await service.generate(
            project_id=state["project_id"],
            requirements=state["requirements"],
            architecture=state["architecture"],
            database_design=state["database_design"],
        )

        return {
            "api_design": api_design.content,
        }

    finally:
        db.close()

async def generate_roadmap(
    state: GenerationState,
) -> dict:
    db = SessionLocal()

    try:
        provider = GeminiProvider()
        agent = RoadmapAgent(provider)
        service = RoadmapService(db, agent)

        roadmap = await service.generate(
            project_id=state["project_id"],
            requirements=state["requirements"],
            prd=state["prd"],
            architecture=state["architecture"],
            database_design=state["database_design"],
            api_design=state["api_design"],
        )

        return {
            "roadmap": roadmap.content,
        }

    finally:
        db.close()


def build_generation_graph():
    graph = StateGraph(GenerationState)

    graph.add_node(
        "requirements",
        generate_requirements,
    )

    graph.add_node(
        "prd",
        generate_prd,
    )

    graph.add_node(
        "architecture",
        generate_architecture,
    )

    graph.add_node(
        "database_design",
        generate_database_design,
    )

    graph.add_node(
        "api_design",
        generate_api_design,
    )

    graph.add_node(
        "roadmap",
        generate_roadmap,
    )

    graph.add_edge(
        START,
        "requirements",
    )

    graph.add_edge(
        "requirements",
        "prd",
    )

    graph.add_edge(
        "prd",
        "architecture",
    )

    graph.add_edge(
        "architecture",
        "database_design",
    )

    graph.add_edge(
        "database_design",
        "api_design",
    )

    
    graph.add_edge(
        "api_design",
        "roadmap",
    )

    graph.add_edge(
        "roadmap",
        END,
    )

    return graph.compile()