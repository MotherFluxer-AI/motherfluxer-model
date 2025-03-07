import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from src.main import app
from contextlib import asynccontextmanager

@pytest.fixture
def mock_app():
    @asynccontextmanager
    async def mock_lifespan(app: FastAPI):
        print("Starting up with mock lifespan...")
        yield
        print("Shutting down mock lifespan...")
    
    app.router.lifespan_context = mock_lifespan
    return app

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}

def test_websocket_connection(mock_app, auth_headers):
    """Test successful WebSocket authentication"""
    print("Starting WebSocket connection test")
    
    with TestClient(mock_app) as client:
        with client.websocket_connect("/ws", headers=auth_headers) as websocket:
            print("WebSocket connected")
            
            auth_message = {
                "type": "system",
                "message": "auth",
                "token": "test-token-123"
            }
            print(f"Sending auth message: {auth_message}")
            websocket.send_json(auth_message)
            
            response = websocket.receive_json()
            print(f"Received response: {response}")
            
            assert response["type"] == "system"
            assert response["status"] == "authenticated"

def test_websocket_invalid_auth(mock_app, auth_headers):
    """Test failed WebSocket authentication"""
    print("Starting invalid auth test")
    
    with TestClient(mock_app) as client:
        with client.websocket_connect("/ws", headers=auth_headers) as websocket:
            auth_message = {
                "type": "system",
                "message": "auth",
                "token": "invalid-token"
            }
            websocket.send_json(auth_message)
            
            response = websocket.receive_json()
            assert response["type"] == "system"
            assert response["status"] == "error"
            assert response["message"] == "Authentication failed"

def test_websocket_no_auth_headers(mock_app):
    """Test connection without auth headers should fail"""
    with TestClient(mock_app) as client:
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect("/ws") as websocket:
                pass
        assert exc_info.value.code == 4001 