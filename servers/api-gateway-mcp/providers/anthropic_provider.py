"""
Anthropic API Provider for API Gateway MCP Server
Provides access to Anthropic Claude APIs with rate limiting and cost tracking.
"""

import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

import anthropic
from anthropic import AsyncAnthropic

from .base import BaseAPIProvider, APIResponse, AuthenticationError, APIError, RateLimitError


class AnthropicProvider(BaseAPIProvider):
    """Anthropic Claude API provider with comprehensive features."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("anthropic", config)
        
        # Initialize Anthropic client
        self.api_key = config.get('api_key') or config.get('ANTHROPIC_API_KEY', '')
        if not self.api_key:
            self.logger.error("Anthropic API key not provided")
            self.enabled = False
            return
            
        self.client = AsyncAnthropic(api_key=self.api_key)
        
        # Anthropic pricing (per 1M tokens) - updated as of Jan 2025
        self.pricing = {
            "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
            "claude-3-5-haiku-20241022": {"input": 0.25, "output": 1.25},
            "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
            "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
            "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25}
        }
        
        # Model aliases for easier access
        self.model_aliases = {
            "claude-3.5-sonnet": "claude-3-5-sonnet-20241022",
            "claude-sonnet": "claude-3-5-sonnet-20241022",
            "claude-3.5-haiku": "claude-3-5-haiku-20241022", 
            "claude-haiku": "claude-3-5-haiku-20241022",
            "claude-opus": "claude-3-opus-20240229",
            "claude-3-sonnet": "claude-3-sonnet-20240229",
            "claude-3-haiku": "claude-3-haiku-20240307"
        }
        
        self.logger.info("Anthropic provider initialized successfully")
    
    async def call_api(self, endpoint: str, method: str = "POST", 
                      data: Optional[Dict[str, Any]] = None,
                      headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Make an API call to Anthropic."""
        start_time = time.time()
        
        if not self.enabled:
            return APIResponse(
                success=False,
                error="Anthropic provider is disabled",
                provider=self.name
            )
        
        # Check rate limits
        if not await self.check_rate_limits():
            return APIResponse(
                success=False,
                error="Rate limit exceeded",
                provider=self.name
            )
        
        try:
            # Increment rate counters
            self.increment_rate_counters()
            
            # Route to appropriate Anthropic API
            response = await self._route_anthropic_request(endpoint, data or {})
            
            # Calculate response time
            response_time = int((time.time() - start_time) * 1000)
            
            # Update response with metadata
            response.provider = self.name
            response.response_time_ms = response_time
            
            # Update usage stats
            self.update_usage_stats(response)
            
            return response
            
        except anthropic.RateLimitError as e:
            error_response = APIResponse(
                success=False,
                error=f"Anthropic rate limit exceeded: {str(e)}",
                provider=self.name,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            self.update_usage_stats(error_response)
            return error_response
            
        except anthropic.AuthenticationError as e:
            error_response = APIResponse(
                success=False,
                error=f"Anthropic authentication failed: {str(e)}",
                provider=self.name,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            self.update_usage_stats(error_response)
            return error_response
            
        except Exception as e:
            self.logger.error(f"Anthropic API call failed: {e}")
            error_response = APIResponse(
                success=False,
                error=f"Anthropic API error: {str(e)}",
                provider=self.name,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            self.update_usage_stats(error_response)
            return error_response
    
    async def _route_anthropic_request(self, endpoint: str, data: Dict[str, Any]) -> APIResponse:
        """Route request to appropriate Anthropic API endpoint."""
        
        if endpoint == "messages" or endpoint == "chat/completions":
            return await self._handle_messages(data)
        elif endpoint == "models":
            return await self._handle_list_models()
        else:
            return APIResponse(
                success=False,
                error=f"Unsupported Anthropic endpoint: {endpoint}"
            )
    
    async def _handle_messages(self, data: Dict[str, Any]) -> APIResponse:
        """Handle message/chat completion requests."""
        try:
            # Handle both Anthropic and OpenAI-style message formats
            messages = data.get("messages", [])
            model = data.get("model", "claude-3-5-sonnet-20241022")
            max_tokens = data.get("max_tokens", 1024)
            temperature = data.get("temperature", 1.0)
            system = data.get("system", "")
            
            # Resolve model alias if used
            if model in self.model_aliases:
                model = self.model_aliases[model]
            
            # Convert OpenAI-style messages to Anthropic format if needed
            anthropic_messages = self._convert_messages_format(messages)
            
            # Extract system message if present in messages
            if not system and anthropic_messages and anthropic_messages[0].get("role") == "system":
                system = anthropic_messages[0]["content"]
                anthropic_messages = anthropic_messages[1:]
            
            # Make API call
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=anthropic_messages
            )
            
            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = self._calculate_cost(model, input_tokens, output_tokens)
            
            return APIResponse(
                success=True,
                data={
                    "id": response.id,
                    "model": response.model,
                    "role": response.role,
                    "content": [{"type": block.type, "text": block.text} for block in response.content],
                    "stop_reason": response.stop_reason,
                    "stop_sequence": response.stop_sequence,
                    "usage": {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens": input_tokens + output_tokens
                    }
                },
                cost=cost,
                tokens_used=input_tokens + output_tokens
            )
            
        except Exception as e:
            raise APIError(f"Messages request failed: {str(e)}", self.name)
    
    def _convert_messages_format(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert OpenAI-style messages to Anthropic format if needed."""
        converted = []
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            # Map OpenAI roles to Anthropic roles
            if role == "system":
                # System messages are handled separately in Anthropic
                converted.append({"role": "system", "content": content})
            elif role == "user":
                converted.append({"role": "user", "content": content})
            elif role == "assistant":
                converted.append({"role": "assistant", "content": content})
            elif role == "function" or role == "tool":
                # Convert function/tool calls to text format for now
                converted.append({
                    "role": "assistant", 
                    "content": f"[Function call: {content}]"
                })
        
        return converted
    
    async def _handle_list_models(self) -> APIResponse:
        """Handle list models requests."""
        try:
            # Anthropic doesn't have a list models endpoint, so return static list
            models = [
                {
                    "id": model_id,
                    "object": "model",
                    "created": 1234567890,  # Placeholder timestamp
                    "owned_by": "anthropic"
                }
                for model_id in self.pricing.keys()
            ]
            
            return APIResponse(
                success=True,
                data={"models": models}
            )
            
        except Exception as e:
            raise APIError(f"List models failed: {str(e)}", self.name)
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for Claude models."""
        if model not in self.pricing:
            # Try to find closest match for older model versions
            base_model = None
            if "sonnet" in model.lower():
                if "3-5" in model or "3.5" in model:
                    base_model = "claude-3-5-sonnet-20241022"
                else:
                    base_model = "claude-3-sonnet-20240229"
            elif "haiku" in model.lower():
                if "3-5" in model or "3.5" in model:
                    base_model = "claude-3-5-haiku-20241022"
                else:
                    base_model = "claude-3-haiku-20240307"
            elif "opus" in model.lower():
                base_model = "claude-3-opus-20240229"
            
            if base_model and base_model in self.pricing:
                model = base_model
            else:
                return 0.0
        
        pricing = self.pricing[model]
        # Pricing is per 1M tokens
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
    
    def estimate_cost(self, request_data: Dict[str, Any]) -> float:
        """Estimate the cost of a request."""
        endpoint = request_data.get("endpoint", "")
        data = request_data.get("data", {})
        
        if endpoint in ["messages", "chat/completions"]:
            messages = data.get("messages", [])
            model = data.get("model", "claude-3-5-sonnet-20241022")
            max_tokens = data.get("max_tokens", 1024)
            
            # Resolve model alias
            if model in self.model_aliases:
                model = self.model_aliases[model]
            
            # Estimate input tokens (rough: 1 token ≈ 0.75 words)
            total_text = " ".join([msg.get("content", "") for msg in messages])
            estimated_input_tokens = len(total_text.split()) * 1.33
            
            return self._calculate_cost(model, int(estimated_input_tokens), max_tokens)
        
        return 0.0
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "api_base": "https://api.anthropic.com",
            "supported_endpoints": [
                "messages",
                "chat/completions",  # OpenAI compatibility
                "models"
            ],
            "available_models": list(self.pricing.keys()),
            "model_aliases": self.model_aliases,
            "pricing_info": self.pricing,
            "has_api_key": bool(self.api_key),
            "usage_stats": self.get_usage_summary(),
            "features": [
                "System messages",
                "Function calling (via text)",
                "Long context windows",
                "Constitutional AI safety"
            ]
        }
