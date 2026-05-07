from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.config import SECRET_KEY, CORS_ORIGINS
from app.routers import auth as auth_router
from app.routers import fitness as fitness_router

app = FastAPI(
    title="Stryder API",
    description="Backend API for the Stryder step tracking app",
    version="1.0.0",
)

# CORS must be registered before other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
)

app.include_router(auth_router.router)
app.include_router(fitness_router.router)


@app.get("/", tags=["Health"])
def root():
    return {"success": True, "message": "Stryder API is running", "version": "1.0.0"}
