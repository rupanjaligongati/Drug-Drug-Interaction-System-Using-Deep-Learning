"""
PostgreSQL Database Configuration and Connection Management
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Database URL from environment variable
# Format: postgresql://username:password@host:port/database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:1234@localhost:5432/ddi_system"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    echo=False  # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function for FastAPI routes
    Provides database session and ensures proper cleanup
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database sessions
    Usage: with get_db_context() as db:
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created successfully")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        raise


def check_db_connection():
    """
    Check if database connection is working
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✓ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False
