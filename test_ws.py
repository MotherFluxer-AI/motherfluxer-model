import asyncio
import websockets
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_connection():
    uri = "ws://localhost:8000/ws?token=0d9faed892236a06ba75a6149e3c0658728450f591a3eddc6cb7b4018c3745cc"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connected to WebSocket server")
            
            # Send chat message with parameters matching proxy format
            chat_message = {
                "type": "chat",
                "message": "Hello, this is a test message!",
                "parameters": {
                    "temperature": 0.7,
                    "max_length": 100
                }
            }
            
            logger.info("Sending chat message...")
            await websocket.send(json.dumps(chat_message))
            
            # Wait for and print the response
            response = await websocket.recv()
            logger.info(f"Received response: {response}")
            
            # Keep connection open and handle messages like proxy
            while True:
                try:
                    # Wait for any additional messages
                    response = await websocket.recv()
                    logger.info(f"Received additional response: {response}")
                except websockets.exceptions.ConnectionClosed:
                    logger.info("Connection closed by server")
                    break
                except Exception as e:
                    logger.error(f"Error receiving message: {e}")
                    break
            
    except websockets.exceptions.ConnectionClosed:
        logger.info("Connection closed normally")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection()) 