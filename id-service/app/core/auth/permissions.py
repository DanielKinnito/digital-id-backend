from fastapi import Depends, HTTPException, status
from typing import List, Callable, Dict
from functools import wraps
from enum import Enum
from .jwt import get_current_user

class RoleType(str, Enum):
    SUPER_ADMIN = "super_admin"
    INSTITUTIONAL_ADMIN = "institutional_admin"
    STAFF = "staff"
    RESIDENT = "resident"

class Permissions:
    # ID Management
    CREATE_ID = "create_id"
    READ_ID = "read_id"
    UPDATE_ID = "update_id"
    REVOKE_ID = "revoke_id"
    
    # Institution-specific
    MANAGE_INSTITUTION_IDS = "manage_institution_ids"
    VIEW_INSTITUTION_IDS = "view_institution_ids"
    
    # Batch operations
    BULK_CREATE_IDS = "bulk_create_ids"
    EXPORT_IDS = "export_ids"
    
    # System operations
    VIEW_METRICS = "view_metrics"
    MANAGE_SETTINGS = "manage_settings"

# Define role-based permissions
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    RoleType.SUPER_ADMIN: [
        Permissions.CREATE_ID,
        Permissions.READ_ID,
        Permissions.UPDATE_ID,
        Permissions.REVOKE_ID,
        Permissions.MANAGE_INSTITUTION_IDS,
        Permissions.VIEW_INSTITUTION_IDS,
        Permissions.BULK_CREATE_IDS,
        Permissions.EXPORT_IDS,
        Permissions.VIEW_METRICS,
        Permissions.MANAGE_SETTINGS,
    ],
    RoleType.INSTITUTIONAL_ADMIN: [
        Permissions.CREATE_ID,
        Permissions.READ_ID,
        Permissions.UPDATE_ID,
        Permissions.MANAGE_INSTITUTION_IDS,
        Permissions.VIEW_INSTITUTION_IDS,
        Permissions.EXPORT_IDS,
        Permissions.VIEW_METRICS,
    ],
    RoleType.STAFF: [
        Permissions.CREATE_ID,
        Permissions.READ_ID,
        Permissions.VIEW_INSTITUTION_IDS,
    ],
    RoleType.RESIDENT: [
        Permissions.READ_ID,
    ],
}

def has_permission(required_permissions: List[str]) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
            # Super admin has all permissions
            if RoleType.SUPER_ADMIN in current_user.get("roles", []):
                return await func(*args, current_user=current_user, **kwargs)
            
            # Get user's role-based permissions
            user_permissions = []
            for role in current_user.get("roles", []):
                user_permissions.extend(ROLE_PERMISSIONS.get(role, []))
            
            # Check if user has all required permissions
            if not all(perm in user_permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

async def validate_institution_access(user_id: int, institution_id: int) -> bool:
    """Validate if user has access to the specified institution"""
    # Implementation depends on your institution access logic
    return True

async def require_institution_admin(current_user = Depends(get_current_user)):
    """Check if user is an institutional admin"""
    if RoleType.INSTITUTIONAL_ADMIN not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires institutional admin privileges"
        )
    return current_user

def check_institution_access(func: Callable) -> Callable:
    """Decorator to check institution access for ID operations"""
    @wraps(func)
    async def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
        if RoleType.SUPER_ADMIN in current_user.get("roles", []):
            return await func(*args, current_user=current_user, **kwargs)
            
        if "institution_id" in kwargs:
            has_access = await validate_institution_access(
                current_user.get("id"), 
                kwargs["institution_id"]
            )
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No access to this institution"
                )
        
        return await func(*args, current_user=current_user, **kwargs)
    return wrapper 