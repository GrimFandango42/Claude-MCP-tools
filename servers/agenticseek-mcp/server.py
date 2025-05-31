#!/usr/bin/env python3
"""
AgenticSeek MCP Server - Phase 1A
Multi-Provider AI Routing with Cost Optimization

Provides intelligent routing between:
- Local AI (DeepSeek R1 14B) - Cost: Free, Privacy: High, Speed: Good
- OpenAI (GPT-3.5/GPT-4) - Cost: Low/High, Privacy: Low, Speed: Fast 
- Google (Gemini) - Cost: Low, Privacy: Low, Speed: Fast
"""

import asyncio
import json
import configparser
import httpx
import os
import sys
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configuration for AgenticSeek
AGENTICSEEK_URL = "http://localhost:8000"
AGENTICSEEK_CONFIG_PATH = "C:\\AI_Projects\\agenticSeek\\config.ini"

@dataclass
class ProviderConfig:
    name: str
    model: str
    is_local: bool
    cost_per_1k_tokens: float
    speed_score: int  # 1-10, higher = faster
    privacy_score: int  # 1-10, higher = more private

# Provider configurations
PROVIDERS = {
    "local": ProviderConfig(
        name="ollama",
        model="deepseek-r1:14b",
        is_local=True,
        cost_per_1k_tokens=0.0,
        speed_score=7,
        privacy_score=10
    ),
    "openai-fast": ProviderConfig(
        name="openai",
        model="gpt-3.5-turbo",
        is_local=False,
        cost_per_1k_tokens=0.002,
        speed_score=9,
        privacy_score=3
    ),
    "openai-quality": ProviderConfig(
        name="openai",
        model="gpt-4",
        is_local=False,
        cost_per_1k_tokens=0.03,
        speed_score=6,
        privacy_score=3
    ),
    "google": ProviderConfig(
        name="google",
        model="gemini-1.5-flash",
        is_local=False,
        cost_per_1k_tokens=0.001,
        speed_score=8,
        privacy_score=3
    )
}

