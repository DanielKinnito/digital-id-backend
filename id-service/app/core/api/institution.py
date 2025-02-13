from fastapi import APIRouter, Depends, HTTPException, Security, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.auth import get_current_user, require_institution
from app.core.schemas.institutional_id import (
    InstitutionalIDCreate,
    InstitutionalIDResponse,
    LimitedUserResponse
)
from app.core.models import Institution, InstitutionalID, User
from typing import List
from datetime import datetime
import httpx
from shared.config import settings

router = APIRouter()

@router.post("/institutional-ids", response_model=InstitutionalIDResponse)
async def issue_institutional_id(
    institutional_id: InstitutionalIDCreate,
    current_user: User = Security(get_current_user, scopes=["institution"]),
    db: AsyncSession = Depends(get_db)
):
    """Issue a new institutional ID"""
    # Verify institution is active
    institution = await db.get(Institution, current_user.institution_id)
    if not institution or not institution.is_active:
        raise HTTPException(
            status_code=403,
            detail="Institution is not active"
        )

    # Verify user exists and is active
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.USER_SERVICE_URL}/users/by-main-id/{institutional_id.main_id}",
            headers={"Authorization": f"Bearer {current_user.access_token}"}
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=404,
                detail="User not found or inactive"
            )
        user_data = response.json()

    # Check for existing active ID of same type
    result = await db.execute(
        select(InstitutionalID).where(
            InstitutionalID.main_id == institutional_id.main_id,
            InstitutionalID.institution_id == current_user.institution_id,
            InstitutionalID.id_type == institutional_id.id_type,
            InstitutionalID.status == "active"
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Active {institutional_id.id_type} ID already exists for this user"
        )

    # Create institutional ID
    db_id = InstitutionalID(
        **institutional_id.dict(),
        institution_id=current_user.institution_id,
        status="active",
        created_by=current_user.id
    )
    db.add(db_id)
    await db.commit()
    await db.refresh(db_id)

    # Update user's institutional_ids in user service
    user_update_data = {
        "institutional_ids": {
            **user_data.get("institutional_ids", {}),
            str(current_user.institution_id): {
                "id_type": institutional_id.id_type,
                "id_number": institutional_id.id_number,
                "valid_until": institutional_id.valid_until.isoformat() if institutional_id.valid_until else None
            }
        }
    }

    await client.patch(
        f"{settings.USER_SERVICE_URL}/users/{user_data['id']}/institutional-ids",
        json=user_update_data,
        headers={"Authorization": f"Bearer {current_user.access_token}"}
    )

    return db_id

@router.get("/institutional-ids/{id_number}", response_model=InstitutionalIDResponse)
async def get_institutional_id(
    id_number: str,
    current_user: User = Security(get_current_user, scopes=["institution"]),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific institutional ID"""
    result = await db.execute(
        select(InstitutionalID).where(
            InstitutionalID.id_number == id_number,
            InstitutionalID.institution_id == current_user.institution_id
        )
    )
    id_record = result.scalar_one_or_none()
    
    if not id_record:
        raise HTTPException(
            status_code=404,
            detail="Institutional ID not found"
        )
    
    return id_record

@router.get("/users/{main_id}", response_model=LimitedUserResponse)
async def view_user_details(
    main_id: str,
    current_user: User = Security(get_current_user, scopes=["institution"]),
    db: AsyncSession = Depends(get_db)
):
    """View limited user details"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.USER_SERVICE_URL}/users/by-main-id/{main_id}",
            headers={"Authorization": f"Bearer {current_user.access_token}"}
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        user_data = response.json()

    # Filter institutional IDs to only show this institution's IDs
    filtered_ids = {
        k: v for k, v in user_data.get("institutional_ids", {}).items()
        if k == str(current_user.institution_id)
    }

    return LimitedUserResponse(
        main_id=user_data["main_id"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        institutional_ids=filtered_ids,
        status=user_data["status"]
    )

@router.patch("/institutional-ids/{id_number}/revoke")
async def revoke_institutional_id(
    id_number: str,
    reason: str,
    current_user: User = Security(get_current_user, scopes=["institution"]),
    db: AsyncSession = Depends(get_db)
):
    """Revoke an institutional ID"""
    result = await db.execute(
        select(InstitutionalID).where(
            InstitutionalID.id_number == id_number,
            InstitutionalID.institution_id == current_user.institution_id
        )
    )
    id_record = result.scalar_one_or_none()
    
    if not id_record:
        raise HTTPException(
            status_code=404,
            detail="Institutional ID not found"
        )
    
    if id_record.status != "active":
        raise HTTPException(
            status_code=400,
            detail="ID is not active"
        )

    id_record.status = "revoked"
    id_record.revocation_reason = reason
    id_record.revoked_at = datetime.utcnow()
    id_record.revoked_by = current_user.id
    
    await db.commit()
    
    # Update user's institutional_ids in user service
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.USER_SERVICE_URL}/users/by-main-id/{id_record.main_id}",
            headers={"Authorization": f"Bearer {current_user.access_token}"}
        )
        if response.status_code == 200:
            user_data = response.json()
            institutional_ids = user_data.get("institutional_ids", {})
            if str(current_user.institution_id) in institutional_ids:
                del institutional_ids[str(current_user.institution_id)]
                
            await client.patch(
                f"{settings.USER_SERVICE_URL}/users/{user_data['id']}/institutional-ids",
                json={"institutional_ids": institutional_ids},
                headers={"Authorization": f"Bearer {current_user.access_token}"}
            )
    
    return {"message": "Institutional ID revoked successfully"} 