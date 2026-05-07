from fastapi import APIRouter
from app.config import ENVIRONMENT

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    return {"status": "ok", "environment": ENVIRONMENT}
