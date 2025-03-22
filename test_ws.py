import asyncio
import websockets
import json

async def test_connection():
    uri = "ws://localhost:8000/ws?token=0d9faed892236a06ba75a6149e3c0658728450f591a3eddc6cb7b4018c3745cc"
   
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server!")
            
            # Send a test message
            test_message = {
                "type": "chat",
                "message": "Hello, this is a test message!"
            }
            
            await websocket.send(json.dumps(test_message))
            
            # Wait for and print the response
            response = await websocket.recv()
            print(f"Received response: {response}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection()) 