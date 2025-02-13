from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/digital_id"
    
    # JWT settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    ALLOWED_ORIGINS: list = ["*"]
    
    # Service settings
    SERVICE_NAME: str = "user-service"
    VERSION: str = "0.1.0"
    
    # Service URLs
    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    USER_SERVICE_URL: str = "http://user-service:8001"
    ID_SERVICE_URL: str = "http://id-service:8002"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 