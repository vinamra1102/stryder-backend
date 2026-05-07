import re
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from app.dependencies import get_current_user
from app.services.google_fit import get_today_steps, get_weekly_steps, get_steps_history, get_activity_summary
from app.schemas.fitness import StepsTodayResponse, WeeklyStepsResponse, StepsHistoryResponse, ActivitySummaryResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/fitness", tags=["Fitness"])


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _get_google_token(current_user: dict) -> str | None:
    return current_user.get("google_access_token")


def _validate_dates(from_date: str, to_date: str) -> None:
    for label, value in [("from_date", from_date), ("to_date", to_date)]:
        if not _DATE_RE.match(value):
            raise HTTPException(
                status_code=422,
                detail=f"Invalid {label}: '{value}'. Expected format YYYY-MM-DD",
            )
    if from_date > to_date:
        raise HTTPException(
            status_code=422,
            detail="from_date must not be later than to_date",
        )


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


@router.get("/summary", response_model=ActivitySummaryResponse)
def activity_summary(current_user: dict = Depends(get_current_user)):
    """Return a dashboard-ready activity summary (today + weekly stats + streak)."""
    token = _get_google_token(current_user)
    if not token:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "Google access token missing from session"},
        )
    return get_activity_summary(token)


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
    _validate_dates(from_date, to_date)
    result = get_steps_history(token, from_date, to_date)
    if not result.get("success"):
        return JSONResponse(status_code=400, content=result)
    return result
