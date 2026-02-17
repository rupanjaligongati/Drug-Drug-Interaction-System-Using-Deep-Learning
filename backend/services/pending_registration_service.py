"""
Pending Registration Service
Handles temporary storage of registration data until OTP verification
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# In-memory storage for pending registrations
# In production, use Redis or database table
pending_registrations: Dict[str, Dict] = {}


class PendingRegistrationService:
    """Service for managing pending user registrations"""
    
    @staticmethod
    def store_pending_registration(
        email: str,
        name: str,
        password_hash: str,
        otp: str,
        otp_expiry: datetime
    ) -> None:
        """
        Store pending registration data
        
        Args:
            email: User's email
            name: User's name
            password_hash: Hashed password
            otp: OTP code
            otp_expiry: OTP expiration time
        """
        pending_registrations[email] = {
            'name': name,
            'password_hash': password_hash,
            'otp': otp,
            'otp_expiry': otp_expiry,
            'created_at': datetime.utcnow()
        }
        logger.info(f"Stored pending registration for {email}")
    
    @staticmethod
    def get_pending_registration(email: str) -> Optional[Dict]:
        """
        Get pending registration data
        
        Args:
            email: User's email
            
        Returns:
            Registration data if exists, None otherwise
        """
        return pending_registrations.get(email)
    
    @staticmethod
    def remove_pending_registration(email: str) -> None:
        """
        Remove pending registration data
        
        Args:
            email: User's email
        """
        if email in pending_registrations:
            del pending_registrations[email]
            logger.info(f"Removed pending registration for {email}")
    
    @staticmethod
    def verify_otp(email: str, otp: str) -> tuple[bool, str, Optional[Dict]]:
        """
        Verify OTP for pending registration
        
        Args:
            email: User's email
            otp: OTP code to verify
            
        Returns:
            tuple: (success, message, registration_data)
        """
        pending = pending_registrations.get(email)
        
        if not pending:
            return False, "No pending registration found. Please register again.", None
        
        # Check if OTP expired
        if datetime.utcnow() > pending['otp_expiry']:
            PendingRegistrationService.remove_pending_registration(email)
            return False, "OTP has expired. Please register again.", None
        
        # Verify OTP
        if pending['otp'] != otp:
            return False, "Invalid OTP code. Please try again.", None
        
        return True, "OTP verified successfully", pending
    
    @staticmethod
    def cleanup_expired() -> None:
        """Remove expired pending registrations"""
        now = datetime.utcnow()
        expired_emails = [
            email for email, data in pending_registrations.items()
            if now > data['otp_expiry']
        ]
        
        for email in expired_emails:
            PendingRegistrationService.remove_pending_registration(email)
        
        if expired_emails:
            logger.info(f"Cleaned up {len(expired_emails)} expired pending registrations")


# Create singleton instance
pending_registration_service = PendingRegistrationService()
