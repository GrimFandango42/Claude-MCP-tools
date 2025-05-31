#!/usr/bin/env python3
"""
AgenticSeek MCP Server - FastMCP Implementation
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
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

# Configure logging to stderr only
logger = logging.getLogger("agenticseek-mcp")
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler(sys.stderr)
logHandler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
logger.addHandler(logHandler)
logger.propagate = False

try:
    from mcp.server.fastmcp import FastMCP
    logger.info("Imported FastMCP successfully")
except ImportError:
    logger.error("Failed to import FastMCP. Please install with: pip install mcp")
    sys.exit(1)

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

# Initialize FastMCP server
mcp = FastMCP("agenticseek-mcp")
logger.info("Using FastMCP for AgenticSeek MCP implementation")

async def call_agenticseek(prompt: str, provider_key: str, context: str = "") -> str:
    """Call AgenticSeek with the specified provider configuration"""
    try:
        # Switch AgenticSeek to the desired provider
        await switch_provider(provider_key)
        
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
                metadata += f"Privacy: {'Local Processing' if provider_info.is_local else 'Cloud Processing'}\\n"
                
                return answer + metadata
            else:
                return f"AgenticSeek error: {result.get('reasoning', 'Unknown error')}"
                
    except Exception as e:
        logger.error(f"Error calling AgenticSeek: {str(e)}")
        return f"Error calling AgenticSeek: {str(e)}"

async def switch_provider(provider_key: str):
    """Switch AgenticSeek to use the specified provider"""
    provider = PROVIDERS[provider_key]
    
    # Read current config
    config = configparser.ConfigParser()
    if os.path.exists(AGENTICSEEK_CONFIG_PATH):
        config.read(AGENTICSEEK_CONFIG_PATH)
    else:
        logger.warning(f"Config file not found: {AGENTICSEEK_CONFIG_PATH}")
        return
    
    # Update provider settings if MAIN section exists
    if 'MAIN' not in config:
        config['MAIN'] = {}
    
    config['MAIN']['provider_name'] = provider.name
    config['MAIN']['provider_model'] = provider.model
    config['MAIN']['is_local'] = str(provider.is_local)
    
    # Write updated config
    try:
        with open(AGENTICSEEK_CONFIG_PATH, 'w') as configfile:
            config.write(configfile)
        
        # Give AgenticSeek a moment to reload config
        await asyncio.sleep(0.5)
        logger.info(f"Switched AgenticSeek to provider: {provider.name} ({provider.model})")
    except Exception as e:
        logger.warning(f"Could not update config file: {e}")

def select_optimal_provider(prompt: str, priority: str) -> str:
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

@mcp.tool()
def local_reasoning(prompt: str, context: str = "") -> str:
    """
    Use local DeepSeek AI for private, cost-free reasoning
    
    Args:
        prompt: The prompt to process
        context: Additional context
    """
    return asyncio.run(call_agenticseek(prompt, "local", context))

@mcp.tool()
def openai_reasoning(prompt: str, model: str = "gpt-3.5-turbo", context: str = "") -> str:
    """
    Use OpenAI for fast, high-quality reasoning (costs money)
    
    Args:
        prompt: The prompt to process
        model: Model to use (gpt-3.5-turbo or gpt-4)
        context: Additional context
    """
    provider = "openai-fast" if model == "gpt-3.5-turbo" else "openai-quality"
    return asyncio.run(call_agenticseek(prompt, provider, context))

@mcp.tool()
def google_reasoning(prompt: str, context: str = "") -> str:
    """
    Use Google Gemini for fast, cost-effective reasoning
    
    Args:
        prompt: The prompt to process
        context: Additional context
    """
    return asyncio.run(call_agenticseek(prompt, "google", context))

@mcp.tool()
def smart_routing(prompt: str, priority: str = "balanced", context: str = "") -> str:
    """
    Automatically select the best provider based on task characteristics
    
    Args:
        prompt: The prompt to process
        priority: Optimization priority (cost, speed, quality, privacy, balanced)
        context: Additional context
    """
    provider = select_optimal_provider(prompt, priority)
    result = asyncio.run(call_agenticseek(prompt, provider, context))
    routing_info = f"[Routed to: {PROVIDERS[provider].name} ({PROVIDERS[provider].model}) - Priority: {priority}]\\n\\n"
    return routing_info + result

@mcp.tool()
def get_provider_status() -> str:
    """
    Check which AI providers are available and their characteristics
    """
    async def check_status():
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
    
    result = asyncio.run(check_status())
    return json.dumps(result, indent=2)

@mcp.tool()
def estimate_cost(prompt: str, provider: str = "all") -> str:
    """
    Estimate the cost of running a prompt on different providers
    
    Args:
        prompt: The prompt to estimate cost for
        provider: Specific provider to estimate (default: all)
    """
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
    
    return json.dumps(estimates, indent=2)

# Main entry point
if __name__ == "__main__":
    try:
        # Log startup information
        logger.info("AgenticSeek MCP Server starting up")
        logger.info(f"AgenticSeek URL: {AGENTICSEEK_URL}")
        logger.info(f"Config path: {AGENTICSEEK_CONFIG_PATH}")
        
        # Check AgenticSeek availability
        try:
            import httpx
            response = httpx.get(f"{AGENTICSEEK_URL}/health", timeout=5.0)
            if response.status_code == 200:
                logger.info("AgenticSeek API is available")
            else:
                logger.warning(f"AgenticSeek API returned status {response.status_code}")
        except Exception as e:
            logger.warning(f"Could not connect to AgenticSeek: {e}")
        
        # Run the MCP server
        mcp.run()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)
