from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.agent.graph import graph

router = APIRouter()

class UploadResponse(BaseModel):
    uris: List[str]

class ExtractRequest(BaseModel):
    file_uris: List[str]

from fastapi import UploadFile, File
from google.cloud import storage
import uuid
from app.core.config import settings

@router.post("/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Uploads files to GCS and returns their URIs.
    """
    uris = []
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(settings.GCS_BUCKET_NAME)
        
        for file in files:
            # Generate unique filename to prevent collisions
            filename = f"{uuid.uuid4()}_{file.filename}"
            blob = bucket.blob(filename)
            
            # Upload from file-like object
            blob.upload_from_file(file.file, content_type=file.content_type)
            
            uris.append(f"gs://{settings.GCS_BUCKET_NAME}/{filename}")
            
    except Exception as e:
        print(f"Upload failed: {e}")
        # For local dev without GCS creds, fallback to mock URIs if needed, 
        # but ideally we want to fail fast or use a local emulator.
        # Raising HTTP exception for better visibility
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
        
    return {"uris": uris}

@router.post("/extract")
async def start_extraction(request: ExtractRequest):
    """
    Triggers the LangGraph workflow.
    """
    initial_state = {"file_uris": request.file_uris}
    
    # Run the graph
    # Note: ainvoke is async. In a real app, we'd use a background task (Celery/Arq)
    # or LangGraph's async streaming to avoid blocking the request.
    try:
        result = await graph.ainvoke(initial_state)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
