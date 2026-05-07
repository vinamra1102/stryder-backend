from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.oauth_client import oauth
from app.config import REDIRECT_URI

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/login")
async def login(request: Request):
    """Initiate Google OAuth flow."""
    return await oauth.google.authorize_redirect(request, REDIRECT_URI)


@router.get("/callback")
async def auth_callback(request: Request):
    """Handle Google OAuth callback and persist access token in session."""
    token = await oauth.google.authorize_access_token(request)
    request.session["access_token"] = token["access_token"]
    return JSONResponse({"success": True, "message": "Authenticated successfully"})
