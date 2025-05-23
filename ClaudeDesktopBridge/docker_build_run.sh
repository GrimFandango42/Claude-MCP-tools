#!/bin/bash

# Bash script to build and run the Claude Desktop Bridge Docker container

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please create it from .env.example"
    echo "Copy .env.example to .env and fill in your API keys"
    exit 1
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t claude-desktop-bridge .

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "Error: Docker build failed"
    exit 1
fi

# Run the Docker container
echo "Running Docker container..."
docker run -d --name claude-desktop-bridge \
    -p 8000:8000 \
    -v "$(pwd)/screenshots:/app/screenshots" \
    -v "$(pwd)/.env:/app/.env" \
    --restart unless-stopped \
    claude-desktop-bridge

# Check if container started successfully
if [ $? -ne 0 ]; then
    echo "Error: Failed to start Docker container"
    exit 1
fi

# Show container status
echo "Container started successfully!"
echo "API is available at: http://localhost:8000"
echo "Streamlit UI can be started with: python -m streamlit run app/ui/streamlit_app.py"

# Show logs
echo "Showing container logs (Ctrl+C to exit)..."
docker logs -f claude-desktop-bridge
