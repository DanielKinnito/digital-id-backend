from fastapi import APIRouter, Depends, HTTPException, Security, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.auth import get_current_user, has_permission
from app.core.schemas.resident import (
    UpdateRequestCreate,
    UpdateRequestResponse,
    ResidentIDResponse,
    UpdateField
)
from app.core.models import User, UpdateRequest, BiometricData
from app.core.utils.serializer import DataSerializer
from typing import List
from datetime import datetime

router = APIRouter()
serializer = DataSerializer()

@router.get("/my-id", response_model=ResidentIDResponse)
@has_permission(["view_own_id"])
async def view_my_id(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """View resident's own ID"""
    # Verify user is a resident
    if current_user.role != "resident":
        raise HTTPException(
            status_code=403,
            detail="Only residents can view their IDs"
        )

    # Get biometric data for photo URL
    result = await db.execute(
        select(BiometricData)
        .where(BiometricData.user_id == current_user.id)
    )
    biometric = result.scalar_one_or_none()
    
    if not biometric:
        raise HTTPException(
            status_code=404,
            detail="Biometric data not found"
        )

    # Construct response with all necessary data
    return ResidentIDResponse(
        main_id=current_user.main_id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        date_of_birth=current_user.date_of_birth,
        nationality=current_user.nationality,
        current_address=current_user.current_address,
        phone_number=current_user.phone_number,
        email=current_user.email,
        status=current_user.status,
        institutional_ids=current_user.institutional_ids,
        photo_url=f"/static/{biometric.photo_reference}",
        created_at=current_user.created_at,
        last_updated=current_user.updated_at
    )

@router.post("/update-requests", response_model=UpdateRequestResponse)
async def request_update(
    request: UpdateRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Request an update to ID information"""
    # Verify user is a resident
    if current_user.role != "resident":
        raise HTTPException(
            status_code=403,
            detail="Only residents can request updates"
        )

    # Verify user is active
    if current_user.status != "active":
        raise HTTPException(
            status_code=403,
            detail="Cannot request updates while ID is suspended"
        )

    # Check for pending requests
    result = await db.execute(
        select(UpdateRequest)
        .where(
            UpdateRequest.user_id == current_user.id,
            UpdateRequest.status == "pending"
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="You already have a pending update request"
        )

    # Create update request
    update_request = UpdateRequest(
        user_id=current_user.id,
        requested_changes=request.fields_to_update,
        reason=request.reason,
        status="pending",
        created_at=datetime.utcnow()
    )
    
    db.add(update_request)
    await db.commit()
    await db.refresh(update_request)
    
    return update_request

@router.get("/update-requests", response_model=List[UpdateRequestResponse])
async def list_update_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all update requests for the current resident"""
    if current_user.role != "resident":
        raise HTTPException(
            status_code=403,
            detail="Only residents can view their update requests"
        )

    result = await db.execute(
        select(UpdateRequest)
        .where(UpdateRequest.user_id == current_user.id)
        .order_by(UpdateRequest.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    return result.scalars().all()

@router.get("/update-requests/{request_id}", response_model=UpdateRequestResponse)
async def get_update_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific update request"""
    update_request = await db.get(UpdateRequest, request_id)
    
    if not update_request:
        raise HTTPException(
            status_code=404,
            detail="Update request not found"
        )
        
    if update_request.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Cannot view update requests of other users"
        )
        
    return update_request

@router.delete("/update-requests/{request_id}")
async def cancel_update_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a pending update request"""
    update_request = await db.get(UpdateRequest, request_id)
    
    if not update_request:
        raise HTTPException(
            status_code=404,
            detail="Update request not found"
        )
        
    if update_request.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Cannot cancel update requests of other users"
        )
        
    if update_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Can only cancel pending update requests"
        )
        
    await db.delete(update_request)
    await db.commit()
    
    return {"message": "Update request cancelled successfully"} 