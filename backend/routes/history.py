
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from models import User, InteractionHistory
from schemas import UserHistoryResponse, UserResponse
from routes.auth import get_current_user

router = APIRouter(prefix="/history", tags=["History"])

@router.get("/me", response_model=UserHistoryResponse)
def get_user_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get interaction history for current user
    """
    # Query history
    history_query = db.query(InteractionHistory).filter(
        InteractionHistory.user_id == current_user.id
    ).order_by(InteractionHistory.created_at.desc())
    
    history_items = history_query.all()
    
    return {
        "user": UserResponse.model_validate(current_user),
        "total_checks": len(history_items),
        "history": history_items
    }


@router.get("/stats")
def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics for current user's interaction history
    """
    try:
        # Count total checks
        total_checks = db.query(func.count(InteractionHistory.id)).filter(
            InteractionHistory.user_id == current_user.id
        ).scalar() or 0
        
        # Count by risk level
        high_risk_count = db.query(func.count(InteractionHistory.id)).filter(
            InteractionHistory.user_id == current_user.id,
            InteractionHistory.risk_level == "High"
        ).scalar() or 0
        
        moderate_risk_count = db.query(func.count(InteractionHistory.id)).filter(
            InteractionHistory.user_id == current_user.id,
            InteractionHistory.risk_level == "Moderate"
        ).scalar() or 0
        
        low_risk_count = db.query(func.count(InteractionHistory.id)).filter(
            InteractionHistory.user_id == current_user.id,
            InteractionHistory.risk_level == "Low"
        ).scalar() or 0
        
        return {
            "total_checks": total_checks,
            "high_risk_count": high_risk_count,
            "moderate_risk_count": moderate_risk_count,
            "low_risk_count": low_risk_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user statistics: {str(e)}"
        )
