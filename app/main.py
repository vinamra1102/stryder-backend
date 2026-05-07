import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from app.auth import oauth
from app.fitness import get_today_steps
from app.config import REDIRECT_URI

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "change-me-in-production"))

@app.get("/")
def root():
    return {"message": "Stryder backend running"}

@app.get("/login")
async def login(request: Request):
    return await oauth.google.authorize_redirect(request, REDIRECT_URI)

@app.get("/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    request.session["access_token"] = token["access_token"]
    return {"message": "Authenticated successfully"}

@app.get("/steps")
def steps(request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    return get_today_steps(access_token)