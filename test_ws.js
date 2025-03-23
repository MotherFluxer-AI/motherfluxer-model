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
            ws.removeListener('message', messageHandler);
            const response = data.toString();
            logger.info(`Received: ${response}`);
            resolve(response);
        };

        ws.on('message', messageHandler);
    });
}

// Main connection function
async function testConnection() {
    const uri = "wss://j03eo0e9yqwlsn-644118b1.proxy.runpod.net/ws?token=0d9faed892236a06ba75a6149e3c0658728450f591a3eddc6cb7b4018c3745cc";
    
    try {
        const ws = new WebSocket(uri, {
            headers: {
                'User-Agent': 'Mozilla/5.0',
                'Host': 'j03eo0e9yqwlsn-644118b1.proxy.runpod.net'
            }
        });

        ws.on('open', () => {
            logger.info("Connected to WebSocket server");
            
            // Start interactive message loop
            const askQuestion = () => {
                rl.question('\nEnter message (or "quit" to exit): ', async (message) => {
                    if (message.toLowerCase() === 'quit') {
                        ws.close();
                        rl.close();
                        return;
                    }

                    try {
                        await sendMessage(ws, message);
                        askQuestion(); // Ask for next message after receiving response
                    } catch (error) {
                        logger.error(`Error: ${error.message}`);
                        ws.close();
                        rl.close();
                    }
                });
            };

            askQuestion();
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