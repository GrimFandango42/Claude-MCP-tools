FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:1
ENV VNC_PORT=5900
ENV VNC_COL_DEPTH=24
ENV VNC_RESOLUTION=1920x1080
ENV VNC_PW=vnc123
ENV PYTHONUNBUFFERED=1

# Install base dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-tk \
    xvfb \
    x11vnc \
    fluxbox \
    wget \
    curl \
    git \
    vim \
    nano \
    xterm \
    firefox \
    chromium-browser \
    libgtk-3-0 \
    libglib2.0-0 \
    libdbus-1-3 \
    libx11-6 \
    libxext6 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libgbm1 \
    libasound2 \
    fonts-liberation \
    xfonts-base \
    xfonts-75dpi \
    xfonts-100dpi \
    supervisor \
    dbus-x11 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for Computer Use
RUN pip3 install --no-cache-dir \
    pyautogui \
    pillow>=10.2.0 \
    python-xlib \
    pynput \
    opencv-python \
    numpy \
    requests>=2.32.0 \
    websocket-client \
    fastmcp

# Create working directory
WORKDIR /app

# Copy the Computer Use server
COPY computer_use_container.py /app/server.py
COPY container_mcp_wrapper.py /app/container_mcp_wrapper.py
COPY requirements.txt /app/requirements.txt

# Install additional requirements if any
RUN pip3 install -r requirements.txt || true

# Create VNC password
RUN mkdir -p ~/.vnc && x11vnc -storepasswd ${VNC_PW} ~/.vnc/passwd

# Copy startup scripts
COPY startup.sh /app/startup.sh
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN chmod +x /app/startup.sh

# Expose ports
EXPOSE 5900 8080

# Set up entrypoint
ENTRYPOINT ["/app/startup.sh"]
