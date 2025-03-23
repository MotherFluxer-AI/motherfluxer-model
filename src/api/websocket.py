from fastapi import WebSocket
from ..utils.auth import extract_token_from_header, verify_token
import json
from typing import Dict, Any, Literal, Union, Optional
from fastapi import WebSocketDisconnect
from ..model.model_manager import ModelManager
import logging

# Configure logging
logger = logging.getLogger(__name__)

MessageType = Literal["chat", "system"]

def create_error_response(error: str, code: int) -> Dict[str, Any]:
    """Create a standardized error response"""
    return {
        "error": error,
        "type": "system",
        "code": code
    }

def create_success_response(response: Union[str, Dict[str, Any]], message_type: MessageType) -> Dict[str, Any]:
    """Create a standardized success response"""
    return {
        "response": response,
        "type": message_type,
        "code": 200
    }

def create_auth_response(success: bool, message: str = None) -> Dict[str, Any]:
    """Create a standardized authentication response"""
    if success:
        return {
            "status": "authenticated",
            "type": "system"
        }
    return {
        "status": "error",
        "message": message or "Authentication failed",
        "type": "system"
    }

def is_valid_message_type(message_type: str) -> bool:
    """Check if the message type is valid"""
    return message_type in ['chat', 'system']

def is_auth_message(data: Dict[str, Any]) -> bool:
    """Check if the message is an authentication message"""
    return (
        data.get('type') == 'auth' or 
        (data.get('type') == 'system' and data.get('message') == 'auth')
    )

async def handle_chat_message(websocket: WebSocket, message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle chat messages using the model manager"""
    try:
        model_manager = websocket.app.state.model_manager
        message_text = message.get("message", "")
        parameters = message.get("parameters", {})
        
        response = await model_manager.generate(
            prompt=message_text,
            **parameters
        )
        
        return create_success_response(response, "chat")
    except Exception as e:
        return create_error_response(str(e), 500)

async def handle_system_message(command: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Handle system messages including authentication"""
    if command == "ping":
        return create_success_response("pong", "system")
    elif command == "auth":
        token = data.get("token")
        logger.debug(f"System message auth - Token from request: {token}")
        if data and verify_token(token):
            logger.debug("System message auth successful")
            return create_auth_response(True)
        logger.debug("System message auth failed")
        return create_auth_response(False)
    
    return create_error_response("Unknown system command", 4004)

async def verify_websocket_auth(websocket: WebSocket) -> bool:
    """Verify websocket authentication from either header or query params"""
    auth_header = websocket.headers.get("authorization")
    token = extract_token_from_header(auth_header) or websocket.query_params.get("token")
    logger.debug(f"WebSocket auth - Token from request: {token}")
    result = bool(token and verify_token(token))
    logger.debug(f"WebSocket auth result: {result}")
    return result

async def handle_message(websocket: WebSocket, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle a single message and return the response"""
    if not isinstance(data, dict) or 'type' not in data:
        return create_error_response("Invalid message format", 4002)
        
    # Handle authentication message - maintaining exact format for UI compatibility
    if is_auth_message(data):
        token = data.get('token')
        logger.debug(f"Message auth - Token from request: {token}")
        result = bool(token and verify_token(token))
        logger.debug(f"Message auth result: {result}")
        return create_auth_response(result)
        
    # Handle regular messages
    if not is_valid_message_type(data['type']):
        return create_error_response("Invalid message type", 4003)
        
    return await (
        handle_chat_message(websocket, data)
        if data['type'] == 'chat'
        else handle_system_message(data.get('message', ''), data)
    )

async def websocket_endpoint(websocket: WebSocket):
    """Main websocket endpoint handler"""
    if not await verify_websocket_auth(websocket):
        await websocket.close(code=4001)
        return

    await websocket.accept()
    
    try:
        while True:
            try:
                data = await websocket.receive_json()
                response = await handle_message(websocket, data)
                if response:
                    await websocket.send_json(response)
            except json.JSONDecodeError:
                await websocket.send_json(create_error_response("Invalid JSON", 4005))
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in websocket connection: {e}")
                break
    finally:
        if websocket.client_state.CONNECTED:
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing websocket: {e}") 