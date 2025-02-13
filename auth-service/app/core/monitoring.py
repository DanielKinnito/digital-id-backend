from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
import time
import logging
from typing import Callable
import json

# Configure logging
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_request_count_total",
    "Total count of HTTP requests",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

ERROR_COUNT = Counter(
    "http_error_count_total",
    "Total count of HTTP errors",
    ["method", "endpoint", "error_type"]
)

def init_monitoring(app: FastAPI):
    """Initialize monitoring for the FastAPI app"""
    
    # Initialize Prometheus metrics
    Instrumentator().instrument(app).expose(app)
    
    @app.get("/metrics")
    async def metrics():
        return generate_latest()
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": time.time()
        }

async def log_request_middleware(request: Request, call_next: Callable):
    """Middleware to log requests and collect metrics"""
    start_time = time.time()
    method = request.method
    path = request.url.path
    
    # Log request
    logger.info(
        f"Request started",
        extra={
            "method": method,
            "path": path,
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent")
        }
    )
    
    try:
        response = await call_next(request)
        
        # Update metrics
        REQUEST_COUNT.labels(
            method=method,
            endpoint=path,
            status_code=response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=method,
            endpoint=path
        ).observe(time.time() - start_time)
        
        # Log response
        logger.info(
            f"Request completed",
            extra={
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration": time.time() - start_time
            }
        )
        
        return response
        
    except Exception as e:
        # Log error
        logger.error(
            f"Request failed",
            extra={
                "method": method,
                "path": path,
                "error": str(e),
                "duration": time.time() - start_time
            },
            exc_info=True
        )
        
        # Update error metrics
        ERROR_COUNT.labels(
            method=method,
            endpoint=path,
            error_type=type(e).__name__
        ).inc()
        
        raise 