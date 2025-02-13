import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # CORS settings
    ALLOWED_ORIGINS: list = ["*"]
    
    # Service settings
    SERVICE_NAME: str = "user-service"
    VERSION: str = "0.1.0"
    
    # Service URLs
    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    USER_SERVICE_URL: str = "http://user-service:8001"
    ID_SERVICE_URL: str = "http://id-service:8002"

    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 

# Validate database URL format
if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables") 