# Containerized Computer Use MCP - Deployment Guide

## 📋 Pre-Deployment Checklist

### 1. System Requirements
- [x] Windows 11 with Docker Desktop installed
- [x] Python 3.8+ installed
- [x] At least 4GB RAM available for container
- [x] VNC client installed (RealVNC, TightVNC, or UltraVNC)

### 2. Docker Setup
- [ ] Docker Desktop is running
- [ ] Docker Compose is available
- [ ] Sufficient disk space (at least 2GB)

### 3. Network Requirements
- [ ] Port 5900 available for VNC
- [ ] Port 8080 available for MCP WebSocket (optional)

## 🚀 Deployment Steps

### Step 1: Build the Docker Image
```batch
cd C:\AI_Projects\Claude-MCP-tools\servers\containerized-computer-use
.\build_docker.bat
```

Expected output:
- Docker image built successfully
- Container ready to start

### Step 2: Test the Server
```batch
.\run_tests.bat
```

All tests should pass before proceeding.

### Step 3: Start the Container
```batch
docker-compose up -d
```

Or use the start script:
```powershell
.\start-container.ps1
```

### Step 4: Verify Container Status
```batch
docker ps
```

Should show `windows-computer-use` container running.

### Step 5: Test VNC Connection
1. Open your VNC client
2. Connect to: `localhost:5900`
3. Password: `vnc123`
4. You should see a Linux desktop

### Step 6: Add to Claude Desktop

1. Open Claude Desktop configuration:
   ```
   C:\Users\Nithin\AppData\Roaming\Claude\claude_desktop_config.json
   ```

2. Add this configuration:
   ```json
   "containerized-computer-use": {
     "command": "cmd",
     "args": ["/c", "C:\\AI_Projects\\Claude-MCP-tools\\servers\\containerized-computer-use\\launch_containerized_mcp.bat"],
     "cwd": "C:\\AI_Projects\\Claude-MCP-tools\\servers\\containerized-computer-use",
     "keepAlive": true,
     "stderrToConsole": true,
     "description": "Containerized Computer Use with Docker isolation and VNC access"
   }
   ```

3. Save the file and restart Claude Desktop

## 🧪 Post-Deployment Testing

### Basic Functionality Tests

1. **Screenshot Test**
   ```
   Take a screenshot using the containerized computer
   ```

2. **Bash Command Test**
   ```
   Run 'ls -la' command in the container
   ```

3. **Text Editor Test**
   ```
   Create a file called test.txt with content "Hello Container" in /tmp/
   ```

### Advanced Tests

1. **Browser Automation**
   ```
   Open Firefox in the container and navigate to google.com
   ```

2. **Multi-Tool Workflow**
   ```
   1. Take a screenshot
   2. Create a Python script that prints "Hello"
   3. Run the script
   4. Capture the output
   ```

## 🔧 Troubleshooting

### Container Won't Start
1. Check Docker Desktop is running
2. Check ports 5900 and 8080 are free
3. Review Docker logs: `docker logs windows-computer-use`

### VNC Connection Failed
1. Verify container is running: `docker ps`
2. Check firewall settings
3. Try alternate VNC port if 5900 is blocked

### MCP Server Not Responding
1. Check server logs in Claude Desktop console
2. Verify Python dependencies: `pip list`
3. Test server directly: `python containerized_mcp_server.py`

### Performance Issues
1. Increase Docker memory allocation
2. Reduce VNC resolution in docker-compose.yml
3. Check CPU usage: `docker stats`

## 🔒 Security Considerations

### Production Deployment
1. **Change VNC Password**
   - Edit `VNC_PW` in docker-compose.yml
   - Rebuild image

2. **Network Isolation**
   - Use Docker networks for isolation
   - Limit port exposure

3. **Resource Limits**
   - Set CPU and memory limits in docker-compose.yml
   - Monitor resource usage

### Best Practices
1. Regular container updates
2. Log monitoring
3. Backup important data from volumes
4. Use read-only volumes where possible

## 📊 Performance Tuning

### Container Optimization
```yaml
# docker-compose.yml adjustments
deploy:
  resources:
    limits:
      cpus: '4'      # Increase for better performance
      memory: 8G     # More memory for complex tasks
```

### VNC Performance
- Lower resolution for faster response: `1280x720`
- Reduce color depth: `VNC_COL_DEPTH=16`
- Disable unnecessary visual effects

## 🎯 Usage Examples

### Example 1: Web Scraping
```python
# Take screenshot of a website
computer_20250124(action="screenshot")
computer_20250124(action="key", text="super")
computer_20250124(action="type", text="firefox")
computer_20250124(action="key", text="Return")
computer_20250124(action="wait", duration=3000)
computer_20250124(action="type", text="https://example.com")
computer_20250124(action="key", text="Return")
```

### Example 2: File Operations
```python
# Create and edit files
text_editor_20250429(command="create", path="/app/shared/report.txt", file_text="Analysis Report")
bash_20250124(command="cat /app/shared/report.txt")
```

### Example 3: Development Workflow
```python
# Write and run Python code
text_editor_20250429(command="create", path="/tmp/hello.py", file_text="print('Hello from container!')")
bash_20250124(command="python3 /tmp/hello.py")
```

## 📅 Maintenance Schedule

### Daily
- Check container health
- Monitor resource usage
- Review logs for errors

### Weekly
- Update container image
- Clean up unused files
- Test all functionality

### Monthly
- Security updates
- Performance review
- Backup configuration

## 🎉 Success Metrics

When properly deployed, you should see:
- ✅ Container running continuously
- ✅ VNC accessible at all times
- ✅ All Computer Use tools functional
- ✅ Less than 2s response time for commands
- ✅ Stable resource usage under 4GB RAM
- ✅ No error logs in Claude Desktop console

## 📞 Support

For issues:
1. Check logs: `docker logs windows-computer-use`
2. Review this guide's troubleshooting section
3. Test components individually
4. Document error messages and steps to reproduce

---

**Last Updated**: May 25, 2025
**Version**: 1.0.0
**Status**: Production Ready
