const WebSocket = require('ws');
const readline = require('readline');

// Configure logging
const logger = {
    info: (msg) => console.log(`INFO: ${msg}`),
    error: (msg) => console.error(`ERROR: ${msg}`),
    debug: (msg) => console.log(`DEBUG: ${msg}`)
};

// Create readline interface for user input
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Function to send message and wait for response
async function sendMessage(ws, message) {
    return new Promise((resolve, reject) => {
        const chatMessage = {
            type: "chat",
            message: message,
            parameters: {
                temperature: 0.7,
                max_length: 100
            }
        };

        ws.send(JSON.stringify(chatMessage));
        logger.info("Message sent, waiting for response...");

        // Set up one-time message handler with timeout
        const messageHandler = (data) => {
            clearTimeout(timeout);
            ws.removeListener('message', messageHandler);
            const response = data.toString();
            logger.info(`Received: ${response}`);
            resolve(response);
        };

        // Add timeout to prevent hanging
        const timeout = setTimeout(() => {
            ws.removeListener('message', messageHandler);
            reject(new Error('Response timeout'));
        }, 30000);

        ws.on('message', messageHandler);
    });
}

// Function to create WebSocket connection
function createWebSocket() {
    const uri = "wss://j03eo0e9yqwlsn-644118b1.proxy.runpod.net/ws?token=0d9faed892236a06ba75a6149e3c0658728450f591a3eddc6cb7b4018c3745cc";
    
    const ws = new WebSocket(uri, {
        followRedirects: true,
        handshakeTimeout: 10000,
        headers: {
            'User-Agent': 'Mozilla/5.0',
            'Upgrade': 'websocket',
            'Connection': 'Upgrade',
            'Sec-WebSocket-Version': '13',
            'Host': 'j03eo0e9yqwlsn-644118b1.proxy.runpod.net'
        },
        perMessageDeflate: false
    });

    return ws;
}

// Main connection function
async function testConnection() {
    let ws = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 3;
    
    const connect = () => {
        if (reconnectAttempts >= maxReconnectAttempts) {
            logger.error("Max reconnection attempts reached");
            process.exit(1);
        }

        ws = createWebSocket();

        ws.on('open', () => {
            logger.info("Connected to WebSocket server");
            reconnectAttempts = 0; // Reset counter on successful connection
            
            // Start interactive message loop
            const askQuestion = () => {
                rl.question('\nEnter message (or "quit" to exit): ', async (message) => {
                    if (message.toLowerCase() === 'quit') {
                        ws.close(1000, "User requested disconnect");
                        rl.close();
                        return;
                    }

                    try {
                        await sendMessage(ws, message);
                        askQuestion(); // Ask for next message after receiving response
                    } catch (error) {
                        logger.error(`Error: ${error.message}`);
                        if (ws.readyState === WebSocket.OPEN) {
                            ws.close(1000, "Error in message handling");
                        }
                        reconnectAttempts++;
                        setTimeout(connect, 2000);
                    }
                });
            };

            askQuestion();
        });

        ws.on('close', (code, reason) => {
            logger.info(`Connection closed: ${code} - ${reason}`);
            if (code !== 1000) { // If not clean close
                reconnectAttempts++;
                setTimeout(connect, 2000);
            } else {
                rl.close();
            }
        });

        ws.on('error', (error) => {
            logger.error(`WebSocket error: ${error.message}`);
            if (ws.readyState === WebSocket.OPEN) {
                ws.close(1000, "Error occurred");
            }
        });
    };

    // Start initial connection
    connect();
}

// Handle program termination
process.on('SIGINT', () => {
    logger.info("Program terminated by user");
    process.exit(0);
});

// Start the connection
testConnection().catch(error => {
    logger.error(`Fatal error: ${error.message}`);
    process.exit(1);
}); 