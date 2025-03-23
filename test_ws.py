import asyncio
import websockets
import json
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def send_message(websocket, message):
    chat_message = {
        "type": "chat",
        "message": message,
        "parameters": {
            "temperature": 0.7,
            "max_length": 100
        }
    }
    await websocket.send(json.dumps(chat_message))
    logger.info("Message sent, waiting for response...")

async def receive_messages(websocket):
    while True:
        try:
            response = await websocket.recv()
            logger.info(f"Received: {response}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection closed by server")
            break
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            break

async def test_connection():
    uri = "ws://localhost:8000/ws?token=0d9faed892236a06ba75a6149e3c0658728450f591a3eddc6cb7b4018c3745cc"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connected to WebSocket server")
            
            # Start message receiver task
            receiver_task = asyncio.create_task(receive_messages(websocket))
            
            # Interactive message sending
            while True:
                try:
                    # Get input from user
                    message = input("\nEnter message (or 'quit' to exit): ")
                    if message.lower() == 'quit':
                        break
                    
                    # Send the message
                    await send_message(websocket, message)
                    
                except KeyboardInterrupt:
                    logger.info("Exiting...")
                    break
                except Exception as e:
                    logger.error(f"Error sending message: {e}")
                    break
            
            # Cancel the receiver task
            receiver_task.cancel()
            
    except websockets.exceptions.ConnectionClosed:
        logger.info("Connection closed normally")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(test_connection())
    except KeyboardInterrupt:
        logger.info("Program terminated by user") 