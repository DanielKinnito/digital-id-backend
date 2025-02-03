from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.schemas.user import UserCreate, UserResponse
from app.core.models import User, BiometricData
from app.core.biometrics.fingerprint_handler import FingerPrintHandler
from app.core.utils.serializer import DataSerializer
from typing import List
import asyncio
import base64
import os

router = APIRouter()
fingerprint_handler = FingerPrintHandler()
serializer = DataSerializer()

@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    photo_file: UploadFile = File(...),
    # background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # Initialize fingerprint device
    if not fingerprint_handler.initialize():
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize fingerprint system"
        )

    try:
        # Create user first
        db_user = User(**user.dict())
        db.add(db_user)
        await db.flush()

        # Capture fingerprint with retry logic
        max_attempts = 3
        template = None
        
        for attempt in range(max_attempts):
            template = fingerprint_handler.capture_fingerprint()
            if template:
                break
            await asyncio.sleep(1)  # Wait before retry

        if not template:
            raise HTTPException(
                status_code=400,
                detail="Failed to capture fingerprint after multiple attempts"
            )

        # Encrypt and encode the template
        encrypted_template = serializer.serialize(template.hex())

        # Save photo file
        photo_path = f"photos/{db_user.id}/{photo_file.filename}"
        contents = await photo_file.read()
        
        # Create biometric record
        biometric_data = BiometricData(
            user_id=db_user.id,
            fingerprint_template=encrypted_template,
            photo_reference=photo_path
        )
        db.add(biometric_data)
        
        # Save changes
        await db.commit()
        await db.refresh(db_user)
        
        # Add background task to save photo
        # background_tasks.add_task(save_photo, photo_path, contents)
        
        return db_user
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating user: {str(e)}"
        )
    finally:
        fingerprint_handler.close()

async def save_photo(path: str, contents: bytes):
    """Save photo file to disk"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(contents)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user 