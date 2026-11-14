FROM python:3.14-slim

# Install useful development tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        curl \
        build-essential \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install ollama

WORKDIR /workspace

# Keep container running for VS Code
CMD ["sleep", "infinity"]