from fastapi import APIRouter, Depends, HTTPException, Security, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.auth import get_current_user, require_super_admin
from app.core.auth.jwt import get_password_hash
from app.core.schemas.admin import (
    InstitutionalAdminCreate,
    AdminResponse,
    ReportResponse,
    InstitutionResponse
)
from app.core.models import User, UserRole, Institution, Report, Role
from typing import List
from datetime import date, datetime
import httpx

router = APIRouter()

@router.post("/institutional-admins", response_model=AdminResponse)
async def create_institutional_admin(
    admin: InstitutionalAdminCreate,
    current_user: User = Security(get_current_user, scopes=["super_admin"]),
    db: AsyncSession = Depends(get_db)
):
    """Create a new institutional admin (Super Admin only)"""
    # Verify institution exists
    institution = await db.get(Institution, admin.institution_id)
    if not institution:
        raise HTTPException(
            status_code=404,
            detail="Institution not found"
        )

    # Check if username or email already exists
    result = await db.execute(
        select(User).where(
            (User.username == admin.username) | (User.email == admin.email)
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )

    # Create new institutional admin
    db_admin = User(
        username=admin.username,
        email=admin.email,
        hashed_password=get_password_hash(admin.password),
        institution_id=admin.institution_id
    )
    
    # Add institutional admin role
    result = await db.execute(
        select(Role).where(Role.name == UserRole.INSTITUTIONAL_ADMIN)
    )
    admin_role = result.scalar_one_or_none()
    if admin_role:
        db_admin.roles.append(admin_role)
    
    db.add(db_admin)
    await db.commit()
    await db.refresh(db_admin)
    
    return db_admin

@router.get("/institutions", response_model=List[InstitutionResponse])
async def list_institutions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Security(get_current_user, scopes=["super_admin"]),
    db: AsyncSession = Depends(get_db)
):
    """List all institutions"""
    result = await db.execute(
        select(Institution)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.get("/reports", response_model=List[ReportResponse])
async def generate_reports(
    report_type: str,
    start_date: date,
    end_date: date,
    current_user: User = Security(get_current_user, scopes=["super_admin"]),
    db: AsyncSession = Depends(get_db)
):
    """Generate system reports"""
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before end date"
        )

    report_data = {}
    
    # Gather data based on report type
    if report_type == "user_registrations":
        result = await db.execute(
            select(User)
            .join(Role, User.roles)
            .where(
                User.created_at.between(start_date, end_date),
                Role.name == UserRole.RESIDENT
            )
        )
        users = result.scalars().all()
        report_data = {
            "total_registrations": len(users),
            "by_institution": {}
        }
        
        for user in users:
            inst_id = str(user.institution_id)
            report_data["by_institution"][inst_id] = report_data["by_institution"].get(inst_id, 0) + 1
    
    elif report_type == "institutional_activity":
        result = await db.execute(
            select(Institution)
            .where(Institution.is_active == True)
        )
        institutions = result.scalars().all()
        
        report_data = {
            "total_institutions": len(institutions),
            "active_admins": 0,
            "total_ids_issued": 0
        }
        
        # Get admin counts
        admin_result = await db.execute(
            select(User)
            .join(Role, User.roles)
            .where(
                Role.name == UserRole.INSTITUTIONAL_ADMIN,
                User.is_active == True
            )
        )
        report_data["active_admins"] = len(admin_result.scalars().all())

    # Create report record
    report = Report(
        report_type=report_type,
        data=report_data,
        generated_by=current_user.id
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    return report

@router.post("/suspend-institution/{institution_id}")
async def suspend_institution(
    institution_id: int,
    reason: str,
    current_user: User = Security(get_current_user, scopes=["super_admin"]),
    db: AsyncSession = Depends(get_db)
):
    """Suspend an institution and its admins"""
    institution = await db.get(Institution, institution_id)
    if not institution:
        raise HTTPException(
            status_code=404,
            detail="Institution not found"
        )

    # Suspend institution
    institution.is_active = False
    
    # Suspend all institutional admins
    result = await db.execute(
        select(User)
        .where(
            User.institution_id == institution_id,
            User.role == UserRole.INSTITUTIONAL_ADMIN
        )
    )
    admins = result.scalars().all()
    
    for admin in admins:
        admin.is_active = False

    await db.commit()
    
    return {"message": "Institution and its admins have been suspended"} 