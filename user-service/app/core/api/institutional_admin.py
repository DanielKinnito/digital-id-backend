from fastapi import APIRouter, Depends, HTTPException, Security, File, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.auth import get_current_user, require_institutional_admin, has_permission
from app.core.schemas.user import UserCreate, UserResponse, UserUpdate
from app.core.schemas.institutional_admin import UserSuspend, UpdateApproval, AdminActionLog
from app.core.models import User, BiometricData, UpdateRequest, AdminAction
from app.core.biometrics.fingerprint_handler import FingerPrintHandler
from app.core.utils.serializer import DataSerializer
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio

router = APIRouter()
fingerprint_handler = FingerPrintHandler()
serializer = DataSerializer()

@router.post("/users", response_model=UserResponse)
async def register_user(
    user: UserCreate,
    photo_file: UploadFile = File(...),
    current_user: User = Security(get_current_user, scopes=["institutional_admin"]),
    db: AsyncSession = Depends(get_db)
):
    """Register a new resident"""
    # Verify admin's institution is active
    if not current_user.is_active or not current_user.institution.is_active:
        raise HTTPException(
            status_code=403,
            detail="Administrator or institution is not active"
        )

    # Initialize fingerprint device
    if not fingerprint_handler.initialize():
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize fingerprint system"
        )

    try:
        # Check for existing user with same email or phone
        result = await db.execute(
            select(User).where(
                (User.email == user.email) | 
                (User.phone_number == user.phone_number)
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="User with this email or phone number already exists"
            )

        # Create user
        db_user = User(
            **user.dict(),
            created_by=current_user.id,
            institution_id=current_user.institution_id
        )
        db.add(db_user)
        await db.flush()

        # Capture and store biometric data
        template = await capture_fingerprint_with_retry()
        if not template:
            raise HTTPException(
                status_code=400,
                detail="Failed to capture fingerprint"
            )

        # Save biometric data
        await save_biometric_data(db, db_user, template, photo_file)

        # Log admin action
        action_log = AdminAction(
            admin_id=current_user.id,
            action_type="user_registration",
            user_id=db_user.id,
            details={"registration_type": "new_resident"}
        )
        db.add(action_log)

        await db.commit()
        await db.refresh(db_user)
        return db_user

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error registering user: {str(e)}"
        )
    finally:
        fingerprint_handler.close()

@router.patch("/users/{user_id}/suspend", response_model=UserResponse)
async def suspend_user_id(
    user_id: int,
    suspension: UserSuspend,
    current_user: User = Security(get_current_user, scopes=["institutional_admin"]),
    db: AsyncSession = Depends(get_db)
):
    """Suspend a user's ID"""
    # Get user and verify institution
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.institution_id != current_user.institution_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot suspend user from different institution"
        )

    # Update user status
    user.status = "suspended"
    user.last_updated_by = current_user.id
    
    # Calculate suspension end date if duration provided
    if suspension.suspension_duration_days:
        user.suspension_end_date = datetime.utcnow() + timedelta(
            days=suspension.suspension_duration_days
        )

    # Log suspension
    action_log = AdminAction(
        admin_id=current_user.id,
        action_type="user_suspension",
        user_id=user_id,
        details={
            "reason": suspension.reason,
            "description": suspension.description,
            "duration_days": suspension.suspension_duration_days
        }
    )
    db.add(action_log)

    await db.commit()
    await db.refresh(user)
    return user

@router.get("/update-requests", response_model=List[UpdateRequest])
async def list_update_requests(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Security(get_current_user, scopes=["institutional_admin"]),
    db: AsyncSession = Depends(get_db)
):
    """List update requests for users in admin's institution"""
    query = select(UpdateRequest).join(User).where(
        User.institution_id == current_user.institution_id
    )
    
    if status:
        query = query.where(UpdateRequest.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/update-requests/{request_id}/review", response_model=UpdateRequest)
async def review_update_request(
    request_id: int,
    approval: UpdateApproval,
    current_user: User = Security(get_current_user, scopes=["institutional_admin"]),
    db: AsyncSession = Depends(get_db)
):
    """Review and approve/reject an update request"""
    update_request = await db.get(UpdateRequest, request_id)
    if not update_request:
        raise HTTPException(status_code=404, detail="Update request not found")

    # Verify user belongs to admin's institution
    user = await db.get(User, update_request.user_id)
    if user.institution_id != current_user.institution_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot review request from different institution"
        )

    if approval.approved:
        # Apply the requested changes
        for field, value in update_request.requested_changes.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        update_request.status = "approved"
        user.last_updated_by = current_user.id
    else:
        update_request.status = "rejected"
        update_request.rejection_reason = approval.rejection_reason

    update_request.reviewed_by = current_user.id
    update_request.reviewed_at = datetime.utcnow()

    # Log admin action
    action_log = AdminAction(
        admin_id=current_user.id,
        action_type="update_request_review",
        user_id=update_request.user_id,
        details={
            "request_id": request_id,
            "approved": approval.approved,
            "rejection_reason": approval.rejection_reason
        }
    )
    db.add(action_log)

    await db.commit()
    await db.refresh(update_request)
    return update_request

@router.get("/users", response_model=List[UserResponse])
@has_permission(["view_users"])
async def list_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List users for institutional admin"""
    # Implementation here
    pass

async def capture_fingerprint_with_retry(max_attempts: int = 3) -> Optional[bytes]:
    """Helper function to capture fingerprint with retry logic"""
    for attempt in range(max_attempts):
        template = fingerprint_handler.capture_fingerprint()
        if template:
            return template
        await asyncio.sleep(1)
    return None

async def save_biometric_data(
    db: AsyncSession,
    user: User,
    template: bytes,
    photo_file: UploadFile
) -> None:
    """Helper function to save biometric data"""
    # Encrypt and encode template
    encrypted_template = serializer.serialize(template.hex())

    # Save photo file
    photo_path = f"photos/{user.id}/{photo_file.filename}"
    contents = await photo_file.read()
    
    # Create biometric record
    biometric_data = BiometricData(
        user_id=user.id,
        fingerprint_template=encrypted_template,
        photo_reference=photo_path
    )
    db.add(biometric_data) 