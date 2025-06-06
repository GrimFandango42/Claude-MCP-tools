# 🚀 Remote MCP Gateway Deployment Guide

## **Quick Deploy Options**

### **Option 1: Railway (Recommended - Easiest)**

1. **Push to GitHub**:
   ```bash
   git add servers/remote-mcp-gateway/
   git commit -m "Add remote MCP gateway"
   git push
   ```

2. **Deploy to Railway**:
   - Go to [railway.app](https://railway.app)
   - Connect your GitHub repo
   - Select the `servers/remote-mcp-gateway` directory
   - Railway will auto-detect Dockerfile and deploy
   - Get your URL: `https://your-app.railway.app`

3. **Test your deployment**:
   ```bash
   curl https://your-app.railway.app/health
   ```

### **Option 2: Render**

1. **Connect Repository**:
   - Go to [render.com](https://render.com)
   - Connect GitHub repo
   - Choose "Web Service"
   - Root directory: `servers/remote-mcp-gateway`

2. **Auto-deploys** from the `render.yaml` config

### **Option 3: Fly.io**

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Deploy**:
   ```bash
   cd servers/remote-mcp-gateway
   fly launch --dockerfile
   fly deploy
   ```

### **Option 4: Local Testing**

1. **Install dependencies**:
   ```bash
   cd servers/remote-mcp-gateway
   pip install -r requirements.txt
   ```

2. **Run locally**:
   ```bash
   python app.py
   # Visit: http://localhost:8000
   ```

## **Using Your Remote MCP Gateway**

### **From Claude Mobile App**

Once deployed, you can access your MCP skills from Claude mobile by making HTTP requests to your deployed gateway.

**Example: Travel booking from your phone**
```
"Search for accommodations in Tokyo from July 15-18 for 2 guests, include Airbnb options"

# Your phone Claude app would make this request:
POST https://your-gateway.railway.app/api/v1/travel/search
{
  "destination": "Tokyo",
  "check_in": "2025-07-15", 
  "check_out": "2025-07-18",
  "guests": 2,
  "include_airbnb": true
}
```

### **API Endpoints Available**

- `GET /` - Documentation homepage
- `GET /api/v1/servers` - List all MCP servers  
- `GET /api/v1/tools` - List all available tools
- `POST /api/v1/execute` - Execute any MCP tool
- `POST /api/v1/travel/search` - Travel booking search
- `POST /api/v1/travel/recommendations` - AI travel recommendations
- `WebSocket /ws` - Real-time communication
- `GET /health` - Health check

### **Interactive Documentation**

Visit your deployed URL + `/docs` for full Swagger documentation:
- `https://your-app.railway.app/docs`

## **Security Considerations**

### **Authentication** (Optional)
Add API key authentication:

```python
# In app.py, uncomment and implement:
def verify_auth_token(token: str) -> bool:
    return token == os.getenv("API_KEY", "your-secret-key")
```

### **Environment Variables**
Set these in your hosting platform:

```bash
API_KEY=your-secret-api-key
ALLOWED_ORIGINS=https://claude.ai,https://your-domain.com
```

### **Rate Limiting**
Add rate limiting for production:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/execute")
@limiter.limit("10/minute")
async def execute_tool(request: Request, ...):
    # Your existing code
```

## **Scaling Considerations**

### **Database Integration**
For persistent data, add database support:

```python
# PostgreSQL example
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)
```

### **Background Tasks**
For long-running operations:

```python
from fastapi import BackgroundTasks

@app.post("/api/v1/execute-async")
async def execute_tool_async(request: MCPToolRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(execute_tool_in_background, request)
    return {"task_id": "123", "status": "started"}
```

### **Caching**
Add Redis for caching:

```python
import aioredis

redis = aioredis.from_url("redis://localhost")

async def cached_execute_tool(request: MCPToolRequest):
    cache_key = f"tool:{request.tool_name}:{hash(str(request.parameters))}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    result = await executor.execute_tool(request)
    await redis.setex(cache_key, 300, result.json())  # 5 min cache
    return result
```

## **Monitoring & Observability**

### **Logging**
Add structured logging:

```python
import structlog

logger = structlog.get_logger()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        "request_processed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time
    )
    
    return response
```

### **Health Checks**
Enhanced health check:

```python
@app.get("/health")
async def health_check():
    # Test database connection
    # Test external API dependencies
    # Check memory usage
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "checks": {
            "database": "ok",
            "memory_usage": "75%",
            "active_connections": 42
        }
    }
```

## **Cost Optimization**

### **Resource Usage**
- **Railway**: $5/month starter (1GB RAM, 1 vCPU)
- **Render**: Free tier available (0.5GB RAM)
- **Fly.io**: Free tier (256MB RAM)

### **Auto-scaling**
Configure based on traffic:

```yaml
# render.yaml
scaling:
  minInstances: 1
  maxInstances: 3
  targetCPUPercent: 70
```

## **Production Checklist**

- [ ] Environment variables configured
- [ ] Authentication implemented  
- [ ] Rate limiting enabled
- [ ] HTTPS/SSL configured
- [ ] Health checks working
- [ ] Monitoring/logging setup
- [ ] Backup strategy for data
- [ ] Error handling robust
- [ ] Performance testing done
- [ ] Security review completed

Your MCP skills are now ready for global access! 🌍