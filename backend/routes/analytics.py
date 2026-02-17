"""
Analytics Routes
Provides system-wide analytics and statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List

from database import get_db
from schemas import DrugAnalyticsResponse, SystemAnalyticsResponse, InteractionHistoryResponse
from models import DrugAnalytics, InteractionHistory, User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/drugs/top", response_model=List[DrugAnalyticsResponse])
def get_top_drugs(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get most frequently checked drugs
    
    Returns drugs sorted by total number of checks
    
    Args:
        limit: Maximum number of drugs to return (default: 10)
        db: Database session
        
    Returns:
        List of drug analytics sorted by total checks
    """
    try:
        top_drugs = db.query(DrugAnalytics).order_by(
            desc(DrugAnalytics.total_checks)
        ).limit(limit).all()
        
        return [DrugAnalyticsResponse.from_orm(drug) for drug in top_drugs]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve top drugs: {str(e)}"
        )


@router.get("/drugs/high-risk", response_model=List[DrugAnalyticsResponse])
def get_high_risk_drugs(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get drugs with most high-risk interactions
    
    Returns drugs sorted by high-risk interaction count
    
    Args:
        limit: Maximum number of drugs to return (default: 10)
        db: Database session
        
    Returns:
        List of drug analytics sorted by high-risk count
    """
    try:
        high_risk_drugs = db.query(DrugAnalytics).order_by(
            desc(DrugAnalytics.high_risk_count)
        ).limit(limit).all()
        
        return [DrugAnalyticsResponse.from_orm(drug) for drug in high_risk_drugs]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve high-risk drugs: {str(e)}"
        )


@router.get("/system")
def get_system_analytics(db: Session = Depends(get_db)):
    """
    Get system-wide analytics
    
    Returns comprehensive statistics about the entire system
    
    Args:
        db: Database session
        
    Returns:
        System analytics including user count, prediction count, risk distribution
    """
    try:
        from datetime import datetime, date
        
        # Count total users
        total_users = db.query(func.count(User.id)).scalar()
        
        # Count total predictions
        total_predictions = db.query(func.count(InteractionHistory.id)).scalar()
        
        # Count predictions made today
        today = date.today()
        checks_today = db.query(func.count(InteractionHistory.id)).filter(
            func.date(InteractionHistory.created_at) == today
        ).scalar()
        
        # Count unique drugs checked
        unique_drugs_query = db.query(
            func.count(func.distinct(DrugAnalytics.drug_name))
        ).scalar()
        
        # Count by risk level
        high_risk = db.query(func.count(InteractionHistory.id)).filter(
            InteractionHistory.risk_level == "High"
        ).scalar()
        
        moderate_risk = db.query(func.count(InteractionHistory.id)).filter(
            InteractionHistory.risk_level == "Moderate"
        ).scalar()
        
        low_risk = db.query(func.count(InteractionHistory.id)).filter(
            InteractionHistory.risk_level == "Low"
        ).scalar()
        
        # Get most checked drugs
        most_checked = db.query(DrugAnalytics).order_by(
            desc(DrugAnalytics.total_checks)
        ).limit(5).all()
        
        # Get recent activity
        recent_activity = db.query(InteractionHistory).order_by(
            desc(InteractionHistory.created_at)
        ).limit(10).all()
        
        return {
            "total_users": total_users or 0,
            "total_predictions": total_predictions or 0,
            "checks_today": checks_today or 0,
            "unique_drugs": unique_drugs_query or 0,
            "high_risk_interactions": high_risk or 0,
            "moderate_risk_interactions": moderate_risk or 0,
            "low_risk_interactions": low_risk or 0,
            "most_checked_drugs": [
                DrugAnalyticsResponse.from_orm(drug) for drug in most_checked
            ],
            "recent_activity": [
                InteractionHistoryResponse.from_orm(record) for record in recent_activity
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system analytics: {str(e)}"
        )


@router.get("/risk-distribution")
def get_risk_distribution(db: Session = Depends(get_db)):
    """
    Get risk level distribution
    
    Returns percentage breakdown of predictions by risk level
    
    Args:
        db: Database session
        
    Returns:
        Risk distribution statistics
    """
    try:
        total = db.query(func.count(InteractionHistory.id)).scalar() or 0
        
        if total == 0:
            return {
                "total_predictions": 0,
                "high_risk_percentage": 0,
                "moderate_risk_percentage": 0,
                "low_risk_percentage": 0
            }
        
        high_risk = db.query(func.count(InteractionHistory.id)).filter(
            InteractionHistory.risk_level == "High"
        ).scalar() or 0
        
        moderate_risk = db.query(func.count(InteractionHistory.id)).filter(
            InteractionHistory.risk_level == "Moderate"
        ).scalar() or 0
        
        low_risk = db.query(func.count(InteractionHistory.id)).filter(
            InteractionHistory.risk_level == "Low"
        ).scalar() or 0
        
        return {
            "total_predictions": total,
            "high_risk_count": high_risk,
            "moderate_risk_count": moderate_risk,
            "low_risk_count": low_risk,
            "high_risk_percentage": round((high_risk / total) * 100, 2),
            "moderate_risk_percentage": round((moderate_risk / total) * 100, 2),
            "low_risk_percentage": round((low_risk / total) * 100, 2)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve risk distribution: {str(e)}"
        )
