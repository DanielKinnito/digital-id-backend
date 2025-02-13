from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.models import DigitalID, IDHistory
from app.core.schemas.digital_id import (
    DigitalIDCreate, DigitalIDResponse, DigitalIDUpdate,
    DigitalIDStatusUpdate, IDHistoryEntry
)
from app.core.auth import get_current_user, has_permission
from app.core.auth.permissions import Permissions
from typing import List, Optional
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=DigitalIDResponse)
@has_permission([Permissions.CREATE_ID])
async def create_digital_id(
    digital_id: DigitalIDCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new digital ID"""
    new_id = DigitalID(
        **digital_id.dict(),
        issuer_id=current_user.id
    )
    
    db.add(new_id)
    await db.commit()
    await db.refresh(new_id)
    return new_id

@router.get("/{id}", response_model=DigitalIDResponse)
@has_permission([Permissions.READ_ID])
async def get_digital_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a digital ID by ID"""
    result = await db.execute(select(DigitalID).filter(DigitalID.id == id))
    digital_id = result.scalar_one_or_none()
    
    if not digital_id:
        raise HTTPException(status_code=404, detail="Digital ID not found")
    
    return digital_id

@router.get("/", response_model=List[DigitalIDResponse])
@has_permission([Permissions.READ_ID])
async def list_digital_ids(
    skip: int = 0,
    limit: int = 100,
    institution_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List digital IDs"""
    query = select(DigitalID).offset(skip).limit(limit)
    
    if institution_id:
        query = query.filter(DigitalID.institution_id == institution_id)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.patch("/{id}", response_model=DigitalIDResponse)
@has_permission([Permissions.UPDATE_ID])
async def update_digital_id(
    id: int,
    update_data: DigitalIDUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a digital ID"""
    result = await db.execute(select(DigitalID).filter(DigitalID.id == id))
    digital_id = result.scalar_one_or_none()
    
    if not digital_id:
        raise HTTPException(status_code=404, detail="Digital ID not found")
    
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(digital_id, field, value)
    
    await db.commit()
    await db.refresh(digital_id)
    return digital_id

@router.post("/{id}/status", response_model=DigitalIDResponse)
@has_permission([Permissions.UPDATE_ID])
async def update_id_status(
    id: int,
    status_update: DigitalIDStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update digital ID status"""
    result = await db.execute(select(DigitalID).filter(DigitalID.id == id))
    digital_id = result.scalar_one_or_none()
    
    if not digital_id:
        raise HTTPException(status_code=404, detail="Digital ID not found")
    
    # Create history entry
    history_entry = IDHistory(
        digital_id_id=digital_id.id,
        old_status=digital_id.status,
        new_status=status_update.status,
        changed_by=current_user.id,
        reason=status_update.reason
    )
    
    digital_id.status = status_update.status
    db.add(history_entry)
    await db.commit()
    await db.refresh(digital_id)
    return digital_id

@router.get("/{id}/history", response_model=List[IDHistoryEntry])
@has_permission([Permissions.READ_ID])
async def get_id_history(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get status history for a digital ID"""
    result = await db.execute(
        select(IDHistory)
        .filter(IDHistory.digital_id_id == id)
        .order_by(IDHistory.changed_at.desc())
    )
    return result.scalars().all() 