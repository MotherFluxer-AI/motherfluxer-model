import { WebSocket, Server as WebSocketServer } from 'ws';
import { Server, IncomingMessage } from 'http';
import ModelInstanceModel from '../models/model_instance.models';
import jwt from 'jsonwebtoken';
import { JwtPayload } from 'jsonwebtoken';
import { ConnectionDetails } from '../types/model-instance.types';

export class WebSocketProxyServer {
  private wss: WebSocketServer;

  constructor(server: Server) {
    // Initialize WebSocket server with explicit upgrade handling
    this.wss = new WebSocketServer({ 
      server,
      path: '/ws/model',
      perMessageDeflate: false,
      clientTracking: true
    });

    // Log when server is ready
    this.wss.on('listening', () => {
      console.log('WebSocket server is listening on /ws/model');
    });

    this.setupWebSocketServer();
  }

  private setupWebSocketServer() {
    this.wss.on('connection', async (ws: WebSocket, req: IncomingMessage) => {
      console.log('New WebSocket connection attempt');
      try {
        const url = new URL(req.url || '', 'ws://localhost');
        const token = url.searchParams.get('token');
        const modelId = url.searchParams.get('modelId');

        if (!token || !modelId) {
          console.log('Missing token or modelId');
          ws.close(1008, 'Missing token or modelId');
          return;
        }

        // Verify user token
        try {
          jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key') as JwtPayload;

          // Get model connection details
          ModelInstanceModel.getConnectionDetails(modelId)
            .then((connectionDetails: ConnectionDetails) => {
              if (!connectionDetails) {
                console.log('Model not found:', modelId);
                ws.close(1008, 'Model not found');
                return;
              }

              console.log('Got connection details for model:', modelId);

              // Connect to model with token in URL
              const modelWsUrl = new URL(connectionDetails.ws_url);
              modelWsUrl.searchParams.set('token', connectionDetails.token);
              const modelWs = new WebSocket(modelWsUrl.toString());
              let isAuthenticated = false;

              modelWs.on('open', () => {
                console.log('Connected to model WebSocket');
                // Send auth message to model
                const authMessage = {
                  type: 'system',
                  message: 'auth',
                  token: connectionDetails.token
                };
                console.log('Sending auth message to model:', authMessage);
                modelWs.send(JSON.stringify(authMessage));
              });

              modelWs.on('message', (data: Buffer) => {
                try {
                  const message = JSON.parse(data.toString());
                  console.log('Received message from model:', message);
                  
                  // Handle auth response
                  if (message.type === 'system' && message.status === 'authenticated') {
                    console.log('Model authentication successful');
                    isAuthenticated = true;
                    return;
                  }

                  // Only forward messages if authenticated
                  if (isAuthenticated) {
                    // Transform the model's response to match what the UI expects
                    const transformedResponse = {
                      type: 'response',
                      content: message.response,
                      code: message.code
                    };
                    console.log('Forwarding transformed response to user:', transformedResponse);
                    ws.send(JSON.stringify(transformedResponse));
                  }
                } catch (error) {
                  console.error('Error handling model message:', error);
                }
              });

              modelWs.on('error', (error: Error) => {
                console.error('Model WebSocket error:', error);
                ws.close(1011, 'Model connection error');
              });

              modelWs.on('close', () => {
                console.log('Model WebSocket connection closed');
                ws.close(1000, 'Model connection closed');
              });

              // Handle client messages
              ws.on('message', (data: Buffer) => {
                console.log('Received message from user:', data.toString());
                console.log('Auth state:', isAuthenticated);
                console.log('Model WebSocket state:', modelWs.readyState);
                
                if (isAuthenticated && modelWs.readyState === WebSocket.OPEN) {
                  try {
                    const message = JSON.parse(data.toString());
                    // Add default parameters if not present
                    const enhancedMessage = {
                      ...message,
                      parameters: {
                        ...message.parameters,
                        temperature: message.parameters?.temperature || 0.7,
                        max_length: message.parameters?.max_length || 100
                      }
                    };
                    console.log('Forwarding enhanced message to model:', enhancedMessage);
                    modelWs.send(JSON.stringify(enhancedMessage));
                    console.log('Message forwarded successfully');
                  } catch (error) {
                    console.error('Error forwarding user message:', error);
                  }
                } else {
                  console.log('Message not forwarded - Auth:', isAuthenticated, 'WebSocket state:', modelWs.readyState);
                }
              });

              ws.on('error', (error: Error) => {
                console.error('Client WebSocket error:', error);
                modelWs.close();
              });

              ws.on('close', () => {
                console.log('Client WebSocket connection closed');
                modelWs.close();
              });
            })
            .catch((error: Error) => {
              console.error('Error getting connection details:', error);
              ws.close(1011, 'Failed to get connection details');
            });
        } catch (error) {
          console.error('Token verification error:', error);
          ws.close(1008, 'Invalid token');
        }
      } catch (error) {
        console.error('Error in WebSocket connection:', error);
        ws.close(4002, 'Internal server error');
      }
    });
  }
}