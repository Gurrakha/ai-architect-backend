from fastapi import FastAPI
from app.api.routes.projects import router as project_router
from app.api.routes.requirements import router as requirements_router

app = FastAPI(
    title="AI Architect API",
    version="0.1.0",
)

app.include_router(project_router)
app.include_router(requirements_router)

@app.get("/health")
async def health():
    return {"status":"ok"}