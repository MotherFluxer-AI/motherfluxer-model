from fastapi import APIRouter, WebSocket, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class InferenceRequest(BaseModel):
    message: str
    context: Optional[List[str]] = None
    parameters: Optional[dict] = None

class InferenceResponse(BaseModel):
    text: str
    usage: dict

# Remove the conflicting websocket endpoint
# The websocket handling is now in main.py 