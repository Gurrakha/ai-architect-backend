from fastapi import FastAPI

app = FastAPI(
    title="AI Architect API",
    version="0.1.0",
)

@app.get("/health")
async def health():
    return {"status":"ok"}