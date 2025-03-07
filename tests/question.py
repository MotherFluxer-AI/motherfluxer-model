import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_model():
    uri = "ws://localhost:8000/ws"
    
    # Get token from environment and print it
    auth_token = os.getenv("AUTH_TOKEN")
    print(f"Using token: {auth_token}")
    
    extra_headers = {
        "Origin": "http://localhost:8000",
        "Authorization": f"Bearer {auth_token}"
    }
    
    print(f"Full Authorization header: {extra_headers['Authorization']}")
    
    async with websockets.connect(uri, extra_headers=extra_headers) as websocket:
        message = {
            "type": "chat",
            "message": "What is the capital of France?",
            "parameters": {
                "temperature": 0.7,
                "max_length": 100
            }
        }
        
        await websocket.send(json.dumps(message))
        response = await websocket.recv()
        print(f"Model response: {response}")

asyncio.get_event_loop().run_until_complete(test_model())