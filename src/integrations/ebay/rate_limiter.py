"""
Rate limiter for eBay API requests.
"""
import time
import threading
from collections import deque
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter for API requests."""

    def __init__(self, calls_per_second: int = 5, burst: int = 10):
        """Initialize rate limiter.

        Args:
            calls_per_second: Maximum calls per second
            burst: Maximum burst size
        """
        self.calls_per_second = calls_per_second
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
        self.lock = threading.Lock()

        logger.info(f"Rate limiter initialized: {calls_per_second} calls/sec, burst={burst}")

    def _add_tokens(self):
        """Add tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update
        new_tokens = elapsed * self.calls_per_second

        self.tokens = min(self.burst, self.tokens + new_tokens)
        self.last_update = now

    def acquire(self, tokens: int = 1, timeout: float = 10.0) -> bool:
        """Acquire tokens for API call.

        Args:
            tokens: Number of tokens to acquire
            timeout: Maximum time to wait for tokens (seconds)

        Returns:
            True if tokens acquired, False if timeout

        """
        start_time = time.time()

        while True:
            with self.lock:
                self._add_tokens()

                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True

            # Check timeout
            if time.time() - start_time >= timeout:
                logger.warning(f"Rate limiter timeout after {timeout}s")
                return False

            # Wait a bit before retrying
            time.sleep(0.1)

    def __call__(self, func: Callable) -> Callable:
        """Decorator to rate limit function calls.

        Args:
            func: Function to rate limit

        Returns:
            Wrapped function
        """
        def wrapper(*args, **kwargs) -> Any:
            if self.acquire():
                return func(*args, **kwargs)
            else:
                raise Exception("Rate limit exceeded")

        return wrapper


class RequestTracker:
    """Track API request history for monitoring."""

    def __init__(self, window_size: int = 3600):
        """Initialize request tracker.

        Args:
            window_size: Time window in seconds (default 1 hour)
        """
        self.window_size = window_size
        self.requests = deque()
        self.lock = threading.Lock()

    def record_request(self, endpoint: str, status_code: int):
        """Record an API request.

        Args:
            endpoint: API endpoint called
            status_code: HTTP status code
        """
        with self.lock:
            now = time.time()

            # Remove old requests outside window
            while self.requests and self.requests[0][0] < now - self.window_size:
                self.requests.popleft()

            # Add new request
            self.requests.append((now, endpoint, status_code))

    def get_stats(self) -> dict:
        """Get request statistics.

        Returns:
            Dictionary with request stats
        """
        with self.lock:
            now = time.time()

            # Remove old requests
            while self.requests and self.requests[0][0] < now - self.window_size:
                self.requests.popleft()

            total_requests = len(self.requests)
            success_count = sum(1 for _, _, status in self.requests if 200 <= status < 300)
            error_count = total_requests - success_count

            # Requests per minute
            if self.requests:
                time_span = now - self.requests[0][0]
                rpm = (total_requests / time_span * 60) if time_span > 0 else 0
            else:
                rpm = 0

            return {
                "total_requests": total_requests,
                "success_count": success_count,
                "error_count": error_count,
                "requests_per_minute": round(rpm, 2),
                "window_size": self.window_size,
            }
