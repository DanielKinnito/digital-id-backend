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
from app.core.api import users
from app.core.database import engine
from app.core.models import Base, RoleType
from app.core.auth.permissions import Permissions, ROLE_PERMISSIONS

# Ensure the app directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Define security schemes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description="""
# Role-Based Access Control

This API implements role-based access control with the following roles:

## Roles and Permissions

### Super Admin
- Full system access
- Can manage all users and institutions
- Can assign roles and permissions
- Has access to audit logs

### Institutional Admin
- Can manage users within their institution
- Can create and manage institutional IDs
- Can view and update institutional settings

### Resident
- Can view their own profile and ID
- Can request updates to their information
- Limited access to system features

### Staff
- Can view user information
- Can create new IDs
- Limited administrative capabilities

## Authentication

All endpoints require a valid JWT token obtained through the /auth/token endpoint.
Include the token in the Authorization header as: `Bearer <token>`

## Error Responses

- 401: Unauthorized - Invalid or missing token
- 403: Forbidden - Insufficient permissions
- 404: Not Found - Requested resource doesn't exist
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

    # Add role-based security requirements
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            # Add security requirement
            operation["security"] = [{"OAuth2PasswordBearer": []}]
            
            # Add role-based tags
            if "tags" in operation:
                required_permissions = operation.get("x-permissions", [])
                for role, permissions in ROLE_PERMISSIONS.items():
                    if all(perm in permissions for perm in required_permissions):
                        operation["tags"].append(f"Role: {role.value}")

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app = FastAPI(
    title="Digital ID System - User Service",
    description="API for managing user data and biometrics in the Digital ID System",
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

# Download Swagger UI files if they don't exist
import httpx
async def download_swagger_files():
    swagger_ui_files = {
        "swagger-ui-bundle.js": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        "swagger-ui.css": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"
    }
    
    for filename, url in swagger_ui_files.items():
        filepath = os.path.join("static", filename)
        if not os.path.exists(filepath):
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                with open(filepath, "wb") as f:
                    f.write(response.content)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Swagger UI",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,  # Hide schemas section by default
            "docExpansion": "none",  # Collapse operations by default
            "filter": True,  # Enable filtering
            "tagsSorter": "alpha",  # Sort tags alphabetically
            "operationsSorter": "alpha",  # Sort operations alphabetically
        }
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return custom_openapi()

@app.on_event("startup")
async def startup():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Download Swagger UI files
    await download_swagger_files()

# Include routers with role-based documentation
app.include_router(
    users.router,
    prefix="/api/users",
    tags=["users"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing token"},
        403: {"description": "Forbidden - Insufficient permissions"},
        404: {"description": "Not found"},
        422: {"description": "Validation Error"}
    }
)