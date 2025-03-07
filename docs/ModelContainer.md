# MotherFluxer Model Container Specification

## 1. Hosting Options

### 1.1 Recommended Provider: RunPod
[Previous RunPod section remains the same, but with updated specs]

#### Deployment Options
| Type | Specs | Cost | Best For |
|------|-------|------|-----------|
| Reserved Instance (Recommended) | RTX 4080/4090, 16-24GB VRAM, 32GB RAM, 8vCPUs | ~$120-150/month | Production deployments |
| Spot Instance | Same specs | $0.25-0.35/hour | Development/Testing |

### 1.2 Minimum Requirements
```yaml
Hardware:
  CPU: 8+ cores (recommended)
  RAM: 32GB minimum
  GPU: 16GB VRAM minimum (RTX 4080 or better recommended)
  Storage: 50GB minimum

Network:
  [remains the same]
```

## 2. Container Configuration

### 2.1 Docker Configuration
```dockerfile
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04  # Updated CUDA version

# System dependencies remain the same

# Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Model-specific environment variables
ENV MODEL_NAME="microsoft/phi-3"
ENV MODEL_REVISION="latest"
ENV MAX_SEQUENCE_LENGTH=2048  # Phi-3 supports longer sequences
ENV DEFAULT_TEMPERATURE=0.7

[rest remains the same]
```

### 2.2 Required Environment Variables
```bash
MODEL_PATH=/app/models/phi-3  # Updated model path
MAX_MEMORY=24000            # Increased memory limit in MB
INSTANCE_ID=unique-id
AUTH_TOKEN=secret
CENTRAL_ROUTER_URL=wss://router.motherfluxer.ai
```

## 3. API Specification

### 3.1 WebSocket Connection
```yaml
Connection:
  url: wss://{instance-address}/ws
  headers:
    Authorization: Bearer {auth-token}
    Instance-ID: {instance-id}

Messages:
  # Health Updates (Every 30s based on HealthChecker.tsx)
  health_update:
    type: "health"
    data:
      health: number        # 0-100 score
      timestamp: string
      metrics:
        latency: number
        errorRate: number
        successRate: number

  # Inference Request
  inference_request:
    type: "inference"
    data:
      message: string
      context?: string[]
      parameters:
        temperature: number
        max_tokens: number

  # Inference Response
  inference_response:
    type: "inference_response"
    data:
      text: string
      usage:
        prompt_tokens: number
        completion_tokens: number
```

### 3.2 REST Endpoints

#### Health Check
```yaml
GET /health
response:
  status: 200
  body:
    health: number         # Matches ModelInstance.healthScore
    is_active: boolean     # Matches ModelInstance.isActive
    version: string       # Matches ModelInstance.version
    container_version: string
```

### 3.3 Required Headers
```yaml
Authorization: Bearer {token}
Instance-ID: {unique-instance-id}
Content-Type: application/json
```

### 3.4 Instance Registration
```yaml
POST /register
request:
  body:
    instance_name: string
    host_address: string
    version: string
    container_version: string
    admin_id?: string

response:
  body:
    id: string            # Assigned instance ID
    auth_token: string    # Instance authentication token
```