# motherfluxer-model
Open source model container for MotherFluxer

## Quick Start

### Prerequisites
- Python 3.10+
- CUDA-compatible GPU (16GB+ VRAM recommended)
- Git
- Pod running with port 8000 open. Confirm port 8000 is listed on the "Expose HTTP Ports" section of "Edit Pod"

### RunPod Setup
1. Create a RunPod account at https://www.runpod.io/
2. Deploy a new pod with:
   - GPU: RTX 2000 Ada or better (16GB+ VRAM)
   - Template: PyTorch Latest
   - Container Disk: 50GB

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/MotherFluxer-AI/motherfluxer-model.git
cd motherfluxer-model
```

2. **Install Dependencies**
```bash
# Install the package in development mode
pip install -e .

# Install development dependencies (if you're developing/testing)
pip install -r requirements-dev.txt
```

3. **Configure Environment**
```bash
# Generate an auth token
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Create .env file with your generated token
echo "MODEL_NAME=microsoft/phi-2
MODEL_REVISION=main
MODEL_VERSION=1.0.0
REBUILD_MODEL=false
MAX_SEQUENCE_LENGTH=2048
DEFAULT_TEMPERATURE=0.7
INSTANCE_ID= your RunPod instance ID (if using RunPod)
AUTH_TOKEN= input the auth token you just created
CENTRAL_ROUTER_URL=wss://router.motherfluxer.ai
HUGGINGFACE_TOKEN=your_huggingface_token" > .env
```

4. **Run Tests**
```bash
pytest
```

5. **Start the Server**
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### API Endpoints

- Health Check: `GET http://localhost:8000/health`
- WebSocket: `ws://localhost:8000/ws`

## Development

### Project Structure
```
motherfluxer-model/
├── src/
│   ├── api/         # API endpoints
│   ├── model/       # Model management
│   └── utils/       # Utilities
├── tests/           # Test files
├── requirements.txt # Production dependencies
└── setup.py        # Package configuration
```

### Common Issues

1. **Module Not Found Errors**
   - Make sure you've installed the package in development mode (`pip install -e .`)
   - Verify all `__init__.py` files are present in the directories

2. **CUDA/GPU Issues**
   - Verify GPU is properly recognized: `nvidia-smi`
   - Check CUDA version compatibility with PyTorch

3. **Environment Issues**
   - Ensure `.env` file is properly configured
   - Check that all required environment variables are set

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
[Your License Here]
