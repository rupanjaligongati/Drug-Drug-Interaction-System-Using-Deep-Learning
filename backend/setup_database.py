"""
Database Setup and Initialization Script

Run this script to:
1. Create database tables
2. Verify database connection
3. Create initial test user (optional)
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db, check_db_connection, get_db_context
from models import User
from services.auth_service import auth_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_database():
    """Initialize database and create tables"""
    logger.info("="*60)
    logger.info("Database Setup - Drug-Drug Interaction System v2.0")
    logger.info("="*60)
    
    # Check connection
    logger.info("\n1. Checking database connection...")
    if not check_db_connection():
        logger.error("✗ Database connection failed!")
        logger.error("Please check your DATABASE_URL in .env file")
        logger.error("Format: postgresql://username:password@host:port/database")
        return False
    
    logger.info("✓ Database connection successful")
    
    # Create tables
    logger.info("\n2. Creating database tables...")
    try:
        init_db()
        logger.info("✓ Database tables created successfully")
    except Exception as e:
        logger.error(f"✗ Failed to create tables: {e}")
        return False
    
    # Create test user (optional)
    logger.info("\n3. Creating test user...")
    try:
        with get_db_context() as db:
            # Check if test user already exists
            existing_user = db.query(User).filter(User.email == "test@example.com").first()
            
            if existing_user:
                logger.info("⚠ Test user already exists")
            else:
                # Create test user
                test_user = User(
                    name="Test User",
                    email="test@example.com",
                    password_hash=auth_service.hash_password("test123")
                )
                db.add(test_user)
                db.commit()
                logger.info("✓ Test user created")
                logger.info("  Email: test@example.com")
                logger.info("  Password: test123")
    except Exception as e:
        logger.warning(f"⚠ Could not create test user: {e}")
    
    logger.info("\n" + "="*60)
    logger.info("Database setup complete!")
    logger.info("="*60)
    logger.info("\nYou can now start the backend server:")
    logger.info("  cd backend")
    logger.info("  python main.py")
    logger.info("="*60)
    
    return True


if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
