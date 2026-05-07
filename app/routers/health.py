from fastapi import APIRouter
from app.config import ENVIRONMENT, APP_VERSION

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    return {"success": True, "status": "ok", "environment": ENVIRONMENT, "version": APP_VERSION}
