from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine, init_db
from app.core.logger import logger
from app.services.ocr_service import ocr_service

# Import API routers
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.scans import router as scans_router
from app.api.protection import router as protection_router
from app.api.dashboard import router as dashboard_router
from app.api.audit import router as audit_router
from app.api.gateway import router as gateway_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-Grade AI Privacy Firewall for Indian Personal Data with context-aware hybrid detection, verified redaction, and compliance auditing.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware - Restricts allowed origins strictly to authorized environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """
    Applies production security headers to all responses.
    CSP permits necessary resources for Google Identity Services while strictly enforcing origin hygiene.
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # CSP: Allow Google GIS iframe and auth scripts while locking down other origins
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://accounts.google.com; "
        "frame-src https://accounts.google.com; "
        "connect-src 'self' https://accounts.google.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:;"
    )
    
    if settings.ENV == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response

@app.on_event("startup")
def on_startup():
    logger.info("Initializing PRIVASCOPE database schema...")
    init_db()
    logger.info(f"Database connected. OCR Service Status: {ocr_service.status}")

@app.get("/health", tags=["System"])
def health_check():
    """System health check endpoint verifying database connectivity and OCR subsystem availability."""
    db_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ok" if db_status == "connected" else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": db_status,
        "ocr_status": ocr_service.status,
        "environment": settings.ENV
    }

# Register production API endpoints under /api
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(documents_router, prefix=settings.API_V1_PREFIX)
app.include_router(scans_router, prefix=settings.API_V1_PREFIX)
app.include_router(protection_router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)
app.include_router(audit_router, prefix=settings.API_V1_PREFIX)
app.include_router(gateway_router, prefix=settings.API_V1_PREFIX)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred while processing the privacy request."}
    )
