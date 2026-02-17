"""
Database Migration: Add Email Verification Fields
Adds email_verified, otp_code, and otp_expiry columns to users table
"""

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def migrate():
    """Add email verification fields to users table"""
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in .env file")
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            print("🔄 Starting migration: Add email verification fields...")
            
            # Check if columns already exist
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('email_verified', 'otp_code', 'otp_expiry')
            """)
            
            existing_columns = [row[0] for row in conn.execute(check_query)]
            
            if len(existing_columns) == 3:
                print("✅ Migration already applied - all columns exist")
                return True
            
            # Add email_verified column
            if 'email_verified' not in existing_columns:
                print("  ➤ Adding email_verified column...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN email_verified BOOLEAN DEFAULT FALSE NOT NULL
                """))
                conn.commit()
                print("  ✓ email_verified column added")
            else:
                print("  ⊙ email_verified column already exists")
            
            # Add otp_code column
            if 'otp_code' not in existing_columns:
                print("  ➤ Adding otp_code column...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN otp_code VARCHAR(10)
                """))
                conn.commit()
                print("  ✓ otp_code column added")
            else:
                print("  ⊙ otp_code column already exists")
            
            # Add otp_expiry column
            if 'otp_expiry' not in existing_columns:
                print("  ➤ Adding otp_expiry column...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN otp_expiry TIMESTAMP
                """))
                conn.commit()
                print("  ✓ otp_expiry column added")
            else:
                print("  ⊙ otp_expiry column already exists")
            
            print("\n✅ Migration completed successfully!")
            print("\n📋 Summary:")
            print("  - email_verified: Boolean field to track verification status")
            print("  - otp_code: Stores the OTP code sent to user")
            print("  - otp_expiry: Timestamp when OTP expires")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("Database Migration: Email Verification")
    print("="*60)
    print()
    
    success = migrate()
    
    if success:
        print("\n" + "="*60)
        print("✅ Migration completed successfully!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ Migration failed!")
        print("="*60)
