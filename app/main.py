from fastapi import Request
from app.auth import oauth

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Stryder backend running"}

@app.get("/login")
async def login(request: Request):
    redirect_uri = "http://localhost:8000/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    return token