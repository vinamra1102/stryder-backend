from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.config import DAILY_STEP_GOAL
from app.schemas.user import UserSettings, UserSettingsResponse

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/settings", response_model=UserSettingsResponse)
def get_settings(current_user: dict = Depends(get_current_user)):
    """
    Return the user's app settings.
    Defaults are returned until a database layer is added for persistence.
    """
    return {
        "success": True,
        "settings": UserSettings(daily_step_goal=DAILY_STEP_GOAL),
    }


@router.put("/settings", response_model=UserSettingsResponse)
def update_settings(
    body: UserSettings,
    current_user: dict = Depends(get_current_user),
):
    """
    Update user settings. Validated and acknowledged but not persisted
    until a database layer is introduced.
    """
    return {"success": True, "settings": body}
