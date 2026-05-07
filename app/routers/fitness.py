from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.services.google_fit import get_today_steps

router = APIRouter(prefix="/fitness", tags=["Fitness"])


@router.get("/steps/today")
def steps_today(request: Request):
    """Return today's step count from Google Fit."""
    access_token = request.session.get("access_token")
    if not access_token:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "Not authenticated"},
        )
    return get_today_steps(access_token)
