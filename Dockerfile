# Use a multi-stage build to reduce final image size
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04 as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only the files needed for installation
COPY pyproject.toml .

# Install dependencies
RUN pip3 install --no-cache-dir .

# Final stage
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy application code
COPY . .

# Create a non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port for API
EXPOSE ${port:-8000}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${port:-8000}/health || exit 1

# Use environment variables in the command
CMD ["python3", "-m", "uvicorn", "src.main:app", "--host", "${host:-0.0.0.0}", "--port", "${port:-8000}"]
