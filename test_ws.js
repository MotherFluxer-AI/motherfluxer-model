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

        const messageHandler = (data) => {
            const response = JSON.parse(data.toString());
            // Only resolve for non-system messages
            if (response.type !== 'system') {
                ws.removeListener('message', messageHandler);
                logger.info(`Received: ${data.toString()}`);
                resolve(response);
            } else {
                logger.debug(`System message: ${data.toString()}`);
            }
        };

        ws.on('message', messageHandler);
    });
}

// Function to authenticate with the server
async function authenticate(ws, token) {
    return new Promise((resolve, reject) => {
        const authMessage = {
            type: "system",
            message: "auth",
            token: token
        };

        ws.send(JSON.stringify(authMessage));
        logger.info("Sent authentication message");

        const authHandler = (data) => {
            const response = JSON.parse(data.toString());
            if (response.type === 'system') {
                ws.removeListener('message', authHandler);
                if (response.status === 'authenticated') {
                    logger.info("Authentication successful");
                    resolve(true);
                } else {
                    logger.error("Authentication failed");
                    reject(new Error("Authentication failed"));
                }
            }
        };

        ws.on('message', authHandler);
    });
}

// Main connection function
async function testConnection() {
    const token = "0d9faed892236a06ba75a6149e3c0658728450f591a3eddc6cb7b4018c3745cc";
    const uri = `wss://j03eo0e9yqwlsn-644118b1.proxy.runpod.net/ws?token=${token}`;
    
    try {
        const ws = new WebSocket(uri);

        ws.on('open', async () => {
            logger.info("Connected to WebSocket server");
            
            try {
                // Authenticate first
                await authenticate(ws, token);
                
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
                            logger.error(`Error sending message: ${error.message}`);
                            ws.close(1000, "Error in message handling");
                            rl.close();
                        }
                    });
                };

                askQuestion();
            } catch (error) {
                logger.error(`Authentication error: ${error.message}`);
                ws.close(1008, "Authentication failed");
                rl.close();
            }
        });

        ws.on('close', (code, reason) => {
            logger.info(`Connection closed: ${code} - ${reason}`);
            rl.close();
        });

        ws.on('error', (error) => {
            logger.error(`WebSocket error: ${error.message}`);
        });

    } catch (error) {
        logger.error(`Connection error: ${error.message}`);
        rl.close();
    }
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