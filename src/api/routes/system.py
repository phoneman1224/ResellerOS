"""
System API routes.
"""
from fastapi import APIRouter, HTTPException
import logging
import os
from datetime import datetime

from src.core.database import check_database_health
from src.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """System health check.

    Returns:
        System health status
    """
    try:
        db_healthy = check_database_health()

        return {
            "success": True,
            "data": {
                "status": "healthy" if db_healthy else "degraded",
                "database": "connected" if db_healthy else "disconnected",
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "success": False,
            "data": {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            },
        }


@router.get("/info")
async def get_system_info():
    """Get system information.

    Returns:
        System information
    """
    try:
        # Get database file size
        db_path = "reselleros.db"
        db_size = 0
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path)

        # Get uploads directory size
        upload_size = 0
        if os.path.exists(settings.upload_dir):
            for root, dirs, files in os.walk(settings.upload_dir):
                upload_size += sum(os.path.getsize(os.path.join(root, f)) for f in files)

        return {
            "success": True,
            "data": {
                "app_name": settings.app_name,
                "version": "1.0.0",
                "environment": settings.app_env,
                "database_size_mb": round(db_size / 1024 / 1024, 2),
                "uploads_size_mb": round(upload_size / 1024 / 1024, 2),
                "ebay_configured": settings.ebay_configured,
                "ollama_url": settings.ollama_base_url,
            },
        }
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system information")


@router.get("/settings")
async def get_settings():
    """Get application settings.

    Returns:
        Application settings (non-sensitive)
    """
    try:
        return {
            "success": True,
            "data": {
                "app_name": settings.app_name,
                "environment": settings.app_env,
                "ebay_configured": settings.ebay_configured,
                "ebay_environment": settings.ebay_environment if settings.ebay_configured else None,
                "ollama_url": settings.ollama_base_url,
                "ollama_model": settings.ollama_model,
                "backup_enabled": settings.backup_enabled,
                "backup_interval_hours": settings.backup_interval_hours,
            },
        }
    except Exception as e:
        logger.error(f"Failed to get settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get settings")


@router.get("/logs")
async def get_logs(lines: int = 100):
    """Get recent log entries.

    Args:
        lines: Number of log lines to return

    Returns:
        Recent log entries
    """
    try:
        log_file = settings.log_file

        if not os.path.exists(log_file):
            return {
                "success": True,
                "data": {
                    "logs": [],
                    "message": "No log file found",
                },
            }

        # Read last N lines
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

        return {
            "success": True,
            "data": {
                "logs": [line.strip() for line in recent_lines],
                "total_lines": len(recent_lines),
            },
        }
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get logs")
