from fastapi import Depends, HTTPException, status
from typing import List, Callable
from functools import wraps
from app.core.models import User, UserRole
from .jwt import get_current_user

class Permissions:
    # User Management
    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    
    # ID Management
    CREATE_ID = "create_id"
    READ_ID = "read_id"
    UPDATE_ID = "update_id"
    REVOKE_ID = "revoke_id"
    
    # Institution Management
    MANAGE_INSTITUTION = "manage_institution"
    
    # System Management
    MANAGE_ROLES = "manage_roles"
    AUDIT_LOG = "audit_log"

# Role-Permission mapping
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: [
        Permissions.CREATE_USER, Permissions.READ_USER,
        Permissions.UPDATE_USER, Permissions.DELETE_USER,
        Permissions.CREATE_ID, Permissions.READ_ID,
        Permissions.UPDATE_ID, Permissions.REVOKE_ID,
        Permissions.MANAGE_INSTITUTION, Permissions.MANAGE_ROLES,
        Permissions.AUDIT_LOG
    ],
    UserRole.INSTITUTIONAL_ADMIN: [
        Permissions.CREATE_USER, Permissions.READ_USER,
        Permissions.UPDATE_USER, Permissions.CREATE_ID,
        Permissions.READ_ID, Permissions.UPDATE_ID
    ],
    UserRole.STAFF: [
        Permissions.READ_USER, Permissions.READ_ID,
        Permissions.CREATE_ID
    ],
    UserRole.RESIDENT: [
        Permissions.READ_USER, Permissions.READ_ID
    ]
}

def has_permission(required_permissions: List[str]):
    """Decorator to check if user has required permissions"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            user_permissions = current_user.permissions
            if not all(perm in user_permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

async def check_institution_access(user: User, institution_id: int) -> bool:
    """Check if user has access to institution"""
    if any(role.name == UserRole.SUPER_ADMIN for role in user.roles):
        return True
    return user.institution_id == institution_id

def require_institution_admin(func: Callable):
    """Decorator to require institutional admin role and check institution access"""
    @wraps(func)
    async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
        if not any(role.name == UserRole.INSTITUTIONAL_ADMIN for role in current_user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Institutional admin role required"
            )
        
        if "institution_id" in kwargs:
            has_access = await check_institution_access(
                current_user,
                kwargs["institution_id"]
            )
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No access to this institution"
                )
        
        return await func(*args, current_user=current_user, **kwargs)
    return wrapper 