from fastapi import HTTPException
from jose import JWTError, jwt
from app.core.config import settings
import hiredis
import time
from typing import Optional

redis = hiredis.from_url(settings.REDIS_URL)

async def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check if token is blacklisted
        if await redis.get(f"blacklist:{token}"):
            raise HTTPException(
                status_code=401,
                detail="Token has been revoked"
            )
            
        return {
            "sub": payload.get("sub"),
            "scopes": payload.get("scopes", []),
            "access_token": token
        }
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_limit: int = 100
    ):
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        
    async def is_rate_limited(self, user_id: str) -> bool:
        """Check if user has exceeded rate limit"""
        current = int(time.time())
        key = f"ratelimit:{user_id}:{current // 60}"
        
        # Get current request count
        count = await redis.get(key)
        if not count:
            # First request in this minute
            await redis.setex(key, 60, 1)
            return False
            
        count = int(count)
        if count >= self.burst_limit:
            return True
            
        # Increment request count
        await redis.incr(key)
        return count >= self.requests_per_minute 