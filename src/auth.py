"""
Authentication and security utilities for DB RAG API
"""

import os
import secrets
from typing import Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel


class APIKeyConfig:
    """Configuration for API key authentication"""
    
    def __init__(self):
        # Get API keys from environment or generate default for development
        self.api_keys = self._load_api_keys()
        self.require_auth = os.getenv("REQUIRE_AUTH", "false").lower() == "true"
    
    def _load_api_keys(self) -> set:
        """Load API keys from environment"""
        env_keys = os.getenv("API_KEYS", "")
        if env_keys:
            return set(key.strip() for key in env_keys.split(",") if key.strip())
        
        # Development default
        dev_key = os.getenv("DEV_API_KEY", "dev-api-key-12345")
        return {dev_key}
    
    def is_valid_key(self, api_key: str) -> bool:
        """Check if API key is valid"""
        return api_key in self.api_keys
    
    def get_development_key(self) -> str:
        """Get the development API key for documentation"""
        return list(self.api_keys)[0] if self.api_keys else "dev-api-key-12345"


# Global configuration instance
auth_config = APIKeyConfig()

# Security scheme for FastAPI
security = HTTPBearer(auto_error=False)


async def verify_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> str:
    """
    Verify API key from Authorization header
    Returns the API key if valid, raises HTTPException if invalid
    """
    # Skip authentication in development mode if not required
    if not auth_config.require_auth:
        return "development-mode"
    
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Missing authentication",
                "error_code": "MISSING_AUTH",
                "details": {
                    "message": "Authorization header with Bearer token required",
                    "example": f"Authorization: Bearer {auth_config.get_development_key()}"
                }
            }
        )
    
    if not auth_config.is_valid_key(credentials.credentials):
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Invalid API key",
                "error_code": "INVALID_API_KEY",
                "details": {
                    "message": "The provided API key is not valid",
                    "hint": "Check your API key or contact support"
                }
            }
        )
    
    return credentials.credentials


class AuthModels:
    """Pydantic models for authentication"""
    
    class APIKeyInfo(BaseModel):
        """Information about API key authentication"""
        required: bool
        development_mode: bool
        development_key: Optional[str] = None
        
    class AuthError(BaseModel):
        """Authentication error response"""
        error: str
        error_code: str
        details: dict


def get_auth_info() -> AuthModels.APIKeyInfo:
    """Get current authentication configuration info"""
    return AuthModels.APIKeyInfo(
        required=auth_config.require_auth,
        development_mode=not auth_config.require_auth,
        development_key=auth_config.get_development_key() if not auth_config.require_auth else None
    )


def generate_api_key() -> str:
    """Generate a secure API key"""
    return f"dbrag-{secrets.token_urlsafe(32)}"


# Rate limiting (basic implementation)
class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, max_requests: int = 100, window_minutes: int = 60):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.requests = {}  # {api_key: [(timestamp, count), ...]}
    
    def is_allowed(self, api_key: str) -> bool:
        """Check if request is allowed under rate limit"""
        now = datetime.now()
        window_start = now - timedelta(minutes=self.window_minutes)
        
        if api_key not in self.requests:
            self.requests[api_key] = []
        
        # Clean old requests
        self.requests[api_key] = [
            (timestamp, count) for timestamp, count in self.requests[api_key]
            if timestamp > window_start
        ]
        
        # Count current requests
        current_count = sum(count for _, count in self.requests[api_key])
        
        if current_count >= self.max_requests:
            return False
        
        # Add current request
        self.requests[api_key].append((now, 1))
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


async def check_rate_limit(api_key: str = Depends(verify_api_key)) -> str:
    """Check rate limiting for the current API key"""
    if not rate_limiter.is_allowed(api_key):
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "details": {
                    "message": f"Maximum {rate_limiter.max_requests} requests per {rate_limiter.window_minutes} minutes",
                    "retry_after": "60 seconds"
                }
            }
        )
    return api_key
