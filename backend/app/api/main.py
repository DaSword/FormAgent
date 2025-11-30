from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/")
async def root():
    return {"message": "Doc Extractor Agent API is running"}

from app.api.routes import workflow

app.include_router(workflow.router, prefix="/api/v1", tags=["workflow"])
