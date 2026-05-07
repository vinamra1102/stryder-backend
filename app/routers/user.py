from fastapi import APIRouter, Depends
from app.dependencies import get_current_user

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return {
        "success": True,
        "profile": {
            "sub": current_user.get("sub"),
            "email": current_user.get("email"),
            "name": current_user.get("name"),
            "picture": current_user.get("picture"),
        },
    }
