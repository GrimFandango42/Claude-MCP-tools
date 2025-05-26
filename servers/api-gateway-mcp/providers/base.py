"""
Base API Provider for API Gateway MCP Server
Provides common interface and functionality for all API providers.
"""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

@dataclass
class APIResponse:
    """Standardized API response format."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    provider: Optional[str] = None
    cached: bool = False
    cost: float = 0.0
    tokens_used: int = 0
    response_time_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RateLimitInfo:
    """Rate limiting information."""
    requests_per_minute: int = 60
    requests_per_hour: int = 3600
    requests_per_day: int = 100000
    current_minute_count: int = 0
    current_hour_count: int = 0
    current_day_count: int = 0
    reset_minute: datetime = field(default_factory=datetime.now)
    reset_hour: datetime = field(default_factory=datetime.now)
    reset_day: datetime = field(default_factory=datetime.now)

@dataclass
class UsageStats:
    """Usage statistics for a provider."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cached_requests: int = 0
    total_cost: float = 0.0
    total_tokens: int = 0
    avg_response_time_ms: float = 0.0
    last_request: Optional[datetime] = None
    rate_limit_info: RateLimitInfo = field(default_factory=RateLimitInfo)


class BaseAPIProvider(ABC):
    """Abstract base class for all API providers."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.enabled = config.get('enabled', True)
        self.api_key = config.get('api_key', '')
        self.base_url = config.get('base_url', '')
        
        # Initialize usage tracking
        self.usage_stats = UsageStats()
        
        # Setup logging
        self.logger = logging.getLogger(f"api-gateway.{name}")
        
        # Initialize rate limiting
        self._init_rate_limiting()
        
    def _init_rate_limiting(self):
        """Initialize rate limiting configuration."""
        rate_config = self.config.get('rate_limits', {})
        self.usage_stats.rate_limit_info = RateLimitInfo(
            requests_per_minute=rate_config.get('per_minute', 60),
            requests_per_hour=rate_config.get('per_hour', 3600),
            requests_per_day=rate_config.get('per_day', 100000)
        )
    
    @abstractmethod
    async def call_api(self, endpoint: str, method: str = "POST", 
                      data: Optional[Dict[str, Any]] = None,
                      headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Make an API call to the provider."""
        pass
    
    @abstractmethod
    def estimate_cost(self, request_data: Dict[str, Any]) -> float:
        """Estimate the cost of a request."""
        pass
    
    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        pass
    
    async def check_rate_limits(self) -> bool:
        """Check if request is within rate limits."""
        now = datetime.now()
        rate_info = self.usage_stats.rate_limit_info
        
        # Reset counters if time windows have passed
        if now >= rate_info.reset_minute + timedelta(minutes=1):
            rate_info.current_minute_count = 0
            rate_info.reset_minute = now
            
        if now >= rate_info.reset_hour + timedelta(hours=1):
            rate_info.current_hour_count = 0
            rate_info.reset_hour = now
            
        if now >= rate_info.reset_day + timedelta(days=1):
            rate_info.current_day_count = 0
            rate_info.reset_day = now
        
        # Check limits
        if rate_info.current_minute_count >= rate_info.requests_per_minute:
            self.logger.warning(f"Rate limit exceeded: {rate_info.current_minute_count}/{rate_info.requests_per_minute} per minute")
            return False
            
        if rate_info.current_hour_count >= rate_info.requests_per_hour:
            self.logger.warning(f"Rate limit exceeded: {rate_info.current_hour_count}/{rate_info.requests_per_hour} per hour")
            return False
            
        if rate_info.current_day_count >= rate_info.requests_per_day:
            self.logger.warning(f"Rate limit exceeded: {rate_info.current_day_count}/{rate_info.requests_per_day} per day")
            return False
            
        return True
    
    def increment_rate_counters(self):
        """Increment rate limiting counters."""
        rate_info = self.usage_stats.rate_limit_info
        rate_info.current_minute_count += 1
        rate_info.current_hour_count += 1
        rate_info.current_day_count += 1
    
    def update_usage_stats(self, response: APIResponse):
        """Update usage statistics after a request."""
        self.usage_stats.total_requests += 1
        self.usage_stats.last_request = datetime.now()
        
        if response.success:
            self.usage_stats.successful_requests += 1
        else:
            self.usage_stats.failed_requests += 1
            
        if response.cached:
            self.usage_stats.cached_requests += 1
            
        self.usage_stats.total_cost += response.cost
        self.usage_stats.total_tokens += response.tokens_used
        
        # Update average response time
        total_time = (self.usage_stats.avg_response_time_ms * 
                     (self.usage_stats.total_requests - 1) + 
                     response.response_time_ms)
        self.usage_stats.avg_response_time_ms = total_time / self.usage_stats.total_requests
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        rate_info = self.usage_stats.rate_limit_info
        now = datetime.now()
        
        return {
            "requests_per_minute": {
                "limit": rate_info.requests_per_minute,
                "used": rate_info.current_minute_count,
                "remaining": rate_info.requests_per_minute - rate_info.current_minute_count,
                "reset_in_seconds": max(0, int((rate_info.reset_minute + timedelta(minutes=1) - now).total_seconds()))
            },
            "requests_per_hour": {
                "limit": rate_info.requests_per_hour,
                "used": rate_info.current_hour_count,
                "remaining": rate_info.requests_per_hour - rate_info.current_hour_count,
                "reset_in_seconds": max(0, int((rate_info.reset_hour + timedelta(hours=1) - now).total_seconds()))
            },
            "requests_per_day": {
                "limit": rate_info.requests_per_day,
                "used": rate_info.current_day_count,
                "remaining": rate_info.requests_per_day - rate_info.current_day_count,
                "reset_in_seconds": max(0, int((rate_info.reset_day + timedelta(days=1) - now).total_seconds()))
            }
        }
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage statistics summary."""
        success_rate = (self.usage_stats.successful_requests / 
                       max(1, self.usage_stats.total_requests) * 100)
        cache_hit_rate = (self.usage_stats.cached_requests / 
                         max(1, self.usage_stats.total_requests) * 100)
        
        return {
            "provider": self.name,
            "enabled": self.enabled,
            "total_requests": self.usage_stats.total_requests,
            "successful_requests": self.usage_stats.successful_requests,
            "failed_requests": self.usage_stats.failed_requests,
            "cached_requests": self.usage_stats.cached_requests,
            "success_rate_percent": round(success_rate, 2),
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "total_cost_usd": round(self.usage_stats.total_cost, 4),
            "total_tokens": self.usage_stats.total_tokens,
            "avg_response_time_ms": round(self.usage_stats.avg_response_time_ms, 2),
            "last_request": self.usage_stats.last_request.isoformat() if self.usage_stats.last_request else None,
            "rate_limits": self.get_rate_limit_status()
        }


class ProviderError(Exception):
    """Base exception for provider errors."""
    def __init__(self, message: str, provider: str, error_code: Optional[str] = None):
        self.message = message
        self.provider = provider
        self.error_code = error_code
        super().__init__(f"[{provider}] {message}")


class RateLimitError(ProviderError):
    """Exception raised when rate limits are exceeded."""
    pass


class AuthenticationError(ProviderError):
    """Exception raised when authentication fails."""
    pass


class APIError(ProviderError):
    """Exception raised when API calls fail."""
    pass
