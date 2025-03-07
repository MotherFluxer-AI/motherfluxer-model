from fastapi import WebSocket
from ..utils.auth import extract_token_from_header, verify_token
from ..utils.rate_limiter import RateLimiter
import json
from typing import Dict, Any, Literal
from fastapi import WebSocketDisconnect
from ..model.model_manager import ModelManager

MessageType = Literal["chat", "system"]

# Initialize rate limiter with 5 messages per minute
rate_limiter = RateLimiter(messages_per_minute=5)

async def handle_chat_message(websocket: WebSocket, message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle chat messages using the model manager"""
    try:
        # Get model manager from app state
        model_manager = websocket.app.state.model_manager
        
        # Extract the message text and parameters
        message_text = message.get("message", "")
        parameters = message.get("parameters", {})
        
        # Generate response using the model
        response = await model_manager.generate(
            prompt=message_text,
            **parameters
        )
        
        return {
            "response": response,
            "type": "chat",
            "code": 200
        }
    except Exception as e:
        return {
            "error": str(e),
            "type": "chat",
            "code": 500
        }

async def handle_system_message(command: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Handle system messages including authentication"""
    print(f"\nHandling system message: command={command}, data={data}")  # Debug print
    
    if command == "ping":
        return {
            "response": "pong",
            "type": "system",
            "code": 200
        }
    elif command == "auth":
        # Match the auth response format from the main websocket
        print(f"Processing auth command with data: {data}")  # Debug print
        if data and data.get("token") == "test-token-123":
            response = {
                "type": "system",
                "status": "authenticated",
                "code": 200
            }
            print(f"Auth successful, sending response: {response}")  # Debug print
            return response
        else:
            response = {
                "type": "system",
                "status": "error",
                "message": "Authentication failed",
                "code": 4001
            }
            print(f"Auth failed, sending response: {response}")  # Debug print
            return response
    
    return {
        "error": "Unknown system command",
        "type": "system",
        "code": 4004
    }

async def websocket_endpoint(websocket: WebSocket):
    client_host = websocket.client.host
    print(f"\n=== Starting websocket connection from {client_host} ===")
    print(f"Headers: {websocket.headers}")
    print(f"Query params: {websocket.query_params}")
    
    # Try to get token from header first
    auth_header = websocket.headers.get("authorization")
    token = extract_token_from_header(auth_header)
    
    # If no token in header, try query parameter
    if not token:
        token = websocket.query_params.get("token")
        print(f"Using token from query parameter: {token}")
    
    print(f"Auth header: {auth_header}, query token: {websocket.query_params.get('token')}, extracted token: {token}")
    
    if not token or not verify_token(token):
        print(f"Initial auth header verification failed. Token: {token}")
        await websocket.close(code=4001)
        return
    
    print("Authentication successful, accepting connection")
    await websocket.accept()
    
    # Track if the user has authenticated via message
    authenticated_via_message = False
    
    try:
        # Keep connection open and handle multiple messages
        while True:
            data = await websocket.receive_json()
            print(f"Received websocket message: {data}")
            
            if not isinstance(data, dict):
                print(f"Invalid message format: {data}")
                await websocket.send_json({
                    "error": "Invalid message format",
                    "type": "system",
                    "code": 4002
                })
                continue
                
            # Handle both auth message formats
            is_auth_message = (
                (data.get('type') == 'auth') or  # Main websocket format
                (data.get('type') == 'system' and data.get('message') == 'auth')  # Simple websocket format
            )
            
            if is_auth_message:
                # Use the same token verification as the initial check
                token_from_message = data.get('token')
                if verify_token(token_from_message):  # Use our verify_token function
                    authenticated_via_message = True
                    await websocket.send_json({
                        "status": "authenticated",
                        "type": "system"
                    })
                else:
                    await websocket.send_json({
                        "status": "error",
                        "message": "Authentication failed",
                        "type": "system"
                    })
                continue
                
            # Regular message handling
            if 'type' not in data or 'message' not in data:
                print(f"Invalid message format: {data}")
                await websocket.send_json({
                    "error": "Invalid message format",
                    "type": "system",
                    "code": 4002
                })
                continue
                
            if data['type'] not in ['chat', 'system']:
                print(f"Invalid message type: {data['type']}")
                await websocket.send_json({
                    "error": "Invalid message type",
                    "type": "system",
                    "code": 4003
                })
                continue
                
            if data['type'] == 'chat':
                response = await handle_chat_message(websocket, data)
            else:  # system
                response = await handle_system_message(data.get('message', ''), data)
                
            print(f"Sending response: {response}")
            await websocket.send_json(response)
                
    except json.JSONDecodeError:
        print("JSON decode error")
        await websocket.send_json({
            "error": "Invalid JSON",
            "type": "system",
            "code": 4005
        })
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in websocket: {str(e)}")
        if websocket.client_state.CONNECTED:
            await websocket.close(code=1000) 