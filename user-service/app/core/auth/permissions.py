from fastapi import Depends, HTTPException, status
from typing import List, Optional
from functools import wraps
from .jwt import get_current_user
from app.core.models import User, RoleType

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
    RoleType.SUPER_ADMIN: [
        Permissions.CREATE_USER, Permissions.READ_USER,
        Permissions.UPDATE_USER, Permissions.DELETE_USER,
        Permissions.CREATE_ID, Permissions.READ_ID,
        Permissions.UPDATE_ID, Permissions.REVOKE_ID,
        Permissions.MANAGE_INSTITUTION, Permissions.MANAGE_ROLES,
        Permissions.AUDIT_LOG
    ],
    RoleType.INSTITUTIONAL_ADMIN: [
        Permissions.CREATE_USER, Permissions.READ_USER,
        Permissions.UPDATE_USER, Permissions.CREATE_ID,
        Permissions.READ_ID, Permissions.UPDATE_ID
    ],
    RoleType.RESIDENT: [
        Permissions.READ_USER, Permissions.READ_ID
    ],
    RoleType.STAFF: [
        Permissions.READ_USER, Permissions.READ_ID,
        Permissions.CREATE_ID
    ]
}

def has_permission(required_permissions: List[str]):
    """Decorator to check if user has required permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            user_permissions = current_user.permissions
            
            # Super admin has all permissions
            if any(role.name == RoleType.SUPER_ADMIN for role in current_user.roles):
                return await func(*args, current_user=current_user, **kwargs)
            
            # Check if user has all required permissions
            if not all(perm in user_permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def has_role(required_roles: List[RoleType]):
    """Decorator to check if user has required roles"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            user_roles = {role.name for role in current_user.roles}
            
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required role(s): {', '.join(required_roles)}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

async def validate_permissions(user: User, required_permissions: List[str]) -> bool:
    """Validate if user has required permissions"""
    user_permissions = user.permissions
    return all(perm in user_permissions for perm in required_permissions)

async def check_permissions(user: User, required_permissions: List[str]) -> bool:
    """Check if user has required permissions"""
    # Super admin has all permissions
    if any(role.name == RoleType.SUPER_ADMIN for role in user.roles):
        return True
        
    user_permissions = user.permissions
    return all(perm in user_permissions for perm in required_permissions) 