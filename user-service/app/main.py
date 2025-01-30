from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.api import users
from app.core.database import engine
from app.core.models.user import Base

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