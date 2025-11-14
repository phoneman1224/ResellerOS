"""
ResellerOS main application entry point.
"""
import sys
import os
import logging
import time
from threading import Thread
from pathlib import Path

# Setup logging first
from src.config.logging_config import setup_logging
setup_logging()

logger = logging.getLogger(__name__)

def run_backend():
    """Run FastAPI backend server in background thread."""
    try:
        import uvicorn
        from src.api.app import app

        logger.info("Starting FastAPI backend server...")
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="error",  # Reduce noise in logs
            access_log=False,
        )
    except Exception as e:
        logger.critical(f"Backend server failed to start: {e}")
        raise


def ensure_directories():
    """Ensure required directories exist."""
    directories = [
        "uploads",
        "backups",
        "logs",
    ]

    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")


def initialize_database():
    """Initialize database if needed."""
    try:
        from src.core.database import init_database, check_database_health

        logger.info("Initializing database...")
        init_database()

        # Check database health
        if check_database_health():
            logger.info("Database initialized and healthy")
        else:
            logger.warning("Database health check failed")

    except Exception as e:
        logger.critical(f"Database initialization failed: {e}")
        raise


def main():
    """Main application entry point."""
    logger.info("=" * 60)
    logger.info("Starting ResellerOS v1.0.0")
    logger.info("=" * 60)

    try:
        # Ensure required directories exist
        logger.info("Setting up application directories...")
        ensure_directories()

        # Initialize database
        initialize_database()

        # Start FastAPI backend in background thread
        logger.info("Starting backend API server...")
        backend_thread = Thread(target=run_backend, daemon=True, name="BackendThread")
        backend_thread.start()

        # Give backend time to start
        logger.info("Waiting for backend to initialize...")
        time.sleep(2)

        # Check if backend is running
        import requests
        try:
            response = requests.get("http://localhost:8000/api/health", timeout=5)
            if response.status_code == 200:
                logger.info("✓ Backend API is running")
            else:
                logger.warning("Backend API returned unexpected status")
        except Exception as e:
            logger.error(f"Backend API health check failed: {e}")
            logger.warning("Continuing anyway...")

        # Start PyQt6 GUI
        logger.info("Starting GUI application...")
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QIcon
        from src.gui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setApplicationName("ResellerOS")
        app.setOrganizationName("ResellerOS")
        app.setOrganizationDomain("reselleros.com")

        # Set app icon if available
        icon_path = "resources/icons/app_icon.png"
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))

        # Create and show main window
        window = MainWindow()
        window.show()

        logger.info("✓ ResellerOS GUI started successfully")
        logger.info("=" * 60)

        # Run application
        exit_code = app.exec()

        logger.info("ResellerOS shutting down...")
        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
