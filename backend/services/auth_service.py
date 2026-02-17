"""
Authentication Service
Handles user registration, login, and JWT token management
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional
import os
import re
from dotenv import load_dotenv

from models import User
from schemas import UserRegister, UserLogin

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production-use-openssl-rand-hex-32")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    
    Requirements:
    - Minimum 10 characters
    - At least one uppercase letter
    - At least one number
    - At least one special character
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 10:
        return False, "Password must be at least 10 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        return False, "Password must contain at least one special character"
    
    return True, ""



class AuthService:
    """Authentication service for user management"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt
        
        Note: bcrypt has a 72-byte limit. We truncate to 72 bytes to avoid errors.
        This is safe because:
        1. Our frontend enforces minimum 10 characters with complexity requirements
        2. 72 bytes is sufficient for strong passwords (typically 72 characters for ASCII)
        3. This is a standard practice when using bcrypt
        """
        # Truncate to 72 bytes to comply with bcrypt limit
        password_bytes = password.encode('utf-8')[:72]
        return pwd_context.hash(password_bytes.decode('utf-8'))
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Truncates password to 72 bytes to match hashing behavior
        """
        # Truncate to 72 bytes to match hashing
        password_bytes = plain_password.encode('utf-8')[:72]
        return pwd_context.verify(password_bytes.decode('utf-8'), hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def send_registration_otp(db: Session, user_data: UserRegister) -> tuple[bool, str]:
        """
        Send OTP for registration (does NOT create user yet)
        
        Args:
            db: Database session
            user_data: User registration data
            
        Returns:
            tuple: (success, message)
            
        Raises:
            ValueError: If email already exists or password is weak
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # Validate password strength
        is_valid, error_message = validate_password_strength(user_data.password)
        if not is_valid:
            raise ValueError(error_message)
        
        # Generate OTP
        from services.email_service import email_service
        from services.pending_registration_service import pending_registration_service
        
        otp = email_service.generate_otp()
        otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        
        # Hash password
        hashed_password = AuthService.hash_password(user_data.password)
        
        # Store pending registration (NOT in database yet)
        pending_registration_service.store_pending_registration(
            email=user_data.email,
            name=user_data.name,
            password_hash=hashed_password,
            otp=otp,
            otp_expiry=otp_expiry
        )
        
        # Send OTP email
        try:
            email_sent = email_service.send_otp_email(user_data.email, otp, user_data.name)
            if not email_sent:
                # Log OTP for development if email fails
                logger.warning(f"Email sending failed. OTP for {user_data.email}: {otp}")
                print(f"\n{'='*60}")
                print(f"📧 EMAIL SENDING DISABLED - DEVELOPMENT MODE")
                print(f"{'='*60}")
                print(f"User: {user_data.name} ({user_data.email})")
                print(f"OTP Code: {otp}")
                print(f"Expires: {otp_expiry}")
                print(f"{'='*60}\n")
            return True, "OTP sent successfully. Please check your email."
        except Exception as e:
            logger.error(f"Failed to send OTP email: {str(e)}")
            print(f"\n⚠️  OTP for {user_data.email}: {otp}\n")
            return True, "OTP generated. Check console for development mode."
    
    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> Optional[User]:
        """
        Authenticate a user with email and password
        
        Args:
            db: Database session
            login_data: Login credentials
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            return None
        
        if not AuthService.verify_password(login_data.password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def verify_otp_and_create_user(db: Session, email: str, otp: str) -> tuple[bool, str, Optional[User]]:
        """
        Verify OTP and create user account
        
        Args:
            db: Database session
            email: User's email
            otp: OTP code to verify
            
        Returns:
            tuple: (success, message, user)
        """
        from services.pending_registration_service import pending_registration_service
        from services.email_service import email_service
        
        # Verify OTP from pending registrations
        success, message, pending_data = pending_registration_service.verify_otp(email, otp)
        
        if not success:
            return False, message, None
        
        # Check if user already exists (double-check)
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            pending_registration_service.remove_pending_registration(email)
            return False, "Email already registered", None
        
        # Create user account
        try:
            new_user = User(
                name=pending_data['name'],
                email=email,
                password_hash=pending_data['password_hash'],
                email_verified=True,  # Already verified via OTP
                otp_code=None,
                otp_expiry=None
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Remove pending registration
            pending_registration_service.remove_pending_registration(email)
            
            # Send welcome email
            try:
                email_service.send_welcome_email(new_user.email, new_user.name)
            except Exception as e:
                logger.error(f"Failed to send welcome email: {str(e)}")
            
            return True, "Account created successfully! You can now login.", new_user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create user: {str(e)}")
            return False, f"Failed to create account: {str(e)}", None
    
    @staticmethod
    def resend_otp(db: Session, email: str) -> tuple[bool, str]:
        """
        Resend OTP verification code for pending registration
        
        Args:
            db: Database session
            email: User's email
            
        Returns:
            tuple: (success, message)
        """
        from services.pending_registration_service import pending_registration_service
        from services.email_service import email_service
        
        # Check pending registrations
        pending = pending_registration_service.get_pending_registration(email)
        
        if not pending:
            # Check if user already exists
            user = db.query(User).filter(User.email == email).first()
            if user:
                return False, "Email already registered. Please login."
            return False, "No pending registration found. Please register first."
        
        # Generate new OTP
        otp = email_service.generate_otp()
        otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        
        # Update pending registration
        pending['otp'] = otp
        pending['otp_expiry'] = otp_expiry
        
        # Send OTP email
        try:
            email_sent = email_service.send_otp_email(email, otp, pending['name'])
            if not email_sent:
                logger.warning(f"Email sending failed. OTP for {email}: {otp}")
                print(f"\n{'='*60}")
                print(f"📧 EMAIL SENDING DISABLED - DEVELOPMENT MODE")
                print(f"{'='*60}")
                print(f"User: {pending['name']} ({email})")
                print(f"OTP Code: {otp}")
                print(f"Expires: {otp_expiry}")
                print(f"{'='*60}\n")
            return True, "OTP sent successfully. Please check your email."
        except Exception as e:
            logger.error(f"Failed to send OTP email: {str(e)}")
            print(f"\n⚠️  OTP for {email}: {otp}\n")
            return True, "OTP generated. Check console for development mode."
    
    @staticmethod
    def check_email_verified(user: User) -> bool:
        """
        Check if user's email is verified
        
        Args:
            user: User object
            
        Returns:
            True if email is verified, False otherwise
        """
        return user.email_verified if user else False


# Create singleton instance
auth_service = AuthService()
