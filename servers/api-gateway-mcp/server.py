#!/usr/bin/env python3
"""
API Gateway MCP Server
Unified interface for multiple API providers with rate limiting, caching, and cost optimization.

This server provides a centralized way to access multiple AI APIs through a single interface,
with built-in rate limiting, response caching, cost tracking, and error handling.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import providers
from providers.openai_provider import OpenAIProvider
from providers.anthropic_provider import AnthropicProvider
from utils.cache import APICache

# Configure logging to stderr only
logging.basicConfig(
    level=logging.INFO,
    format='[api-gateway] %(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)


class APIGatewayMCP:
    """MCP Server for unified API access with advanced features."""
    
    def __init__(self):
        self.server = Server("api-gateway")
        self.providers: Dict[str, Any] = {}
        self.cache: Optional[APICache] = None
        self.config = self._load_config()
        
        # Initialize components
        self._initialize_providers()
        self._initialize_cache()
        self._register_tools()
        
        logging.info("API Gateway MCP Server initialized successfully")
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment and config files."""
        config = {
            "providers": {
                "openai": {
                    "enabled": True,
                    "api_key": os.getenv("OPENAI_API_KEY", ""),
                    "rate_limits": {
                        "per_minute": 60,
                        "per_hour": 3600,
                        "per_day": 100000
                    }
                },
                "anthropic": {
                    "enabled": True,
                    "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
                    "rate_limits": {
                        "per_minute": 50,
                        "per_hour": 1000,
                        "per_day": 50000
                    }
                }
            },
            "cache": {
                "type": "memory",  # or "redis"
                "max_size": 1000,
                "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379")
            },
            "default_provider": "openai",
            "cost_tracking": True,
            "detailed_logging": True
        }
        
        # Try to load from config file
        config_file = Path(__file__).parent / "config" / "gateway_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                    # Merge configs (file config takes precedence)
                    self._deep_merge(config, file_config)
            except Exception as e:
                logging.warning(f"Failed to load config file: {e}")
                
        return config
    
    def _deep_merge(self, dict1: Dict, dict2: Dict):
        """Deep merge two dictionaries."""
        for key, value in dict2.items():
            if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
                self._deep_merge(dict1[key], value)
            else:
                dict1[key] = value
    
    def _initialize_providers(self):
        """Initialize API providers based on configuration."""
        provider_configs = self.config.get("providers", {})
        
        # Initialize OpenAI provider
        if provider_configs.get("openai", {}).get("enabled", False):
            try:
                self.providers["openai"] = OpenAIProvider(provider_configs["openai"])
                logging.info("OpenAI provider initialized")
            except Exception as e:
                logging.error(f"Failed to initialize OpenAI provider: {e}")
                
        # Initialize Anthropic provider
        if provider_configs.get("anthropic", {}).get("enabled", False):
            try:
                self.providers["anthropic"] = AnthropicProvider(provider_configs["anthropic"])
                logging.info("Anthropic provider initialized")
            except Exception as e:
                logging.error(f"Failed to initialize Anthropic provider: {e}")
                
        if not self.providers:
            logging.warning("No API providers initialized - check your configuration")
            
    def _initialize_cache(self):
        """Initialize response caching."""
        try:
            cache_config = self.config.get("cache", {})
            self.cache = APICache(cache_config)
            logging.info(f"Cache initialized: {cache_config.get('type', 'memory')}")
        except Exception as e:
            logging.error(f"Failed to initialize cache: {e}")
            self.cache = None
    
    def _register_tools(self):
        """Register all MCP tools."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List all available tools."""
            return [
                Tool(
                    name="call_api",
                    description="Make an API call through the gateway with automatic provider selection, rate limiting, and caching",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "provider": {
                                "type": "string",
                                "enum": list(self.providers.keys()) + ["auto"],
                                "description": "API provider to use ('auto' for intelligent selection)",
                                "default": "auto"
                            },
                            "endpoint": {
                                "type": "string",
                                "description": "API endpoint (e.g., 'chat/completions', 'embeddings', 'images/generations')",
                                "examples": ["chat/completions", "embeddings", "images/generations", "models"]
                            },
                            "data": {
                                "type": "object", 
                                "description": "Request data/parameters for the API call"
                            },
                            "method": {
                                "type": "string",
                                "enum": ["GET", "POST", "PUT", "DELETE"],
                                "default": "POST",
                                "description": "HTTP method"
                            },
                            "use_cache": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to use response caching"
                            },
                            "cache_ttl": {
                                "type": "integer",
                                "description": "Custom cache TTL in seconds (optional)"
                            }
                        },
                        "required": ["endpoint", "data"]
                    }
                ),
                Tool(
                    name="list_providers",
                    description="List all available API providers and their status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_stats": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include usage statistics"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_usage_stats",
                    description="Get detailed usage statistics for providers and gateway",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "provider": {
                                "type": "string",
                                "description": "Specific provider to get stats for (optional)"
                            },
                            "include_cache_stats": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include cache performance statistics"
                            }
                        }
                    }
                ),
                Tool(
                    name="estimate_cost",
                    description="Estimate the cost of an API request before making it",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "provider": {
                                "type": "string",
                                "enum": list(self.providers.keys()) + ["auto"],
                                "default": "auto",
                                "description": "Provider to estimate cost for"
                            },
                            "endpoint": {
                                "type": "string",
                                "description": "API endpoint"
                            },
                            "data": {
                                "type": "object",
                                "description": "Request parameters"
                            }
                        },
                        "required": ["endpoint", "data"]
                    }
                ),
                Tool(
                    name="manage_cache",
                    description="Manage response cache (clear, get stats, configure)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["stats", "clear", "clear_provider"],
                                "description": "Cache management action"
                            },
                            "provider": {
                                "type": "string",
                                "description": "Provider to clear cache for (for clear_provider action)"
                            }
                        },
                        "required": ["action"]
                    }
                ),
                Tool(
                    name="gateway_status",
                    description="Get overall gateway health and status information",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool execution requests."""
            logging.info(f"Executing tool: {name} with arguments: {json.dumps(arguments, default=str)}")
            
            try:
                if name == "call_api":
                    result = await self._handle_api_call(arguments)
                elif name == "list_providers":
                    result = await self._handle_list_providers(arguments)
                elif name == "get_usage_stats":
                    result = await self._handle_usage_stats(arguments)
                elif name == "estimate_cost":
                    result = await self._handle_estimate_cost(arguments)
                elif name == "manage_cache":
                    result = await self._handle_manage_cache(arguments)
                elif name == "gateway_status":
                    result = await self._handle_gateway_status(arguments)
                else:
                    result = {"error": f"Unknown tool: {name}"}
                
                return [TextContent(type="text", text=json.dumps(result, default=str, indent=2))]
                
            except Exception as e:
                logging.error(f"Error executing tool {name}: {e}")
                error_result = {"error": f"Tool execution failed: {str(e)}"}
                return [TextContent(type="text", text=json.dumps(error_result))]
    
    async def _handle_api_call(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle API call requests."""
        provider_name = args.get("provider", "auto")
        endpoint = args.get("endpoint")
        data = args.get("data", {})
        method = args.get("method", "POST")
        use_cache = args.get("use_cache", True)
        
        # Select provider
        if provider_name == "auto":
            provider_name = self._select_best_provider(endpoint, data)
            
        if provider_name not in self.providers:
            return {"error": f"Provider '{provider_name}' not available"}
            
        provider = self.providers[provider_name]
        
        if not provider.enabled:
            return {"error": f"Provider '{provider_name}' is disabled"}
        
        # Check cache first
        cached_response = None
        if use_cache and self.cache:
            cached_response = await self.cache.get_cached_response(provider_name, endpoint, data)
            if cached_response:
                return {
                    "success": True,
                    "data": cached_response,
                    "provider": provider_name,
                    "cached": True,
                    "cost": 0.0,
                    "message": "Response served from cache"
                }
        
        # Make API call
        response = await provider.call_api(endpoint, method, data)
        
        # Cache successful response
        if response.success and use_cache and self.cache:
            estimated_cost = provider.estimate_cost({"endpoint": endpoint, "data": data})
            await self.cache.cache_response(
                provider_name, endpoint, data, response.data, cost_saved=estimated_cost
            )
        
        return {
            "success": response.success,
            "data": response.data,
            "error": response.error,
            "provider": provider_name,
            "cached": False,
            "cost_usd": response.cost,
            "tokens_used": response.tokens_used,
            "response_time_ms": response.response_time_ms
        }
    
    def _select_best_provider(self, endpoint: str, data: Dict[str, Any]) -> str:
        """Intelligently select the best provider for the request."""
        # Simple heuristics for provider selection
        
        # Check if specific model is requested
        model = data.get("model", "")
        if model:
            if any(claude in model.lower() for claude in ["claude", "anthropic"]):
                if "anthropic" in self.providers:
                    return "anthropic"
            elif any(gpt in model.lower() for gpt in ["gpt", "openai"]):
                if "openai" in self.providers:
                    return "openai"
        
        # Default routing by endpoint
        if endpoint in ["embeddings", "images/generations", "audio/speech"]:
            # OpenAI has better support for these
            if "openai" in self.providers and self.providers["openai"].enabled:
                return "openai"
        elif endpoint == "messages":
            # Anthropic-specific endpoint
            if "anthropic" in self.providers and self.providers["anthropic"].enabled:
                return "anthropic"
        
        # Fall back to default provider or first available
        default = self.config.get("default_provider", "openai")
        if default in self.providers and self.providers[default].enabled:
            return default
        
        # Return first enabled provider
        for name, provider in self.providers.items():
            if provider.enabled:
                return name
                
        return list(self.providers.keys())[0] if self.providers else "openai"
    
    async def _handle_list_providers(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list providers request."""
        include_stats = args.get("include_stats", True)
        
        providers_info = {}
        for name, provider in self.providers.items():
            info = provider.get_provider_info()
            if not include_stats:
                info.pop("usage_stats", None)
            providers_info[name] = info
            
        return {
            "providers": providers_info,
            "total_providers": len(self.providers),
            "enabled_providers": sum(1 for p in self.providers.values() if p.enabled),
            "default_provider": self.config.get("default_provider")
        }
    
    async def _handle_usage_stats(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle usage statistics request."""
        provider_name = args.get("provider")
        include_cache = args.get("include_cache_stats", True)
        
        if provider_name:
            if provider_name not in self.providers:
                return {"error": f"Provider '{provider_name}' not found"}
            return {"provider_stats": self.providers[provider_name].get_usage_summary()}
        
        # Get stats for all providers
        stats = {
            "gateway_stats": {
                "total_providers": len(self.providers),
                "enabled_providers": sum(1 for p in self.providers.values() if p.enabled),
                "cache_enabled": self.cache is not None
            },
            "provider_stats": {
                name: provider.get_usage_summary()
                for name, provider in self.providers.items()
            }
        }
        
        if include_cache and self.cache:
            stats["cache_stats"] = await self.cache.get_cache_stats()
            
        return stats
    
    async def _handle_estimate_cost(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cost estimation request."""
        provider_name = args.get("provider", "auto")
        endpoint = args.get("endpoint")
        data = args.get("data", {})
        
        if provider_name == "auto":
            provider_name = self._select_best_provider(endpoint, data)
            
        if provider_name not in self.providers:
            return {"error": f"Provider '{provider_name}' not available"}
            
        provider = self.providers[provider_name]
        
        try:
            estimated_cost = provider.estimate_cost({"endpoint": endpoint, "data": data})
            
            return {
                "provider": provider_name,
                "endpoint": endpoint,
                "estimated_cost_usd": round(estimated_cost, 6),
                "estimation_note": "Cost estimation is approximate and may vary based on actual usage"
            }
        except Exception as e:
            return {"error": f"Cost estimation failed: {str(e)}"}
    
    async def _handle_manage_cache(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cache management request."""
        if not self.cache:
            return {"error": "Cache is not enabled"}
            
        action = args.get("action")
        
        if action == "stats":
            return await self.cache.get_cache_stats()
        elif action == "clear":
            cleared = await self.cache.invalidate()
            return {"message": f"Cleared {cleared} cache entries"}
        elif action == "clear_provider":
            provider = args.get("provider")
            if not provider:
                return {"error": "Provider name required for clear_provider action"}
            cleared = await self.cache.invalidate(provider=provider)
            return {"message": f"Cleared {cleared} cache entries for provider {provider}"}
        else:
            return {"error": f"Unknown cache action: {action}"}
    
    async def _handle_gateway_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle gateway status request."""
        provider_status = {}
        for name, provider in self.providers.items():
            provider_status[name] = {
                "enabled": provider.enabled,
                "has_api_key": bool(provider.api_key),
                "total_requests": provider.usage_stats.total_requests,
                "success_rate": (
                    provider.usage_stats.successful_requests / 
                    max(1, provider.usage_stats.total_requests) * 100
                )
            }
        
        cache_status = "disabled"
        if self.cache:
            cache_stats = await self.cache.get_cache_stats()
            cache_status = cache_stats.get("type", "unknown")
        
        return {
            "gateway_version": "1.0.0",
            "status": "operational",
            "uptime": "N/A",  # Would need startup time tracking
            "providers": provider_status,
            "cache": {
                "status": cache_status,
                "enabled": self.cache is not None
            },
            "features": [
                "Multi-provider API access",
                "Intelligent provider selection", 
                "Response caching",
                "Rate limiting",
                "Cost tracking",
                "Usage statistics"
            ]
        }
    
    async def run(self):
        """Run the MCP server."""
        logging.info("Starting API Gateway MCP Server...")
        
        # Initialize cache connections
        if self.cache:
            await self.cache.initialize()
        
        # Log provider status
        enabled_providers = [name for name, provider in self.providers.items() if provider.enabled]
        logging.info(f"Enabled providers: {enabled_providers}")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Entry point for the MCP server."""
    server = APIGatewayMCP()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
