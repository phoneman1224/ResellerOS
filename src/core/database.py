"""
Database configuration and session management.
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
import logging

from src.config.settings import settings

logger = logging.getLogger(__name__)

# Create declarative base
Base = declarative_base()

# Database engine
engine = None
SessionLocal = None


def _configure_sqlite(dbapi_con, connection_record):
    """Configure SQLite connection with WAL mode and foreign keys."""
    try:
        # Enable WAL mode for better concurrency
        dbapi_con.execute("PRAGMA journal_mode=WAL")
        # Enable foreign key constraints
        dbapi_con.execute("PRAGMA foreign_keys=ON")
        # Optimize for performance
        dbapi_con.execute("PRAGMA synchronous=NORMAL")
        dbapi_con.execute("PRAGMA cache_size=10000")
        dbapi_con.execute("PRAGMA temp_store=MEMORY")
        logger.debug("SQLite connection configured with WAL mode")
    except Exception as e:
        logger.error(f"Failed to configure SQLite: {e}")


def init_engine():
    """Initialize database engine."""
    global engine, SessionLocal

    if engine is not None:
        return engine

    logger.info(f"Initializing database: {settings.database_url}")

    # Create engine
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
        poolclass=StaticPool if "sqlite" in settings.database_url else None,
        echo=settings.is_development,
        pool_pre_ping=True,
    )

    # Configure SQLite if using SQLite
    if "sqlite" in settings.database_url:
        event.listen(engine, "connect", _configure_sqlite)

    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    logger.info("Database engine initialized")
    return engine


def get_engine():
    """Get database engine, initializing if necessary."""
    global engine
    if engine is None:
        init_engine()
    return engine


def get_session_factory():
    """Get session factory, initializing if necessary."""
    global SessionLocal
    if SessionLocal is None:
        init_engine()
    return SessionLocal


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session with automatic commit/rollback.

    Usage:
        with get_db() as db:
            # do database operations
            # automatically commits on success, rolls back on error
    """
    factory = get_session_factory()
    db = factory()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database transaction failed: {e}")
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """Get a new database session (manual management).

    Note: Caller is responsible for closing the session.
    Prefer using get_db() context manager when possible.

    Returns:
        New database session
    """
    factory = get_session_factory()
    return factory()


def init_database():
    """Initialize database schema.

    Creates all tables defined in models.
    """
    try:
        # Import all models to register them with Base
        from src.models.item import Item
        from src.models.expense import Expense
        from src.models.sale import Sale
        from src.models.settings import UserSettings

        # Initialize engine
        engine = get_engine()

        # Create all tables
        Base.metadata.create_all(bind=engine)

        logger.info("Database schema initialized successfully")

        # Verify tables were created
        with engine.connect() as conn:
            if "sqlite" in settings.database_url:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result]
                logger.info(f"Created tables: {', '.join(tables)}")

    except Exception as e:
        logger.critical(f"Database initialization failed: {e}")
        raise


def drop_all_tables():
    """Drop all database tables.

    WARNING: This will delete all data!
    Only use for testing or development.
    """
    if settings.is_production:
        raise RuntimeError("Cannot drop tables in production!")

    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")


def reset_database():
    """Reset database by dropping and recreating all tables.

    WARNING: This will delete all data!
    Only use for testing or development.
    """
    if settings.is_production:
        raise RuntimeError("Cannot reset database in production!")

    drop_all_tables()
    init_database()
    logger.warning("Database has been reset")


def check_database_health() -> bool:
    """Check if database is accessible and healthy.

    Returns:
        True if database is healthy, False otherwise
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