class AgenticSeekMCPServer:
    def __init__(self):
        self.server = Server("agenticseek-mcp")
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            return [
                types.Tool(
                    name="local_reasoning",
                    description="Use local DeepSeek AI for private, cost-free reasoning",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "The prompt to process"},
                            "context": {"type": "string", "description": "Additional context", "default": ""}
                        },
                        "required": ["prompt"]
                    }
                ),
                types.Tool(
                    name="openai_reasoning",
                    description="Use OpenAI for fast, high-quality reasoning (costs money)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "The prompt to process"},
                            "model": {"type": "string", "description": "Model to use", "enum": ["gpt-3.5-turbo", "gpt-4"], "default": "gpt-3.5-turbo"},
                            "context": {"type": "string", "description": "Additional context", "default": ""}
                        },
                        "required": ["prompt"]
                    }
                ),
                types.Tool(
                    name="google_reasoning",
                    description="Use Google Gemini for fast, cost-effective reasoning",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "The prompt to process"},
                            "context": {"type": "string", "description": "Additional context", "default": ""}
                        },
                        "required": ["prompt"]
                    }
                ),
                types.Tool(
                    name="smart_routing",
                    description="Automatically select the best provider based on task characteristics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "The prompt to process"},
                            "priority": {"type": "string", "description": "Optimization priority", 
                                       "enum": ["cost", "speed", "quality", "privacy", "balanced"], "default": "balanced"},
                            "context": {"type": "string", "description": "Additional context", "default": ""}
                        },
                        "required": ["prompt"]
                    }
                ),
                types.Tool(
                    name="get_provider_status",
                    description="Check which AI providers are available and their characteristics",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="estimate_cost",
                    description="Estimate the cost of running a prompt on different providers",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "The prompt to estimate cost for"},
                            "provider": {"type": "string", "description": "Specific provider to estimate", "default": "all"}
                        },
                        "required": ["prompt"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            try:
                if name == "local_reasoning":
                    result = await self.call_agenticseek(arguments["prompt"], "local", arguments.get("context", ""))
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "openai_reasoning":
                    model = arguments.get("model", "gpt-3.5-turbo")
                    provider = "openai-fast" if model == "gpt-3.5-turbo" else "openai-quality"
                    result = await self.call_agenticseek(arguments["prompt"], provider, arguments.get("context", ""))
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "google_reasoning":
                    result = await self.call_agenticseek(arguments["prompt"], "google", arguments.get("context", ""))
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "smart_routing":
                    provider = self.select_optimal_provider(arguments["prompt"], arguments.get("priority", "balanced"))
                    result = await self.call_agenticseek(arguments["prompt"], provider, arguments.get("context", ""))
                    routing_info = f"[Routed to: {PROVIDERS[provider].name} ({PROVIDERS[provider].model}) - Priority: {arguments.get('priority', 'balanced')}]\\n\\n"
                    return [types.TextContent(type="text", text=routing_info + result)]
                
                elif name == "get_provider_status":
                    status = await self.get_provider_status()
                    return [types.TextContent(type="text", text=json.dumps(status, indent=2))]
                
                elif name == "estimate_cost":
                    estimates = self.estimate_costs(arguments["prompt"], arguments.get("provider", "all"))
                    return [types.TextContent(type="text", text=json.dumps(estimates, indent=2))]
                
                else:
                    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
                    
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def call_agenticseek(self, prompt: str, provider_key: str, context: str = "") -> str:
        """Call AgenticSeek with the specified provider configuration"""
        try:
            # Switch AgenticSeek to the desired provider
            await self.switch_provider(provider_key)
            
            # Make the API call
            full_prompt = f"{context}\\n\\n{prompt}" if context else prompt
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{AGENTICSEEK_URL}/query",
                    json={"query": full_prompt, "tts_enabled": False}
                )
                response.raise_for_status()
                
                result = response.json()
                if result.get("success") == "true":
                    answer = result.get("answer", "No response")
                    reasoning = result.get("reasoning", "")
                    provider_info = PROVIDERS[provider_key]
                    
                    # Add provider metadata
                    metadata = f"\\n\\n---\\nProvider: {provider_info.name} ({provider_info.model})\\n"
                    if not provider_info.is_local:
                        metadata += f"Est. Cost: ~${provider_info.cost_per_1k_tokens * len(prompt) / 1000:.4f}\\n"
                    metadata += f"Privacy: {'🔒 Local' if provider_info.is_local else '☁️ Cloud'}\\n"
                    
                    return answer + metadata
                else:
                    return f"AgenticSeek error: {result.get('reasoning', 'Unknown error')}"
                    
        except Exception as e:
            return f"Error calling AgenticSeek: {str(e)}"

    async def switch_provider(self, provider_key: str):
        """Switch AgenticSeek to use the specified provider"""
        provider = PROVIDERS[provider_key]
        
        # Read current config
        config = configparser.ConfigParser()
        config.read(AGENTICSEEK_CONFIG_PATH)
        
        # Update provider settings
        config['MAIN']['provider_name'] = provider.name
        config['MAIN']['provider_model'] = provider.model
        config['MAIN']['is_local'] = str(provider.is_local)
        
        # Write updated config
        with open(AGENTICSEEK_CONFIG_PATH, 'w') as configfile:
            config.write(configfile)
        
        # Give AgenticSeek a moment to reload config
        await asyncio.sleep(0.5)

    def select_optimal_provider(self, prompt: str, priority: str) -> str:
        """Select the best provider based on task characteristics and priority"""
        prompt_lower = prompt.lower()
        
        # Simple heuristics for provider selection
        if priority == "cost":
            return "local"
        elif priority == "privacy":
            return "local"
        elif priority == "speed":
            return "openai-fast"
        elif priority == "quality":
            return "openai-quality"
        else:  # balanced
            # Smart routing based on task type
            if any(word in prompt_lower for word in ["private", "confidential", "internal", "sensitive"]):
                return "local"
            elif any(word in prompt_lower for word in ["quick", "fast", "brief", "simple"]):
                return "openai-fast"
            elif any(word in prompt_lower for word in ["analyze", "complex", "detailed", "comprehensive"]):
                return "openai-quality"
            else:
                return "google"  # Good balance of cost/speed

    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all available providers"""
        status = {}
        
        for key, provider in PROVIDERS.items():
            status[key] = {
                "name": provider.name,
                "model": provider.model,
                "type": "local" if provider.is_local else "cloud",
                "cost_per_1k_tokens": provider.cost_per_1k_tokens,
                "speed_score": provider.speed_score,
                "privacy_score": provider.privacy_score
            }
        
        # Check AgenticSeek availability
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{AGENTICSEEK_URL}/health")
                agenticseek_status = "online" if response.status_code == 200 else "offline"
        except:
            agenticseek_status = "offline"
        
        return {
            "agenticseek_status": agenticseek_status,
            "providers": status
        }

    def estimate_costs(self, prompt: str, provider: str) -> Dict[str, Any]:
        """Estimate costs for running prompt on different providers"""
        prompt_length = len(prompt)
        token_estimate = prompt_length / 4  # Rough estimation
        
        estimates = {}
        
        if provider == "all":
            for key, config in PROVIDERS.items():
                if not config.is_local:
                    estimates[key] = {
                        "provider": config.name,
                        "model": config.model,
                        "estimated_cost": config.cost_per_1k_tokens * token_estimate / 1000,
                        "estimated_tokens": int(token_estimate)
                    }
                else:
                    estimates[key] = {
                        "provider": config.name,
                        "model": config.model,
                        "estimated_cost": 0.0,
                        "estimated_tokens": int(token_estimate),
                        "note": "Local processing - no API costs"
                    }
        else:
            if provider in PROVIDERS:
                config = PROVIDERS[provider]
                estimates[provider] = {
                    "provider": config.name,
                    "model": config.model,
                    "estimated_cost": config.cost_per_1k_tokens * token_estimate / 1000 if not config.is_local else 0.0,
                    "estimated_tokens": int(token_estimate)
                }
        
        return estimates

async def main():
    server_instance = AgenticSeekMCPServer()
    
    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="agenticseek-mcp",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=types.ServerCapabilities.NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
