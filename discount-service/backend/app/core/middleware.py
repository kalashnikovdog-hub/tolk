"""
Rate Limiting Middleware for brute-force protection
"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.settings import settings
from app.core.exceptions import RateLimitExceededException


class RateLimiter:
    """In-memory rate limiter with sliding window"""
    
    def __init__(self):
        # Store: {identifier: [(timestamp, count)]}
        self.requests: Dict[str, list] = defaultdict(list)
        
        # Default limits
        self.default_limit = 100  # requests per minute
        self.auth_limit = 10  # stricter limit for auth endpoints
        self.window_seconds = 60
    
    def _clean_old_requests(self, identifier: str, current_time: float):
        """Remove requests older than the window"""
        if identifier in self.requests:
            cutoff = current_time - self.window_seconds
            self.requests[identifier] = [
                (ts, count) for ts, count in self.requests[identifier]
                if ts > cutoff
            ]
    
    def is_rate_limited(
        self,
        identifier: str,
        limit: int = None,
        window: int = None
    ) -> Tuple[bool, int, int, int]:
        """
        Check if identifier is rate limited
        
        Returns: (is_limited, remaining, reset_time, retry_after)
        """
        if limit is None:
            limit = self.default_limit
        if window is None:
            window = self.window_seconds
        
        current_time = time.time()
        self._clean_old_requests(identifier, current_time)
        
        # Count total requests in current window
        total_requests = sum(count for _, count in self.requests[identifier])
        
        # Calculate reset time (when oldest request expires)
        if self.requests[identifier]:
            oldest_request = min(ts for ts, _ in self.requests[identifier])
            reset_time = int(oldest_request + window)
        else:
            reset_time = int(current_time + window)
        
        # Check if limit exceeded
        if total_requests >= limit:
            retry_after = reset_time - int(current_time)
            return True, 0, reset_time, max(1, retry_after)
        
        # Record this request
        self.requests[identifier].append((current_time, 1))
        remaining = limit - total_requests - 1
        
        return False, remaining, reset_time, 0
    
    def record_request(self, identifier: str):
        """Record a request for an identifier"""
        current_time = time.time()
        self.requests[identifier].append((current_time, 1))


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to apply rate limiting to all requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP address or user ID)
        client_ip = request.client.host if request.client else "unknown"
        
        # Try to get user ID from token if authenticated
        user_id = getattr(request.state, "user_id", None)
        identifier = f"user:{user_id}" if user_id else f"ip:{client_ip}"
        
        # Determine rate limit based on endpoint
        path = request.url.path
        if "/auth/" in path:
            # Stricter limits for authentication endpoints
            limit = rate_limiter.auth_limit
        else:
            limit = rate_limiter.default_limit
        
        # Check rate limit
        is_limited, remaining, reset_time, retry_after = rate_limiter.is_rate_limited(
            identifier, limit=limit
        )
        
        if is_limited:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "message": "Rate limit exceeded",
                    "detail": "Too many requests. Please try again later."
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(retry_after)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response
