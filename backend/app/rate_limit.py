"""
Rate limiting with SlowAPI.
Limiter is configured in main.py (app.state.limiter).
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from .config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT] if settings.RATE_LIMIT_DEFAULT else [],
)
