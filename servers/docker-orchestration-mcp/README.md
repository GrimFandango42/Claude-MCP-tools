# Docker Orchestration MCP Server

A Model Context Protocol server that provides autonomous Docker container orchestration capabilities. This server enables Claude to deploy, manage, and monitor Docker containers and multi-container applications autonomously.

## 🎯 **Autonomous Capabilities**

This server transforms Claude into an autonomous deployment assistant that can:

### Container Management
- **Deploy Containers**: Create and start containers from images with custom configurations
- **Lifecycle Control**: Start, stop, restart, and remove containers
- **Resource Management**: Configure CPU, memory, and storage limits
- **Network Configuration**: Create and manage container networks
- **Volume Management**: Handle persistent storage and data volumes

### Multi-Container Applications
- **Application Stacks**: Deploy complete applications with multiple interconnected services
- **Service Discovery**: Configure container-to-container communication
- **Load Balancing**: Set up load balancing for scalable applications
- **Environment Management**: Handle environment variables and configuration

### Autonomous Features
- **Health Monitoring**: Continuous monitoring of deployed containers
- **Auto-Recovery**: Automatic restart of failed containers
- **Log Analysis**: Built-in log parsing and error detection
- **Configuration Validation**: Pre-deployment configuration checking
- **Rollback Capabilities**: Automatic rollback on deployment failures

## 🚀 **Integration with Autonomous Assistant**

This server serves as the **foundation** for the autonomous assistant, enabling:
- **Infrastructure as Code**: Deploy infrastructure through natural language commands
- **Integration with N8n**: Trigger deployments from N8n workflows
- **Credential Management**: Secure handling of registry credentials and secrets
- **Testing Integration**: Automated testing of deployed services
- **Monitoring Pipeline**: Health checks and performance monitoring

## 📋 **MCP Tools**

### Core Container Management
- `deploy_container(config)` - Deploy a single container with specified configuration
- `list_containers(filters)` - List containers with optional filtering
- `get_container_info(container_id)` - Get detailed container information
- `stop_container(container_id)` - Stop a running container
- `start_container(container_id)` - Start a stopped container
- `remove_container(container_id)` - Remove a container
- `get_container_logs(container_id)` - Retrieve container logs

### Network Management
- `create_network(config)` - Create a Docker network
- `list_networks()` - List available networks
- `connect_container_to_network(container_id, network_name)` - Connect container to network
- `disconnect_container_from_network(container_id, network_name)` - Disconnect from network

### Volume Management
- `create_volume(config)` - Create a persistent volume
- `list_volumes()` - List available volumes
- `mount_volume(container_id, volume_name, mount_point)` - Mount volume to container

### Multi-Container Applications
- `deploy_application_stack(stack_config)` - Deploy complete application with multiple services
- `scale_service(service_name, replicas)` - Scale a service to specified number of replicas
- `get_application_status(app_name)` - Get status of multi-container application

### Health & Monitoring
- `check_container_health(container_id)` - Perform health check on container
- `monitor_application(app_name)` - Start monitoring for application
- `get_system_resources()` - Get Docker system resource usage
- `cleanup_unused_resources()` - Clean up unused containers, networks, volumes

### Debugging & Diagnostics
- `validate_configuration(config)` - Validate deployment configuration before execution
- `diagnose_container_issues(container_id)` - Analyze and diagnose container problems
- `get_deployment_logs(deployment_id)` - Get comprehensive deployment logs
- `rollback_deployment(deployment_id)` - Roll back a failed deployment

## 🔧 **Installation**

1. Ensure Docker Desktop is installed and running
2. Create Python virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -e .
   ```

## 📁 **Configuration**

Add to Claude Desktop configuration (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "docker-orchestration": {
      "command": "python",
      "args": [
        "C:\\AI_Projects\\Claude-MCP-tools\\servers\\docker-orchestration-mcp\\src\\server.py"
      ],
      "cwd": "C:\\AI_Projects\\Claude-MCP-tools\\servers\\docker-orchestration-mcp",
      "env": {
        "DOCKER_HOST": "npipe:////./pipe/docker_engine",
        "PYTHONPATH": "C:\\AI_Projects\\Claude-MCP-tools\\servers\\docker-orchestration-mcp"
      },
      "keepAlive": true,
      "stderrToConsole": true,
      "description": "Autonomous Docker container orchestration and deployment management"
    }
  }
}
```

## 🧪 **Usage Examples**

### Simple Container Deployment
*"Deploy an nginx web server on port 8080"*
- Creates nginx container
- Configures port mapping
- Starts container and verifies health

### Multi-Container Application
*"Deploy a web application with database and cache"*
- Creates application network
- Deploys PostgreSQL database container
- Deploys Redis cache container
- Deploys web application container
- Configures inter-container communication
- Verifies all services are healthy

### Integration with N8n
*"Create an N8n workflow that deploys containers based on webhook triggers"*
- Sets up webhook endpoint
- Configures container deployment workflow
- Implements error handling and notifications

## 🔍 **Debugging Features**

### Built-in Diagnostics
- **Pre-deployment Validation**: Configuration syntax and dependency checking
- **Real-time Monitoring**: Container health and resource usage tracking
- **Log Analysis**: Automated parsing of container and deployment logs
- **Error Recovery**: Automatic retry and rollback mechanisms

### Integration with Claude Desktop Logs
- Logs to `C:\Users\Nithin\AppData\Roaming\Claude\logs\mcp-server-docker-orchestration.log`
- JSON-structured logging for easy parsing
- Error categorization and suggested solutions
- Performance metrics and timing information

## 🎯 **Success Metrics**

- **Deployment Speed**: Average container deployment time < 30 seconds
- **Success Rate**: 95%+ successful deployments on first attempt
- **Health Monitoring**: 99%+ uptime for monitored services
- **Error Recovery**: 90%+ automatic recovery from common failures

## 🔮 **Future Enhancements**

- **Multi-host Deployment**: Docker Swarm and Kubernetes integration
- **Advanced Monitoring**: Prometheus and Grafana integration
- **CI/CD Integration**: GitHub Actions and Jenkins webhook support
- **Cost Optimization**: Resource usage analysis and recommendations
- **Security Scanning**: Container vulnerability assessment

## 🤝 **Integration Points**

### With Existing MCP Servers
- **N8n Integration**: Deploy containers from N8n workflows
- **Knowledge Memory**: Store deployment configurations and history
- **Financial Data**: Cost tracking and optimization
- **Computer Use**: GUI-based Docker Desktop management when needed

### With Future Autonomous Servers
- **Credential Manager**: Secure handling of registry credentials
- **Health Monitor**: Advanced monitoring and alerting
- **Test Automation**: Automated testing of deployed services
- **Master Orchestrator**: Coordinated multi-service deployments

---
*Created: 2025-01-24*  
*Status: In Development*  
*Priority: Foundation Server for Autonomous Assistant*
