import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # Service URLs
    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    USER_SERVICE_URL: str = "http://user-service:8001"
    ID_SERVICE_URL: str = "http://id-service:8002"

    class Config:
        case_sensitive = True

settings = Settings() 