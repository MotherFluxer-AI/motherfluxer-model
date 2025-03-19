from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime, timezone

from .model.model_manager import ModelManager
from .utils.config import Settings
from .api.websocket import websocket_endpoint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    try:
        model_manager = ModelManager()
        await model_manager.initialize()
        app.state.model_manager = model_manager  # Store in app state
        logger.info("Model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize model: {e}")
        raise
    yield
    # Shutdown
    print("Shutting down...")

# Initialize FastAPI app
app = FastAPI(title="MotherFluxer Model Container", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a dependency function to get settings
def get_settings():
    return Settings()

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Server is running"}

@app.websocket("/ws")
async def websocket_simple_route(websocket: WebSocket):
    """WebSocket endpoint that uses the websocket implementation"""
    await websocket_endpoint(websocket)