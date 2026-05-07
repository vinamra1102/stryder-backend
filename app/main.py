import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from app.config import SECRET_KEY, CORS_ORIGINS, ENVIRONMENT, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, JWT_SECRET_KEY
from app.utils.logger import get_logger
from app.utils.request_logger import RequestLoggingMiddleware
from app.routers import auth as auth_router
from app.routers import fitness as fitness_router
from app.routers import health as health_router
from app.routers import user as user_router

logger = get_logger(__name__)

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

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
)

app.include_router(health_router.router)
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(fitness_router.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}:\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "An unexpected error occurred"},
    )


@app.on_event("startup")
async def startup():
    _required = {
        "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
        "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
        "SECRET_KEY": SECRET_KEY,
        "JWT_SECRET_KEY": JWT_SECRET_KEY,
    }
    missing = [k for k, v in _required.items() if not v or "change-me" in v]
    if missing:
        logger.warning(f"Missing or placeholder env vars: {', '.join(missing)}")
    logger.info(f"Stryder API starting — environment: {ENVIRONMENT}")


@app.get("/", tags=["Health"])
def root():
    return {"success": True, "message": "Stryder API is running", "version": "1.0.0"}
