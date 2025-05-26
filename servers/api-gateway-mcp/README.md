# API Gateway MCP Server

A production-ready MCP server that provides unified access to multiple AI API providers with intelligent routing, response caching, rate limiting, and comprehensive cost tracking.

## 🌟 Features

- **Multi-Provider Support**: OpenAI, Anthropic Claude (extensible architecture)
- **Intelligent Routing**: Automatic provider selection based on request type and model
- **Response Caching**: Configurable TTL caching with memory and Redis backends
- **Rate Limiting**: Per-provider and global rate limiting with intelligent backoff
- **Cost Tracking**: Real-time cost estimation and usage analytics
- **Error Handling**: Robust error handling with fallback mechanisms
- **Production Ready**: Comprehensive logging, monitoring, and operational tools

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│            Claude Desktop               │
├─────────────────────────────────────────┤
│              MCP Protocol               │
│                   ↕                     │
│            API Gateway Server           │
├─────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────────────┐ │
│  │   Cache     │ │    Rate Limiter     │ │
│  │  (Memory/   │ │   (Per Provider)    │ │
│  │   Redis)    │ │                     │ │
│  └─────────────┘ └─────────────────────┘ │
├─────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────────────┐ │
│  │   OpenAI    │ │     Anthropic       │ │
│  │  Provider   │ │     Provider        │ │
│  └─────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **API Keys** for desired providers:
   - OpenAI: Set `OPENAI_API_KEY` environment variable
   - Anthropic: Set `ANTHROPIC_API_KEY` environment variable
3. **Optional**: Redis for production caching

### Installation

1. The server will auto-install dependencies on first run
2. Set your API keys as environment variables:
```bash
set OPENAI_API_KEY=your_openai_key_here
set ANTHROPIC_API_KEY=your_anthropic_key_here
```

### Add to Claude Desktop

Add this configuration to your `claude_desktop_config.json`:

```json
{
  "api-gateway": {
    "command": "cmd",
    "args": ["/c", "C:\\AI_Projects\\Claude-MCP-tools\\servers\\api-gateway-mcp\\launch_api_gateway.bat"],
    "cwd": "C:\\AI_Projects\\Claude-MCP-tools\\servers\\api-gateway-mcp",
    "env": {
      "OPENAI_API_KEY": "your_openai_key_here",
      "ANTHROPIC_API_KEY": "your_anthropic_key_here"
    },
    "keepAlive": true,
    "stderrToConsole": true,
    "description": "Unified API Gateway with intelligent routing, caching, and cost optimization"
  }
}
```

## 🛠️ Available Tools

### `call_api`
Make API calls through the gateway with automatic optimization.

**Parameters:**
- `provider`: Provider to use ("openai", "anthropic", or "auto")
- `endpoint`: API endpoint (e.g., "chat/completions", "embeddings")
- `data`: Request parameters
- `use_cache`: Enable response caching (default: true)
- `cache_ttl`: Custom cache TTL in seconds

**Example:**
```json
{
  "provider": "auto",
  "endpoint": "chat/completions",
  "data": {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }
}
```

### `list_providers`
Get information about all available providers and their status.

### `get_usage_stats`
Retrieve detailed usage statistics including costs, request counts, and performance metrics.

### `estimate_cost`
Estimate the cost of an API request before making it.

### `manage_cache`
Manage the response cache (get stats, clear cache, etc.).

### `gateway_status`
Get overall gateway health and operational status.

## 📊 Intelligent Features

### Automatic Provider Selection
When using `provider: "auto"`, the gateway intelligently selects the best provider based on:
- Requested model (Claude → Anthropic, GPT → OpenAI)
- Endpoint type (embeddings → OpenAI, messages → Anthropic)
- Provider availability and rate limits
- Cost optimization preferences

### Response Caching
Responses are automatically cached based on:
- **Embeddings**: 24 hours (content rarely changes)
- **Chat completions**: 5 minutes (conversational context)
- **Image generation**: 2 hours (same prompt results)
- **Model lists**: 6 hours (infrequent updates)

