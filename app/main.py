"""
FastAPI application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pathlib import Path
import time
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import get_settings
from app.database import engine
from app.models.base import Base
from app.routers import auth, articles, appointments, chat, faqs, upload, translation, documents, subscriptions
from app.tasks import scheduler  # T069: Background task scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Initialize rate limiter
# Swallow errors to prevent rate limiting from blocking OPTIONS requests
limiter = Limiter(key_func=get_remote_address, swallow_errors=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    Handles startup and shutdown logic.
    """
    # Startup
    print("🚀 Starting News Platform API...")
    print(f"📝 Environment: {settings.ENVIRONMENT}")
    print(f"🔗 Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'configured'}")

    # Note: In production, use Alembic migrations instead of create_all
    # Uncomment the following line only for development/testing:
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    # T069: Start background task scheduler
    await scheduler.start()

    yield

    # Shutdown
    print("🛑 Shutting down News Platform API...")

    # T069: Stop background task scheduler
    await scheduler.stop()

    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title="News Platform API",
    description="Backend API for S&L News Platform with AI-powered features",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    redirect_slashes=False  # Disable trailing slash redirects to avoid CORS issues
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for Pydantic validation errors.
    Returns detailed error information for debugging.
    """
    errors = exc.errors()
    logger.error(f"Validation error for {request.method} {request.url.path}: {errors}")

    # Format errors for better readability
    formatted_errors = []
    for error in errors:
        formatted_errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        })

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": formatted_errors
        }
    )

# Configure CORS - MUST be added BEFORE other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
    max_age=3600,
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Add security headers to all responses.
    """
    response = await call_next(request)

    # Special CSP for API docs to allow Swagger UI to work
    if request.url.path.startswith("/api/docs") or request.url.path.startswith("/api/redoc") or request.url.path.startswith("/api/openapi.json"):
        # Relaxed CSP for Swagger UI - allow CDN resources
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https://cdn.jsdelivr.net; "
            "connect-src 'self';"
        )
    else:
        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS protection in older browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Enforce HTTPS in production (when deployed with HTTPS)
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy (CSP)
        # Note: Adjust this based on your frontend requirements
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://accounts.google.com; "
            "frame-ancestors 'none';"
        )

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (formerly Feature Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )

    return response


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests and their response times.
    """
    # Skip logging for OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        response = await call_next(request)
        return response

    start_time = time.time()

    # Log request
    logger.info(f"📥 {request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}")

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log response
    logger.info(
        f"📤 {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )

    # Add custom header with processing time
    response.headers["X-Process-Time"] = str(process_time)

    return response

# Register routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(articles.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(faqs.router, prefix="/api/v1")
app.include_router(translation.router, prefix="/api/v1")
app.include_router(documents.router)
app.include_router(subscriptions.router, prefix="/api/v1")
app.include_router(upload.router)

# Mount static files for uploaded images
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        Status message indicating the API is running
    """
    return {
        "status": "healthy",
        "service": "News Platform API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.

    Returns:
        Welcome message and API documentation links
    """
    return {
        "message": "Welcome to News Platform API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "health": "/health"
    }

