from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from app.oauth_client import oauth
from app.config import REDIRECT_URI, FRONTEND_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from app.services.token_service import create_access_token
from app.dependencies import get_current_user
from app.utils.logger import get_logger
import httpx

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/login")
async def login(request: Request):
    """Redirect the user to Google OAuth consent screen."""
    return await oauth.google.authorize_redirect(request, REDIRECT_URI)


@router.get("/callback")
async def auth_callback(request: Request):
    """
    Handle Google OAuth callback.
    Exchanges the auth code for tokens, extracts the user profile,
    and issues a Stryder JWT for subsequent API requests.
    """
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        logger.error(f"OAuth token exchange failed: {e}")
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "OAuth authentication failed"},
        )

    user_info = token.get("userinfo") or {}

    # Fallback: fetch userinfo from Google if not embedded in token
    if not user_info.get("sub"):
        try:
            resp = await oauth.google.userinfo(token=token)
            user_info = dict(resp)
        except Exception as e:
            logger.warning(f"Failed to fetch userinfo: {e}")

    sub = user_info.get("sub") or user_info.get("id", "")
    if not sub:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Could not retrieve user identity"},
        )

    jwt_payload = {
        "sub": sub,
        "email": user_info.get("email", ""),
        "name": user_info.get("name", ""),
        "picture": user_info.get("picture", ""),
        "google_access_token": token.get("access_token", ""),
        "google_refresh_token": token.get("refresh_token", ""),
    }

    access_token = create_access_token(jwt_payload)
    logger.info(f"User authenticated: {jwt_payload['email']}")

    # Redirect to the frontend with the token in the query string.
    # The frontend reads ?token= on its /auth/callback route and stores it.
    redirect_url = f"{FRONTEND_URL}/auth/callback?token={access_token}"
    return RedirectResponse(url=redirect_url)


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Return the authenticated user's profile from their JWT claims."""
    return {
        "success": True,
        "user": {
            "sub": current_user.get("sub"),
            "email": current_user.get("email"),
            "name": current_user.get("name"),
            "picture": current_user.get("picture"),
        },
    }


@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    Refresh the Stryder JWT and attempt to renew the embedded Google access token.
    Uses the stored Google refresh token so the user stays logged in past the 1-hour
    Google access token expiry without needing to re-authenticate.
    """
    google_access_token = current_user.get("google_access_token", "")
    google_refresh_token = current_user.get("google_refresh_token", "")

    # Attempt to exchange Google refresh token for a fresh access token
    if google_refresh_token:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": GOOGLE_CLIENT_ID,
                        "client_secret": GOOGLE_CLIENT_SECRET,
                        "refresh_token": google_refresh_token,
                        "grant_type": "refresh_token",
                    },
                )
            if resp.status_code == 200:
                google_access_token = resp.json().get("access_token", google_access_token)
                logger.info(f"Google access token refreshed for: {current_user.get('email')}")
            else:
                logger.warning(f"Google token refresh failed ({resp.status_code}) for: {current_user.get('email')}")
        except Exception as e:
            logger.error(f"Error refreshing Google token: {e}")

    new_token = create_access_token({
        "sub": current_user.get("sub"),
        "email": current_user.get("email"),
        "name": current_user.get("name"),
        "picture": current_user.get("picture"),
        "google_access_token": google_access_token,
        "google_refresh_token": google_refresh_token,
    })
    logger.info(f"JWT refreshed for user: {current_user.get('email')}")
    return {
        "success": True,
        "access_token": new_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout():
    """
    Logout endpoint — instructs the client to discard the token.
    JWTs are stateless so server-side invalidation requires a denylist
    (deferred to a future improvement).
    """
    return {"success": True, "message": "Logged out successfully"}
