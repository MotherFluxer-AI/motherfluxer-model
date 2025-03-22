const { io } = require('socket.io-client');

const WEBSOCKET_URL = 'http://213.173.99.23:8000';
const AUTH_TOKEN = '0d9faed892236a06ba75a6149e3c0658728450f591a3eddc6cb7b4018c3745cc';

const socket = io(WEBSOCKET_URL, {
    query: {
        token: AUTH_TOKEN
    }
});

socket.on('connect', () => {
    console.log('Connected to WebSocket server!');
    
    // Send a test message
    const testMessage = {
        type: 'chat',
        message: 'Hello, this is a test message!'
    };
    
    socket.emit('message', testMessage);
});

socket.on('message', (data) => {
    console.log('Received response:', data);
});

socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
}); 