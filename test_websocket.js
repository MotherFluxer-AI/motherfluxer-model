const WebSocket = require('ws');

// Replace these with your actual values
const WEBSOCKET_URL = 'ws://213.173.99.23:8000/ws';  // Direct IP address
const AUTH_TOKEN = '0d9faed892236a06ba75a6149e3c0658728450f591a3eddc6cb7b4018c3745cc';  // Replace with your auth token from .env file

// Connect to the WebSocket server with the token in query parameters
const ws = new WebSocket(`${WEBSOCKET_URL}?token=${AUTH_TOKEN}`);

ws.on('open', () => {
    console.log('Connected to WebSocket server!');
    
    // Send a test message
    const testMessage = {
        type: 'chat',
        message: 'Hello, this is a test message!'
    };
    
    ws.send(JSON.stringify(testMessage));
});

ws.on('message', (data) => {
    console.log('Received response:', data.toString());
});

ws.on('error', (error) => {
    console.error('WebSocket error:', error);
});

ws.on('close', () => {
    console.log('Connection closed');
}); 