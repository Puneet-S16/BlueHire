"""
Rate limiting configuration for the FastAPI application.

Uses `slowapi`. Local development uses in-memory storage (no external
infrastructure required). Production deployments behind a reverse proxy should
switch the `storage_uri` to Redis (e.g. `redis://localhost:6379`) and ensure
the proxy forwards `X-Forwarded-For` / `X-Real-IP` so `get_remote_address`
resolves the real client IP rather than the proxy IP.

Trust configuration:
- If BlueHire sits behind a trusted reverse proxy, configure the proxy to
  send `X-Forwarded-For` and set `TRUSTED_PROXIES` (or equivalent) so the
  rate limiter keys on the original client IP. Without this, all clients
  behind the same proxy share one rate-limit bucket.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Default storage is in-memory. Override with REDIS_URL in production.
# Example production value: storage_uri="redis://redis:6379"
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")

__all__ = ["limiter"]
