import sys
import os
from dotenv import load_dotenv
from typing import Dict, List
from enum import Enum

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer
from app.core.database import engine
from app.core.models import Base
from app.core.api import digital_ids
from app.core.auth.permissions import Permissions, ROLE_PERMISSIONS

# Ensure the app directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description="""
# Digital ID Service API

This service manages digital identification documents and their lifecycle.

## Features
- Digital ID Creation
- ID Verification
- ID Status Management
- Revocation Handling
- ID Document Generation

## Authentication
All endpoints require a valid JWT token obtained through the auth service.
Include the token in the Authorization header as: `Bearer <token>`

## Error Responses
- 401: Unauthorized - Invalid or missing token
- 403: Forbidden - Insufficient permissions
- 404: Not Found - ID not found
- 422: Validation Error - Invalid request data
        """,
        routes=app.routes,
    )

    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "token",
                    "scopes": {
                        "super_admin": "Full system access",
                        "institutional_admin": "Institution management access",
                        "resident": "Resident access",
                        "staff": "Staff access"
                    }
                }
            }
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app = FastAPI(
    title="Digital ID System - ID Service",
    description="API for managing digital identification documents",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None  # Disable default redoc
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static directory if it doesn't exist
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
os.makedirs(static_dir, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Swagger UI",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return custom_openapi()

@app.on_event("startup")
async def startup():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Include routers
app.include_router(
    digital_ids.router,
    prefix="/api/ids",
    tags=["digital-ids"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing token"},
        403: {"description": "Forbidden - Insufficient permissions"},
        404: {"description": "Not found"},
        422: {"description": "Validation Error"}
    }
) 