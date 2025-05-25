#!/bin/bash
# Startup script for Containerized Computer Use

echo "Starting Containerized Computer Use environment..."

# Start X virtual framebuffer
echo "Starting Xvfb..."
Xvfb :1 -screen 0 ${VNC_RESOLUTION}x${VNC_COL_DEPTH} &
sleep 2

# Start window manager
echo "Starting Fluxbox..."
fluxbox &
sleep 2

# Start VNC server
echo "Starting VNC server..."
x11vnc -display :1 -forever -usepw -shared -rfbport 5900 &

# Start the Computer Use API server
echo "Starting Computer Use API server..."
cd /app
python3 /app/server.py &

# Keep container running
echo "Container ready - VNC available on port 5900"
tail -f /dev/null
