from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.auth import verify_token, RateLimiter
from app.core.config import settings
import httpx
import time
from typing import Optional

app = FastAPI(
    title="Digital ID System - API Gateway",
    description="API Gateway for Digital ID System",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize rate limiter
rate_limiter = RateLimiter()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

async def get_token_header(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )
    
    try:
        token = authorization.split(" ")[1]
        return await verify_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )

# Auth Service Routes
@app.post("/api/auth/login")
async def auth_login(request: Request):
    """Forward login requests to auth service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.AUTH_SERVICE_URL}/auth/login",
            json=await request.json()
        )
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )

# User Service Routes
@app.get("/api/users/me")
async def get_current_user(token_data: dict = Depends(get_token_header)):
    """Get current user profile"""
    if await rate_limiter.is_rate_limited(token_data["sub"]):
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.USER_SERVICE_URL}/users/me",
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )

# ID Service Routes
@app.post("/api/institutional-ids")
async def create_institutional_id(
    request: Request,
    token_data: dict = Depends(get_token_header)
):
    """Create new institutional ID"""
    if "institution" not in token_data["scopes"]:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions"
        )

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ID_SERVICE_URL}/institutional-ids",
            json=await request.json(),
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Check health of all services"""
    services = {
        "auth": settings.AUTH_SERVICE_URL,
        "user": settings.USER_SERVICE_URL,
        "id": settings.ID_SERVICE_URL
    }
    
    health_status = {}
    async with httpx.AsyncClient() as client:
        for service, url in services.items():
            try:
                response = await client.get(f"{url}/health")
                health_status[service] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "details": response.json()
                }
            except Exception as e:
                health_status[service] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
    
    return health_status 