from fastapi import Depends, HTTPException, status
from .jwt import get_current_user

async def require_institution(current_user = Depends(get_current_user)):
    if "institution_admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user 