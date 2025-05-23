#!/bin/bash

# Start X Virtual Framebuffer
Xvfb :1 -screen 0 ${VNC_RESOLUTION}x${VNC_COL_DEPTH} &
sleep 2

# Start fluxbox window manager
fluxbox &
sleep 2

# Start VNC server
x11vnc -display :1 -usepw -forever -shared -rfbport ${VNC_PORT} -bg -o /var/log/x11vnc.log

# Configure pyautogui to work in container
export DISPLAY=:1

# Start the MCP server using supervisor
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
