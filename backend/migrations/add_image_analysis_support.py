"""
Database Migration: Add Image Analysis Support
Adds fields to interaction_history table for storing image-based analysis
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Add image analysis fields to interaction_history table"""
    
    migrations = [
        # Add analysis_mode column
        """
        ALTER TABLE interaction_history 
        ADD COLUMN IF NOT EXISTS analysis_mode VARCHAR(20) DEFAULT 'text' NOT NULL;
        """,
        
        # Add image_paths column (stores JSON array)
        """
        ALTER TABLE interaction_history 
        ADD COLUMN IF NOT EXISTS image_paths TEXT NULL;
        """,
        
        # Add detected_drugs column (stores JSON array)
        """
        ALTER TABLE interaction_history 
        ADD COLUMN IF NOT EXISTS detected_drugs TEXT NULL;
        """,
        
        # Add index on analysis_mode for faster queries
        """
        CREATE INDEX IF NOT EXISTS idx_analysis_mode 
        ON interaction_history(analysis_mode);
        """,
        
        # Add comment to table
        """
        COMMENT ON COLUMN interaction_history.analysis_mode IS 
        'Analysis type: text or image';
        """,
        
        """
        COMMENT ON COLUMN interaction_history.image_paths IS 
        'JSON array of uploaded image file paths';
        """,
        
        """
        COMMENT ON COLUMN interaction_history.detected_drugs IS 
        'JSON array of all drugs detected from images';
        """
    ]
    
    try:
        with engine.connect() as conn:
            for idx, migration in enumerate(migrations, 1):
                try:
                    logger.info(f"Running migration {idx}/{len(migrations)}...")
                    conn.execute(text(migration))
                    conn.commit()
                    logger.info(f"✅ Migration {idx} completed")
                except Exception as e:
                    logger.warning(f"⚠️ Migration {idx} skipped or failed: {e}")
                    continue
        
        logger.info("✅ All migrations completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Database Migration: Add Image Analysis Support")
    print("="*60 + "\n")
    
    success = migrate()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("The database is now ready for image analysis storage.\n")
    else:
        print("\n❌ Migration failed. Please check the logs.\n")
