"""
SQLAlchemy Database Models
Defines all database tables and relationships
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """
    User table - stores user authentication and profile data
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Email verification fields
    email_verified = Column(Boolean, default=False, nullable=False)
    otp_code = Column(String(10), nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    
    # Relationships
    interaction_history = relationship("InteractionHistory", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name}, verified={self.email_verified})>"


class InteractionHistory(Base):
    """
    Interaction history table - stores all drug interaction predictions
    Supports both text-based and image-based analysis
    """
    __tablename__ = "interaction_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    drug_1 = Column(String(255), nullable=False)
    drug_2 = Column(String(255), nullable=False)
    interaction = Column(String(50), nullable=False)  # Yes/No
    confidence = Column(Float, nullable=False)
    risk_level = Column(String(50), nullable=False)  # Low/Moderate/High
    severity = Column(String(50))  # Mild/Moderate/Severe
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Image analysis support
    analysis_mode = Column(String(20), default="text", nullable=False)  # "text" or "image"
    image_paths = Column(Text, nullable=True)  # JSON array of image file paths
    detected_drugs = Column(Text, nullable=True)  # JSON array of all detected drugs
    
    # Relationships
    user = relationship("User", back_populates="interaction_history")
    explanations = relationship("Explanation", back_populates="interaction", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="interaction", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_drugs', 'drug_1', 'drug_2'),
        Index('idx_analysis_mode', 'analysis_mode'),
    )
    
    def __repr__(self):
        return f"<InteractionHistory(id={self.id}, drugs={self.drug_1}+{self.drug_2}, risk={self.risk_level}, mode={self.analysis_mode})>"


class Explanation(Base):
    """
    Explanations table - stores explainable AI results
    """
    __tablename__ = "explanations"
    
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interaction_history.id", ondelete="CASCADE"), nullable=False, index=True)
    explanation_type = Column(String(100), nullable=False)  # drug_class, side_effect, pregnancy, alcohol
    explanation_text = Column(Text, nullable=False)
    severity_contribution = Column(String(50))  # Low/Medium/High
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    interaction = relationship("InteractionHistory", back_populates="explanations")
    
    def __repr__(self):
        return f"<Explanation(id={self.id}, type={self.explanation_type})>"


class Recommendation(Base):
    """
    Recommendations table - stores alternative drug suggestions
    """
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interaction_history.id", ondelete="CASCADE"), nullable=False, index=True)
    alternative_drug = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    safety_score = Column(Float)  # 0-1 score
    medical_condition = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    interaction = relationship("InteractionHistory", back_populates="recommendations")
    
    def __repr__(self):
        return f"<Recommendation(id={self.id}, alternative={self.alternative_drug})>"


class DrugAnalytics(Base):
    """
    Analytics table - aggregated statistics for dashboard
    """
    __tablename__ = "drug_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    drug_name = Column(String(255), nullable=False, unique=True, index=True)
    total_checks = Column(Integer, default=0)
    high_risk_count = Column(Integer, default=0)
    moderate_risk_count = Column(Integer, default=0)
    low_risk_count = Column(Integer, default=0)
    last_checked = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<DrugAnalytics(drug={self.drug_name}, checks={self.total_checks})>"
