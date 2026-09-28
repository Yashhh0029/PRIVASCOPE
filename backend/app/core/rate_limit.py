import time
from collections import defaultdict
from threading import Lock
from typing import Dict, List
from fastapi import Request, HTTPException, status

class InMemoryRateLimiter:
    """
    Sliding-window rate limiter by client IP.
    Protects authentication endpoints (like /api/auth/google) against brute-force / abuse.
    
    Production Note:
    For multi-instance / autoscaled deployments behind a load balancer,
    this interface can be backed by a centralized Redis cluster via REDIS_URL.
    """
    def __init__(self, max_requests: int = 15, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, request: Request) -> None:
        # Extract client IP (respecting X-Forwarded-For if behind a reverse proxy)
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "127.0.0.1"

        now = time.time()
        with self._lock:
            timestamps = self._requests[client_ip]
            # Prune timestamps older than window
            cutoff = now - self.window_seconds
            self._requests[client_ip] = [t for t in timestamps if t > cutoff]

            if len(self._requests[client_ip]) >= self.max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many authentication attempts. Please wait a minute before retrying."
                )

            self._requests[client_ip].append(now)

auth_rate_limiter = InMemoryRateLimiter(max_requests=20, window_seconds=60)
