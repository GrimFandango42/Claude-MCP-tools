# Universal Remote MCP Gateway 🌍

**One-click deployment** for mobile access to ALL your Claude Desktop MCP servers!

## 🎯 What This Does

This gateway exposes **ALL 22 of your MCP servers** as HTTP endpoints for mobile access:

- **filesystem**, **firecrawl**, **playwright**, **financial-datasets**
- **fantasy-pl**, **mcp-pandoc**, **screenpilot**, **sqlite**  
- **windows-computer-use**, **containerized-computer-use**
- **n8n-workflow-generator**, **docker-orchestration**
- **github**, **memory**, **api-gateway**, **claude-code-integration**
- **vibetest**, **agenticseek-mcp**, **code-formatter**
- **security-scanner**, **visual-debugging**, **enhanced-memory**
- **auto-accept**, **travel-booking**

## 🚀 Quick Deploy

### **Option 1: Railway (Recommended)**
1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Select: `GrimFandango42/Claude-MCP-tools`
4. **Root Directory**: `servers/universal-remote-gateway`
5. Deploy!

### **Option 2: Render**
1. Go to [render.com](https://render.com)
2. New Web Service → Connect GitHub
3. Repository: `GrimFandango42/Claude-MCP-tools`
4. **Root Directory**: `servers/universal-remote-gateway`
5. Deploy

## 📱 Mobile Usage Examples

Once deployed at `https://your-app.railway.app`:

### **Execute Any MCP Tool**
```bash
curl -X POST https://your-app.railway.app/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "server_name": "travel-booking",
    "tool_name": "search_accommodations", 
    "parameters": {"destination": "Paris", "check_in": "2025-08-01", "check_out": "2025-08-03"}
  }'
```

## 🔗 API Endpoints

- `GET /` - Interactive dashboard
- `GET /health` - Health check
- `GET /docs` - Swagger documentation
- `GET /api/v1/servers` - List all 22 MCP servers
- `POST /api/v1/execute` - Execute any tool on any server

## 🧪 Test Your Deployment

```bash
# Health check
curl https://your-app.railway.app/health

# List all servers
curl https://your-app.railway.app/api/v1/servers
```

## 🎉 What You Get

Once deployed, your **Claude mobile app** can access:

✅ **All 22 MCP servers** via HTTP  
✅ **150+ individual tools** across all servers  
✅ **Interactive documentation** at `/docs`  
✅ **Global access** from anywhere  

Your entire Claude Desktop MCP ecosystem is now mobile-ready! 🌍