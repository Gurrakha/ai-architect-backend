from fastapi import FastAPI
from app.api.routes.projects import router as project_router
from app.api.routes.requirements import router as requirements_router
from app.api.routes.prd import router as prd_router
from app.api.routes.architecture import router as architecture_router
from app.api.routes.database_design import router as database_design_router
from app.api.routes.api_design import router as api_design_router
from app.api.routes.roadmap import router as roadmap_router

from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres import PostgresSaver
from app.services.generation.graph import build_generation_graph
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    with PostgresSaver.from_conn_string(
        settings.DATABASE_URL,
    ) as checkpointer:
        checkpointer.setup()

        app.state.generation_graph = build_generation_graph(
            checkpointer,
        )

        yield

app = FastAPI(
    title="AI Architect API",
    version="0.1.0",
)

app.include_router(project_router)
app.include_router(requirements_router)
app.include_router(prd_router)
app.include_router(architecture_router)
app.include_router(database_design_router)
app.include_router(api_design_router)
app.include_router(roadmap_router)

@app.get("/health")
async def health():
    return {"status":"ok"}