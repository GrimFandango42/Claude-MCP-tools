"""
OpenAI API Provider for API Gateway MCP Server
Provides access to OpenAI APIs with rate limiting and cost tracking.
"""

import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

import openai
from openai import AsyncOpenAI

from .base import BaseAPIProvider, APIResponse, AuthenticationError, APIError, RateLimitError


class OpenAIProvider(BaseAPIProvider):
    """OpenAI API provider with comprehensive features."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("openai", config)
        
        # Initialize OpenAI client
        self.api_key = config.get('api_key') or config.get('OPENAI_API_KEY', '')
        if not self.api_key:
            self.logger.error("OpenAI API key not provided")
            self.enabled = False
            return
            
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # OpenAI pricing (per 1K tokens) - updated as of Jan 2025
        self.pricing = {
            "gpt-4o": {"input": 0.0050, "output": 0.0150},
            "gpt-4o-mini": {"input": 0.000150, "output": 0.000600},
            "gpt-4-turbo": {"input": 0.0100, "output": 0.0300},
            "gpt-4": {"input": 0.0300, "output": 0.0600},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "text-embedding-3-large": {"input": 0.00013, "output": 0.0},
            "text-embedding-3-small": {"input": 0.00002, "output": 0.0},
            "text-embedding-ada-002": {"input": 0.00010, "output": 0.0},
            "whisper-1": {"input": 0.006, "output": 0.0},  # per minute
            "tts-1": {"input": 0.0150, "output": 0.0},  # per 1K characters
            "tts-1-hd": {"input": 0.0300, "output": 0.0},  # per 1K characters
            "dall-e-3": {"standard": 0.040, "hd": 0.080},  # per image
            "dall-e-2": {"standard": 0.020}  # per image
        }
        
        self.logger.info("OpenAI provider initialized successfully")
    
    async def call_api(self, endpoint: str, method: str = "POST", 
                      data: Optional[Dict[str, Any]] = None,
                      headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Make an API call to OpenAI."""
        start_time = time.time()
        
        if not self.enabled:
            return APIResponse(
                success=False,
                error="OpenAI provider is disabled",
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
            
            # Route to appropriate OpenAI API
            response = await self._route_openai_request(endpoint, data or {})
            
            # Calculate response time
            response_time = int((time.time() - start_time) * 1000)
            
            # Update response with metadata
            response.provider = self.name
            response.response_time_ms = response_time
            
            # Update usage stats
            self.update_usage_stats(response)
            
            return response
            
        except openai.RateLimitError as e:
            error_response = APIResponse(
                success=False,
                error=f"OpenAI rate limit exceeded: {str(e)}",
                provider=self.name,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            self.update_usage_stats(error_response)
            return error_response
            
        except openai.AuthenticationError as e:
            error_response = APIResponse(
                success=False,
                error=f"OpenAI authentication failed: {str(e)}",
                provider=self.name,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            self.update_usage_stats(error_response)
            return error_response
            
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            error_response = APIResponse(
                success=False,
                error=f"OpenAI API error: {str(e)}",
                provider=self.name,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            self.update_usage_stats(error_response)
            return error_response
    
    async def _route_openai_request(self, endpoint: str, data: Dict[str, Any]) -> APIResponse:
        """Route request to appropriate OpenAI API endpoint."""
        
        if endpoint == "chat/completions" or endpoint == "completions":
            return await self._handle_chat_completion(data)
        elif endpoint == "embeddings":
            return await self._handle_embeddings(data)
        elif endpoint == "images/generations":
            return await self._handle_image_generation(data)
        elif endpoint == "audio/speech":
            return await self._handle_text_to_speech(data)
        elif endpoint == "audio/transcriptions":
            return await self._handle_speech_to_text(data)
        elif endpoint == "models":
            return await self._handle_list_models()
        else:
            return APIResponse(
                success=False,
                error=f"Unsupported OpenAI endpoint: {endpoint}"
            )
    
    async def _handle_chat_completion(self, data: Dict[str, Any]) -> APIResponse:
        """Handle chat completion requests."""
        try:
            # Extract parameters
            messages = data.get("messages", [])
            model = data.get("model", "gpt-3.5-turbo")
            temperature = data.get("temperature", 1.0)
            max_tokens = data.get("max_tokens")
            stream = data.get("stream", False)
            
            # Make API call
            response = await self.client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            # Calculate cost
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0
            cost = self._calculate_text_cost(model, input_tokens, output_tokens)
            
            return APIResponse(
                success=True,
                data={
                    "choices": [choice.model_dump() for choice in response.choices],
                    "usage": response.usage.model_dump() if response.usage else None,
                    "model": response.model,
                    "id": response.id,
                    "created": response.created
                },
                cost=cost,
                tokens_used=input_tokens + output_tokens
            )
            
        except Exception as e:
            raise APIError(f"Chat completion failed: {str(e)}", self.name)
    
    async def _handle_embeddings(self, data: Dict[str, Any]) -> APIResponse:
        """Handle embedding requests."""
        try:
            input_text = data.get("input", "")
            model = data.get("model", "text-embedding-3-small")
            
            response = await self.client.embeddings.create(
                input=input_text,
                model=model
            )
            
            # Calculate cost (embeddings are priced per token)
            tokens_used = response.usage.total_tokens if response.usage else 0
            cost = self._calculate_embedding_cost(model, tokens_used)
            
            return APIResponse(
                success=True,
                data={
                    "embeddings": [emb.embedding for emb in response.data],
                    "usage": response.usage.model_dump() if response.usage else None,
                    "model": response.model
                },
                cost=cost,
                tokens_used=tokens_used
            )
            
        except Exception as e:
            raise APIError(f"Embeddings request failed: {str(e)}", self.name)
    
    async def _handle_image_generation(self, data: Dict[str, Any]) -> APIResponse:
        """Handle image generation requests."""
        try:
            prompt = data.get("prompt", "")
            model = data.get("model", "dall-e-3")
            size = data.get("size", "1024x1024")
            quality = data.get("quality", "standard")
            n = data.get("n", 1)
            
            response = await self.client.images.generate(
                prompt=prompt,
                model=model,
                size=size,
                quality=quality,
                n=n
            )
            
            # Calculate cost based on model and quality
            cost = self._calculate_image_cost(model, quality, n)
            
            return APIResponse(
                success=True,
                data={
                    "images": [{"url": img.url, "revised_prompt": getattr(img, 'revised_prompt', None)} 
                              for img in response.data]
                },
                cost=cost
            )
            
        except Exception as e:
            raise APIError(f"Image generation failed: {str(e)}", self.name)
    
    async def _handle_text_to_speech(self, data: Dict[str, Any]) -> APIResponse:
        """Handle text-to-speech requests."""
        try:
            input_text = data.get("input", "")
            model = data.get("model", "tts-1")
            voice = data.get("voice", "alloy")
            
            response = await self.client.audio.speech.create(
                input=input_text,
                model=model,
                voice=voice
            )
            
            # Calculate cost (per 1K characters)
            chars = len(input_text)
            cost = self._calculate_tts_cost(model, chars)
            
            # Convert audio to base64 for transport
            import base64
            audio_content = await response.aread()
            audio_base64 = base64.b64encode(audio_content).decode()
            
            return APIResponse(
                success=True,
                data={
                    "audio": audio_base64,
                    "format": "mp3"
                },
                cost=cost
            )
            
        except Exception as e:
            raise APIError(f"Text-to-speech failed: {str(e)}", self.name)
    
    async def _handle_speech_to_text(self, data: Dict[str, Any]) -> APIResponse:
        """Handle speech-to-text requests."""
        try:
            # This would need file handling - simplified for now
            model = data.get("model", "whisper-1")
            language = data.get("language")
            
            # Note: In real implementation, would handle file upload
            return APIResponse(
                success=False,
                error="Speech-to-text requires file upload implementation"
            )
            
        except Exception as e:
            raise APIError(f"Speech-to-text failed: {str(e)}", self.name)
    
    async def _handle_list_models(self) -> APIResponse:
        """Handle list models requests."""
        try:
            response = await self.client.models.list()
            
            return APIResponse(
                success=True,
                data={
                    "models": [model.model_dump() for model in response.data]
                }
            )
            
        except Exception as e:
            raise APIError(f"List models failed: {str(e)}", self.name)
    
    def _calculate_text_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for text generation models."""
        if model not in self.pricing:
            return 0.0
            
        pricing = self.pricing[model]
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return input_cost + output_cost
    
    def _calculate_embedding_cost(self, model: str, tokens: int) -> float:
        """Calculate cost for embedding models."""
        if model not in self.pricing:
            return 0.0
            
        return (tokens / 1000) * self.pricing[model]["input"]
    
    def _calculate_image_cost(self, model: str, quality: str, count: int) -> float:
        """Calculate cost for image generation."""
        if model not in self.pricing:
            return 0.0
            
        if model == "dall-e-3":
            price_per_image = self.pricing[model]["hd"] if quality == "hd" else self.pricing[model]["standard"]
        else:
            price_per_image = self.pricing[model]["standard"]
            
        return price_per_image * count
    
    def _calculate_tts_cost(self, model: str, characters: int) -> float:
        """Calculate cost for text-to-speech."""
        if model not in self.pricing:
            return 0.0
            
        return (characters / 1000) * self.pricing[model]["input"]
    
    def estimate_cost(self, request_data: Dict[str, Any]) -> float:
        """Estimate the cost of a request."""
        endpoint = request_data.get("endpoint", "")
        data = request_data.get("data", {})
        
        if endpoint == "chat/completions":
            # Rough estimation based on message length
            messages = data.get("messages", [])
            model = data.get("model", "gpt-3.5-turbo")
            
            # Estimate tokens (rough: 1 token ≈ 0.75 words)
            total_text = " ".join([msg.get("content", "") for msg in messages])
            estimated_input_tokens = len(total_text.split()) * 1.33
            estimated_output_tokens = data.get("max_tokens", 150)
            
            return self._calculate_text_cost(model, int(estimated_input_tokens), estimated_output_tokens)
            
        elif endpoint == "embeddings":
            input_text = data.get("input", "")
            model = data.get("model", "text-embedding-3-small")
            estimated_tokens = len(input_text.split()) * 1.33
            
            return self._calculate_embedding_cost(model, int(estimated_tokens))
            
        elif endpoint == "images/generations":
            model = data.get("model", "dall-e-3")
            quality = data.get("quality", "standard")
            n = data.get("n", 1)
            
            return self._calculate_image_cost(model, quality, n)
            
        return 0.0
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "api_base": "https://api.openai.com/v1",
            "supported_endpoints": [
                "chat/completions",
                "embeddings", 
                "images/generations",
                "audio/speech",
                "audio/transcriptions",
                "models"
            ],
            "available_models": {
                "chat": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
                "embeddings": ["text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002"],
                "images": ["dall-e-3", "dall-e-2"],
                "audio": ["tts-1", "tts-1-hd", "whisper-1"]
            },
            "pricing_info": self.pricing,
            "has_api_key": bool(self.api_key),
            "usage_stats": self.get_usage_summary()
        }
