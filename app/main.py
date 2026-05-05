from fastapi import Request
from app.auth import oauth

@app.get("/login")
async def login(request: Request):
    redirect_uri = "http://localhost:8000/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)