### Rate Limiting
Per-provider rate limiting with:
- Requests per minute/hour/day tracking
- Automatic backoff on limit approaching
- Intelligent request queuing
- Cross-provider failover

## 💰 Cost Tracking

The gateway provides comprehensive cost tracking:
- Real-time cost calculation per request
- Usage statistics by provider and endpoint
- Cost savings from caching
- Historical usage trends
- Budget monitoring and alerts

## ⚙️ Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `REDIS_URL`: Redis connection URL (optional)

### Configuration File
Edit `config/gateway_config.json` to customize:
- Provider settings and rate limits
- Cache configuration
- Default models and routing preferences
- Security and access controls

## 🔧 Advanced Usage

### Custom Provider Selection
```json
{
  "provider": "anthropic",
  "endpoint": "messages",
  "data": {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 1000,
    "messages": [{"role": "user", "content": "Analyze this..."}]
  }
}
```

### Cost-Optimized Requests
```json
{
  "provider": "auto",
  "endpoint": "chat/completions", 
  "data": {
    "model": "gpt-4o-mini",
    "messages": [...],
    "temperature": 0.1,
    "cache_ttl": 3600
  },
  "use_cache": true
}
```

### Batch Operations
The gateway can handle multiple requests efficiently with automatic batching and caching.

## 📈 Monitoring & Analytics

### Usage Statistics
- Total requests by provider
- Success/failure rates
- Average response times
- Cost breakdowns
- Cache hit rates

### Performance Metrics
- Request latency by endpoint
- Provider reliability scores
- Rate limit utilization
- Cache performance

### Cost Analytics
- Cost per request by model
- Daily/monthly spending trends
- Cost savings from caching
- Provider cost comparison

## 🔒 Security Features

- API key secure storage
- Request validation and sanitization
- Rate limiting to prevent abuse
- Optional Redis authentication
- Audit logging for compliance

## 🚨 Error Handling

The gateway provides robust error handling:
- Automatic retry with exponential backoff
- Provider failover on errors
- Detailed error reporting
- Graceful degradation

## 🧪 Testing

Run the test suite:
```bash
python test_api_gateway.py
```

Test specific functionality:
```bash
# Test OpenAI integration
python -c "import asyncio; from server import APIGatewayMCP; asyncio.run(APIGatewayMCP()._test_openai())"

# Test cache performance  
python -c "import asyncio; from utils.cache import MemoryCache; cache = MemoryCache(); asyncio.run(cache.get_stats())"
```

## 📝 Troubleshooting

### Common Issues

**"Provider not available"**
- Check API keys are set correctly
- Verify provider is enabled in config
- Check network connectivity

**"Rate limit exceeded"**
- Increase rate limits in config
- Enable request queuing
- Use caching to reduce API calls

**"Cache not working"**
- Check Redis connection (if using Redis)
- Verify TTL settings
- Monitor cache statistics

### Debug Mode
Enable detailed logging by setting `PYTHONUNBUFFERED=1` and checking stderr output.

## 🔄 Updates & Maintenance

### Adding New Providers
1. Create provider class inheriting from `BaseAPIProvider`
2. Implement required methods (`call_api`, `estimate_cost`, etc.)
3. Add provider to configuration
4. Update intelligent routing logic

### Cache Optimization
- Monitor cache hit rates with `manage_cache`
- Adjust TTL values based on usage patterns
- Consider Redis for high-volume production use

### Performance Tuning
- Adjust rate limits based on API provider quotas
- Optimize cache size for memory usage
- Enable request batching for high throughput

## 📊 Production Deployment

### Recommended Settings
- Use Redis for caching in production
- Set appropriate rate limits for your usage
- Enable detailed logging and monitoring
- Implement backup API keys for redundancy

### Scaling Considerations
- Multiple gateway instances can share Redis cache
- Provider-specific rate limiting scales automatically
- Consider request queuing for high-volume scenarios

## 🤝 Contributing

This server follows the established MCP framework patterns:
- Proper `mcp.server.Server` usage
- Async/await patterns throughout
- Comprehensive error handling
- Structured logging to stderr

## 📄 License

Same as parent project

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: May 25, 2025

For issues or feature requests, check the server logs and verify your configuration settings.
