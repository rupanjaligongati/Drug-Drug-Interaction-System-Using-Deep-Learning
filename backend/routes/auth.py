"""
Authentication Routes
Handles user registration, login, and token management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from schemas import UserRegister, UserLogin, TokenResponse, UserResponse, VerifyOTPRequest, ResendOTPRequest
from services.auth_service import auth_service
from models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    """
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = auth_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Send OTP for registration (Step 1 of 2)
    
    Validates user data and sends OTP to email. User account is NOT created yet.
    """
    try:
        # Send OTP (does not create user)
        success, message = auth_service.send_registration_otp(db, user_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return {
            "success": True,
            "message": message,
            "email": user_data.email,
            "next_step": "verify_otp"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password
    
    Returns JWT access token on successful authentication
    """
    try:
        # Authenticate user
        user = auth_service.authenticate_user(db, login_data)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        access_token = auth_service.create_access_token(
            data={"user_id": user.id, "email": user.email}
        )
        
        # Check if email is verified
        requires_verification = not user.email_verified
        message = None
        if requires_verification:
            message = "Please verify your email to access all features"
        
        return TokenResponse(
            access_token=access_token,
            user=UserResponse.from_orm(user),
            requires_verification=requires_verification,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/verify-otp", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def verify_otp(verify_data: VerifyOTPRequest, db: Session = Depends(get_db)):
    """
    Verify OTP and create user account (Step 2 of 2)
    
    Verifies the OTP and creates the user account. Returns JWT token for immediate login.
    """
    try:
        success, message, user = auth_service.verify_otp_and_create_user(
            db, 
            verify_data.email, 
            verify_data.otp
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Create access token for the new user
        access_token = auth_service.create_access_token(
            data={"user_id": user.id, "email": user.email}
        )
        
        return TokenResponse(
            access_token=access_token,
            user=UserResponse.from_orm(user),
            requires_verification=False,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OTP verification failed: {str(e)}"
        )


@router.post("/resend-otp")
def resend_otp(resend_data: ResendOTPRequest, db: Session = Depends(get_db)):
    """
    Resend OTP verification code
    
    Generates and sends a new OTP to the user's email
    """
    try:
        success, message = auth_service.resend_otp(db, resend_data.email)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return {
            "success": True,
            "message": message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resend OTP: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    
    Requires authentication
    """
    return UserResponse.from_orm(current_user)


@router.get("/verify")
def verify_token(current_user: User = Depends(get_current_user)):
    """
    Verify if token is valid
    
    Returns user info if token is valid
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "email_verified": current_user.email_verified
    }
