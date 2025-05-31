# AgenticSeek MCP Server - Phase 1A

Multi-Provider AI Routing with Cost Optimization

## Features

- **Local AI Routing**: Use DeepSeek R1 14B locally (free, private)
- **OpenAI Integration**: GPT-3.5-turbo (fast) and GPT-4 (quality)
- **Google Integration**: Gemini-1.5-flash (cost-effective)
- **Smart Routing**: Automatically select optimal provider
- **Cost Estimation**: Calculate API costs before execution
- **Privacy Control**: Keep sensitive data local when needed

## Setup

1. Install dependencies:
```bash
setup.bat
```

2. Make sure AgenticSeek is running:
```bash
# In WSL2
cd ~/agenticSeek
source agentic_seek_env/bin/activate
python3 api.py
```

3. Add to claude_desktop_config.json:
```json
"agenticseek-mcp": {
  "command": "C:\\AI_Projects\\Claude-MCP-tools\\servers\\agenticseek-mcp\\.venv\\Scripts\\python.exe",
  "args": ["C:\\AI_Projects\\Claude-MCP-tools\\servers\\agenticseek-mcp\\server.py"],
  "cwd": "C:\\AI_Projects\\Claude-MCP-tools\\servers\\agenticseek-mcp",
  "keepAlive": true,
  "stderrToConsole": true,
  "description": "AgenticSeek multi-provider AI routing with cost optimization"
}
```

## Available Tools

- `local_reasoning` - Private, cost-free local AI
- `openai_reasoning` - Fast OpenAI processing  
- `google_reasoning` - Cost-effective Google Gemini
- `smart_routing` - Automatic provider selection
- `get_provider_status` - Check provider availability
- `estimate_cost` - Cost estimation for different providers

## Usage Examples

```python
# Cost-optimized processing
smart_routing("Analyze this data", priority="cost")

# Privacy-focused processing  
local_reasoning("Process this confidential information")

# Speed-optimized processing
openai_reasoning("Quick summary needed", model="gpt-3.5-turbo")

# Quality-focused processing
openai_reasoning("Complex analysis required", model="gpt-4")
```

## Smart Routing Logic

- **Cost Priority**: Routes to local DeepSeek
- **Privacy Priority**: Routes to local DeepSeek  
- **Speed Priority**: Routes to OpenAI GPT-3.5
- **Quality Priority**: Routes to OpenAI GPT-4
- **Balanced**: Smart selection based on content analysis

## Provider Characteristics

| Provider | Cost/1K tokens | Speed | Privacy | Best For |
|----------|----------------|-------|---------|----------|
| Local DeepSeek | $0.00 | Good | High | Cost-sensitive, private |
| OpenAI GPT-3.5 | $0.002 | Fast | Low | Quick responses |
| OpenAI GPT-4 | $0.03 | Medium | Low | Complex analysis |
| Google Gemini | $0.001 | Fast | Low | Balanced cost/performance |
