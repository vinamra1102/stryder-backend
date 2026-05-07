from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from app.dependencies import get_current_user
from app.services.google_fit import get_today_steps, get_weekly_steps, get_steps_history
from app.schemas.fitness import StepsTodayResponse, WeeklyStepsResponse, StepsHistoryResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/fitness", tags=["Fitness"])


def _get_google_token(current_user: dict) -> str | None:
    return current_user.get("google_access_token")


@router.get("/steps/today", response_model=StepsTodayResponse)
def steps_today(current_user: dict = Depends(get_current_user)):
    """Return today's step count for the authenticated user."""
    token = _get_google_token(current_user)
    if not token:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "Google access token missing from session"},
        )
    return get_today_steps(token)


@router.get("/steps/week", response_model=WeeklyStepsResponse)
def steps_week(current_user: dict = Depends(get_current_user)):
    """Return step counts for the last 7 days."""
    token = _get_google_token(current_user)
    if not token:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "Google access token missing from session"},
        )
    return get_weekly_steps(token)


@router.get("/steps/history", response_model=StepsHistoryResponse)
def steps_history(
    from_date: str = Query(..., description="Start date (YYYY-MM-DD)", example="2025-04-01"),
    to_date: str = Query(..., description="End date (YYYY-MM-DD)", example="2025-04-30"),
    current_user: dict = Depends(get_current_user),
):
    """Return step counts for a custom date range."""
    token = _get_google_token(current_user)
    if not token:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "Google access token missing from session"},
        )
    result = get_steps_history(token, from_date, to_date)
    if not result.get("success"):
        return JSONResponse(status_code=400, content=result)
    return result
