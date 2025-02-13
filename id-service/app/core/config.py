import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables first
load_dotenv()

class Settings(BaseSettings):
    # JWT Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database Settings
    DATABASE_URL: str

    # Service URLs
    AUTH_SERVICE_URL: str = "http://localhost:8000"
    USER_SERVICE_URL: str = "http://localhost:8001"
    ID_SERVICE_URL: str = "http://localhost:8002"

    class Config:
        case_sensitive = True

    @property
    def async_database_url(self) -> str:
        """Convert DATABASE_URL to async format if needed"""
        if self.DATABASE_URL.startswith('postgresql://'):
            return self.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)
        return self.DATABASE_URL

    def validate_settings(self):
        """Validate critical settings"""
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY must be set in environment variables")
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set in environment variables")

# Initialize settings
settings = Settings()
# Validate critical settings
settings.validate_settings() 