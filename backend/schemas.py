"""
Pydantic Schemas for Request/Response Validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


# ==================== Authentication Schemas ====================

class UserRegister(BaseModel):
    """User registration request"""
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User data response"""
    id: int
    name: str
    email: str
    email_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class VerifyOTPRequest(BaseModel):
    """OTP verification request"""
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)


class ResendOTPRequest(BaseModel):
    """Resend OTP request"""
    email: EmailStr


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    requires_verification: bool = False
    message: Optional[str] = None


# ==================== Prediction Schemas ====================

class PredictionRequest(BaseModel):
    """Drug interaction prediction request"""
    drug1: str = Field(..., min_length=1, max_length=255, description="First drug name")
    drug2: str = Field(..., min_length=1, max_length=255, description="Second drug name")
    drug3: Optional[str] = Field(None, description="Third drug name (optional)")
    drug4: Optional[str] = Field(None, description="Fourth drug name (optional)")
    drug5: Optional[str] = Field(None, description="Fifth drug name (optional)")
    
    @validator('drug1', 'drug2')
    def drug_name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Drug name cannot be empty')
        return v.strip()


class ExplanationResponse(BaseModel):
    """Explanation data"""
    explanation_type: str
    explanation_text: str
    severity_contribution: Optional[str] = None
    
    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    """Alternative drug recommendation"""
    alternative_drug: str
    reason: str
    safety_score: Optional[float] = None
    medical_condition: Optional[str] = None
    
    class Config:
        from_attributes = True


class PredictionResponse(BaseModel):
    """Complete prediction response with all details"""
    # Basic prediction
    interaction: str
    confidence: float
    risk_level: str
    severity: Optional[str] = None
    
    # Detailed information
    interaction_summary: str
    warnings: str
    
    # Explainable AI
    explanations: List[ExplanationResponse] = []
    
    # Recommendations
    recommendations: List[RecommendationResponse] = []
    
    # Metadata
    disclaimer: str
    analyzed_drugs: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ==================== History Schemas ====================

class InteractionHistoryResponse(BaseModel):
    """Single interaction history record"""
    id: int
    drug_1: str
    drug_2: str
    interaction: str
    confidence: float
    risk_level: str
    severity: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserHistoryResponse(BaseModel):
    """User's complete interaction history"""
    user: UserResponse
    total_checks: int
    history: List[InteractionHistoryResponse]
    
    class Config:
        from_attributes = True


# ==================== Analytics Schemas ====================

class DrugAnalyticsResponse(BaseModel):
    """Drug analytics data"""
    drug_name: str
    total_checks: int
    high_risk_count: int
    moderate_risk_count: int
    low_risk_count: int
    last_checked: datetime
    
    class Config:
        from_attributes = True


class SystemAnalyticsResponse(BaseModel):
    """System-wide analytics"""
    total_users: int
    total_predictions: int
    high_risk_interactions: int
    moderate_risk_interactions: int
    low_risk_interactions: int
    most_checked_drugs: List[DrugAnalyticsResponse]
    recent_activity: List[InteractionHistoryResponse]


# ==================== Health Check Schema ====================

class HealthResponse(BaseModel):
    """API health check response"""
    status: str
    timestamp: datetime
    database_connected: bool
    model_loaded: bool
    version: str = "2.0.0"

    model_config = {
        "protected_namespaces": ()
    }
