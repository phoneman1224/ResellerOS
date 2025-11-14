"""
FastAPI application setup.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from src.config.settings import settings
from src.config.logging_config import setup_logging
from src.core.database import init_database
from src.core.exceptions import ResellerOSException

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="ResellerOS API",
        description="API for Reseller OS - eBay reseller management platform",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # CORS middleware - allow localhost only
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:*", "http://127.0.0.1:*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    # Global exception handler
    @app.exception_handler(ResellerOSException)
    async def reselleros_exception_handler(request: Request, exc: ResellerOSException):
        logger.error(f"ResellerOS exception: {exc.message}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error",
                "message": str(exc) if settings.is_development else "An error occurred",
            },
        )

    # Include routers
    from src.api.routes import inventory, assistant, ebay, system

    app.include_router(inventory.router, prefix="/api/inventory", tags=["Inventory"])
    app.include_router(assistant.router, prefix="/api/assistant", tags=["AI Assistant"])
    app.include_router(ebay.router, prefix="/api/ebay", tags=["eBay Integration"])
    app.include_router(system.router, prefix="/api/system", tags=["System"])

    @app.on_event("startup")
    async def startup_event():
        """Initialize application on startup."""
        logger.info("Starting ResellerOS API...")
        try:
            # Initialize database
            init_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.critical(f"Failed to initialize database: {e}")
            raise

        logger.info(f"ResellerOS API started on {settings.api_host}:{settings.api_port}")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown."""
        logger.info("Shutting down ResellerOS API...")

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "ResellerOS API",
            "version": "1.0.0",
            "status": "running",
            "docs": "/api/docs",
        }

    @app.get("/api/health")
    async def health_check():
        """Health check endpoint."""
        from src.core.database import check_database_health

        db_healthy = check_database_health()

        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "database": "connected" if db_healthy else "disconnected",
            "version": "1.0.0",
        }

    return app


# Create application instance
app = create_app()
