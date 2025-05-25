#!/bin/bash
cd /mnt/c/AI_Projects/Claude-MCP-tools/servers/containerized-computer-use
echo "Starting Docker build process..."
docker-compose build --no-cache > build.log 2>&1 &
BUILD_PID=$!
echo "Docker build started with PID: $BUILD_PID"
echo "Build log will be saved to build.log"
echo "You can check progress with: tail -f build.log"
