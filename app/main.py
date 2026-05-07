import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.routers import auth as auth_router
from app.routers import fitness as fitness_router

app = FastAPI(
    title="Stryder API",
    description="Backend API for the Stryder step tracking app",
    version="1.0.0",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "change-me-in-production"),
)

app.include_router(auth_router.router)
app.include_router(fitness_router.router)


@app.get("/", tags=["Health"])
def root():
    return {"success": True, "message": "Stryder API is running", "version": "1.0.0"}
