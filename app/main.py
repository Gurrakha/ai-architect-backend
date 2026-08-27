from fastapi import FastAPI
from app.api.routes.projects import router as project_router
from app.api.routes.requirements import router as requirements_router
from app.api.routes.prd import router as prd_router
from app.api.routes.architecture import router as architecture_router
from app.api.routes.database_design import router as database_design_router
from app.api.routes.api_design import router as api_design_router
from app.api.routes.roadmap import router as roadmap_router
from app.api.routes.generation import router as generation_router
from app.api.routes.events import router as events_router

from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.core.config import settings

from fastapi.middleware.cors import CORSMiddleware
import asyncio
import sys

print("sys.platform=", sys.platform)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncPostgresSaver.from_conn_string(
        settings.DATABASE_URL.replace(
            "postgresql+psycopg://",
            "postgresql://",
        ),
    ) as checkpointer:
        await checkpointer.setup()

        app.state.checkpointer = checkpointer

        yield

app = FastAPI(
    title="AI Architect API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(project_router)
app.include_router(requirements_router)
app.include_router(prd_router)
app.include_router(architecture_router)
app.include_router(database_design_router)
app.include_router(api_design_router)
app.include_router(roadmap_router)
app.include_router(generation_router)
app.include_router(events_router)


@app.get("/health")
async def health():
    return {"status":"ok"}