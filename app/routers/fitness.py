import re
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from app.dependencies import get_current_user
from app.services.google_fit import (
    get_today_steps,
    get_weekly_steps,
    get_steps_history,
    get_activity_summary,
    get_monthly_steps,
)
from app.schemas.fitness import (
    StepsTodayResponse,
    WeeklyStepsResponse,
    StepsHistoryResponse,
    ActivitySummaryResponse,
    MonthlyStepsResponse,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/fitness", tags=["Fitness"])

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _require_google_token(current_user: dict) -> str:
    token = current_user.get("google_access_token")
    if not token:
        raise HTTPException(
            status_code=403,
            detail={"success": False, "error": "Google access token missing — please re-authenticate"},
        )
    return token


def _validate_dates(from_date: str, to_date: str) -> None:
    for label, value in [("from_date", from_date), ("to_date", to_date)]:
        if not _DATE_RE.match(value):
            raise HTTPException(
                status_code=422,
                detail={"success": False, "error": f"Invalid {label}: '{value}'. Expected YYYY-MM-DD"},
            )
    if from_date > to_date:
        raise HTTPException(
            status_code=422,
            detail={"success": False, "error": "from_date must not be later than to_date"},
        )


@router.get("/steps/today", response_model=StepsTodayResponse)
async def steps_today(current_user: dict = Depends(get_current_user)):
    """Return today's step count for the authenticated user."""
    token = _require_google_token(current_user)
    return await get_today_steps(token)


@router.get("/steps/week", response_model=WeeklyStepsResponse)
async def steps_week(current_user: dict = Depends(get_current_user)):
    """Return step counts for the last 7 calendar days."""
    token = _require_google_token(current_user)
    return await get_weekly_steps(token)


@router.get("/steps/monthly", response_model=MonthlyStepsResponse)
async def steps_monthly(
    year: int = Query(None, description="4-digit year, e.g. 2025"),
    month: int = Query(None, description="Month number 1–12"),
    current_user: dict = Depends(get_current_user),
):
    """Return daily step counts for a given calendar month (defaults to current month)."""
    now = datetime.now(timezone.utc)
    y = year or now.year
    m = month or now.month
    if not (1 <= m <= 12):
        raise HTTPException(
            status_code=422,
            detail={"success": False, "error": "month must be between 1 and 12"},
        )
    token = _require_google_token(current_user)
    return await get_monthly_steps(token, y, m)


@router.get("/summary", response_model=ActivitySummaryResponse)
async def activity_summary(current_user: dict = Depends(get_current_user)):
    """Return a dashboard-ready activity summary (today + weekly stats + streak)."""
    token = _require_google_token(current_user)
    return await get_activity_summary(token)


@router.get("/steps/history", response_model=StepsHistoryResponse)
async def steps_history(
    from_date: str = Query(..., description="Start date (YYYY-MM-DD)", example="2025-04-01"),
    to_date: str = Query(..., description="End date (YYYY-MM-DD)", example="2025-04-30"),
    limit: int = Query(90, ge=1, le=365, description="Max days to return (1–365)"),
    current_user: dict = Depends(get_current_user),
):
    """Return step counts for a custom date range (max 365 days)."""
    _validate_dates(from_date, to_date)
    token = _require_google_token(current_user)
    result = await get_steps_history(token, from_date, to_date)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)
    # Apply limit after fetching (Google Fit is the expensive call, not slicing)
    result["days"] = result["days"][:limit]
    return result
