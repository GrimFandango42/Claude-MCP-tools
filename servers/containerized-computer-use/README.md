# Containerized Computer Use MCP Server

A Docker-based implementation of the Computer Use API that provides enhanced isolation, security, and portability for desktop automation tasks.

## Overview

This containerized version of the Windows Computer Use server runs in a Docker container with a full Linux desktop environment, accessible via VNC. It provides the same Computer Use API compatibility but with better isolation and cross-platform support.

## Architecture

```
┌─────────────────────────────────────────┐
│         Claude Desktop (Host)           │
├─────────────────────────────────────────┤
│            MCP Protocol                 │
│                  ↕                      │
│     Docker Container Boundary           │
├─────────────────────────────────────────┤
│      Container MCP Wrapper              │
│                  ↕                      │
│     Computer Use API Server             │
│                  ↕                      │
│    Linux Desktop Environment            │
│      (XVFB + Fluxbox + VNC)           │
└─────────────────────────────────────────┘
```

## Features

- **Full Computer Use API Compliance**: All three tools (computer_20250124, text_editor_20250429, bash_20250124)
- **VNC Access**: View and control the containerized desktop
- **Isolated Environment**: Complete separation from host system
- **Cross-Platform**: Works on Windows, macOS, and Linux hosts
- **Resource Limits**: Configurable CPU and memory constraints
- **Persistent Storage**: Shared volumes for data exchange

## Installation

### Prerequisites

1. **Docker Desktop**: Install from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. **VNC Viewer**: Any VNC client (TightVNC, RealVNC, UltraVNC)
3. **PowerShell**: For Windows management scripts

### Quick Setup

1. Run the setup script:
```powershell
.\setup.ps1
```

2. Start the container:
```powershell
.\start-container.ps1
```

3. Connect via VNC:
   - Host: `localhost:5900`
   - Password: `vnc123`

4. Add to Claude Desktop configuration:
```json
{
  "containerized-computer-use": {
    "command": "docker",
    "args": ["exec", "-i", "windows-computer-use", "python3", "/app/container_mcp_wrapper.py"],
    "keepAlive": true,
    "stderrToConsole": true
  }
}
```

## Usage

### Available Tools

1. **computer_20250124**
   - Actions: screenshot, key, type, mouse operations, scroll, wait
   - Full desktop automation capabilities

2. **text_editor_20250429**
   - Commands: view, create, str_replace
   - File editing within the container

3. **bash_20250124**
   - Execute Linux commands in the container
   - Full shell access to the containerized environment

### Example Workflows

```python
# Take a screenshot
computer_20250124(action="screenshot")

# Open a browser
computer_20250124(action="key", text="super")  # Open menu
computer_20250124(action="type", text="firefox")
computer_20250124(action="key", text="Return")

# Create a file
text_editor_20250429(command="create", path="/app/test.txt", file_text="Hello Container!")

# Run a command
bash_20250124(command="ls -la /app")
```

## Configuration

### Environment Variables

Edit `docker-compose.yml` to customize:

- `VNC_RESOLUTION`: Screen resolution (default: 1920x1080)
- `VNC_PW`: VNC password (default: vnc123)
- `VNC_COL_DEPTH`: Color depth (default: 24)

### Resource Limits

Adjust in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
```

### Volumes

- `./shared`: Share files between host and container
- `./workspaces`: Persistent workspace for projects

## Troubleshooting

### Container Won't Start

1. Check Docker is running:
```powershell
docker ps
```

2. View logs:
```powershell
docker logs windows-computer-use
```

3. Rebuild image:
```powershell
docker-compose build --no-cache
```

### VNC Connection Failed

1. Verify container is running:
```powershell
docker ps | findstr windows-computer-use
```

2. Check VNC service:
```powershell
docker exec windows-computer-use ps aux | findstr x11vnc
```

3. Test port availability:
```powershell
netstat -an | findstr 5900
```

### Performance Issues

1. Increase resource limits in docker-compose.yml
2. Reduce VNC resolution
3. Disable unnecessary services in container

## Development

### Extending the Server

1. Modify `computer_use_container.py` for API changes
2. Update `container_mcp_wrapper.py` for protocol changes
3. Rebuild with `docker-compose build`

### Adding Applications

Edit `Dockerfile` to install additional software:

```dockerfile
RUN apt-get update && apt-get install -y \
    your-application-here
```

### Custom Desktop Environment

Replace Fluxbox with alternatives in `startup.sh`:
- XFCE: `apt-get install xfce4`
- LXDE: `apt-get install lxde`
- Openbox: `apt-get install openbox`

## Security Considerations

- Container runs without privileged mode
- VNC password should be changed for production
- Network isolation via Docker networks
- No direct host filesystem access (only via volumes)
- Consider TLS/SSL for VNC in production

## Performance Optimization

1. **Use local image registry** for faster builds
2. **Enable BuildKit** for better caching:
   ```powershell
   $env:DOCKER_BUILDKIT=1
   ```
3. **Prune unused resources**:
   ```powershell
   docker system prune -a
   ```

## Comparison with Native Implementation

| Feature | Native Windows | Containerized |
|---------|---------------|---------------|
| Performance | Fastest | ~10% overhead |
| Isolation | Process-level | Full container |
| Portability | Windows only | Cross-platform |
| Resource Control | Limited | Full control |
| GUI Access | Direct | Via VNC |
| Setup Complexity | Simple | Moderate |

## Future Enhancements

- [ ] Web-based noVNC interface
- [ ] Multi-container orchestration
- [ ] GPU acceleration support
- [ ] Kubernetes deployment
- [ ] Automated testing framework
- [ ] Performance monitoring dashboard

## License

Same as parent project
