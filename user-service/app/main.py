import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.api import users
from app.core.database import engine
from app.core.models import Base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure the app directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="User Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(users.router, prefix="/api/users", tags=["users"])