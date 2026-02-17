# Preprocessing utilities for backend

import pandas as pd
import numpy as np
from typing import Dict, Optional
import re

def normalize_drug_name(name: str) -> str:
    """
    Normalize drug name for consistent matching
    
    Args:
        name: Raw drug name
        
    Returns:
        Normalized drug name (lowercase, stripped)
    """
    if not name:
        return ""
    
    # Convert to lowercase and strip whitespace
    normalized = str(name).lower().strip()
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    return normalized


def validate_drug_input(drug1: str, drug2: str) -> tuple[bool, str]:
    """
    Validate drug input
    
    Args:
        drug1: First drug name
        drug2: Second drug name
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if drugs are provided
    if not drug1 or not drug1.strip():
        return False, "First drug name is required"
    
    if not drug2 or not drug2.strip():
        return False, "Second drug name is required"
    
    # Check if drugs are different
    if normalize_drug_name(drug1) == normalize_drug_name(drug2):
        return False, "Please enter two different drugs"
    
    # Check length
    if len(drug1) > 200 or len(drug2) > 200:
        return False, "Drug names are too long"
    
    return True, ""


def get_drug_features_from_db(drug_name: str, drug_features_db: Dict) -> Optional[Dict]:
    """
    Get drug features from database
    
    Args:
        drug_name: Normalized drug name
        drug_features_db: Dictionary of drug features
        
    Returns:
        Dictionary of drug features or None if not found
    """
    normalized = normalize_drug_name(drug_name)
    
    # Direct lookup
    if normalized in drug_features_db:
        return drug_features_db[normalized]
    
    # Try partial matching (for brand names, etc.)
    for db_drug, features in drug_features_db.items():
        if normalized in db_drug or db_drug in normalized:
            return features
    
    return None


def prepare_feature_vector(drug1_features: Dict, drug2_features: Dict) -> Dict:
    """
    Prepare feature vector from drug features
    
    Args:
        drug1_features: Features for first drug
        drug2_features: Features for second drug
        
    Returns:
        Combined feature dictionary
    """
    features = {
        # Drug 1 features
        'drug1_rating': drug1_features.get('rating', 0),
        'drug1_pregnancy': drug1_features.get('pregnancy_category', 'Unknown'),
        'drug1_alcohol': drug1_features.get('alcohol', 'Unknown'),
        'drug1_rx_otc': drug1_features.get('rx_otc', 'Unknown'),
        
        # Drug 2 features
        'drug2_rating': drug2_features.get('rating', 0),
        'drug2_pregnancy': drug2_features.get('pregnancy_category', 'Unknown'),
        'drug2_alcohol': drug2_features.get('alcohol', 'Unknown'),
        'drug2_rx_otc': drug2_features.get('rx_otc', 'Unknown'),
    }
    
    return features


def get_default_drug_features() -> Dict:
    """
    Get default drug features for unknown drugs
    
    Returns:
        Dictionary with default values
    """
    return {
        'drug_classes': 'Unknown',
        'pregnancy_category': 'Unknown',
        'alcohol': 'Unknown',
        'rating': 0,
        'rx_otc': 'Unknown'
    }


def calculate_risk_level(confidence: float) -> str:
    """
    Calculate risk level based on confidence score
    
    Args:
        confidence: Prediction confidence (0-1)
        
    Returns:
        Risk level: "Low", "Moderate", or "High"
    """
    if confidence >= 0.8:
        return "High"
    elif confidence >= 0.5:
        return "Moderate"
    else:
        return "Low"


def generate_interaction_summary(drug1: str, drug2: str, has_interaction: bool, confidence: float) -> str:
    """
    Generate interaction summary text
    
    Args:
        drug1: First drug name
        drug2: Second drug name
        has_interaction: Whether interaction was predicted
        confidence: Prediction confidence
        
    Returns:
        Summary text
    """
    if has_interaction:
        return (f"A potential drug-drug interaction has been detected between {drug1.title()} "
                f"and {drug2.title()} with {confidence*100:.1f}% confidence. "
                f"These medications may interact when taken together.")
    else:
        return (f"No significant interaction detected between {drug1.title()} and {drug2.title()} "
                f"based on available data (confidence: {confidence*100:.1f}%).")


def generate_warnings(drug1: str, drug2: str, has_interaction: bool, risk_level: str) -> str:
    """
    Generate warning text based on prediction
    
    Args:
        drug1: First drug name
        drug2: Second drug name
        has_interaction: Whether interaction was predicted
        risk_level: Risk level
        
    Returns:
        Warning text
    """
    if not has_interaction:
        return ("While no interaction is predicted, always monitor for unexpected side effects. "
                "Individual responses may vary.")
    
    if risk_level == "High":
        return (f"⚠️ HIGH RISK: The combination of {drug1.title()} and {drug2.title()} may pose "
                f"significant health risks. Consult your healthcare provider immediately before "
                f"taking these medications together. Do not start, stop, or change dosages without "
                f"medical supervision.")
    elif risk_level == "Moderate":
        return (f"⚠️ MODERATE RISK: {drug1.title()} and {drug2.title()} may interact. "
                f"Discuss this combination with your healthcare provider. Dosage adjustments "
                f"or additional monitoring may be necessary.")
    else:
        return (f"⚠️ LOW RISK: A potential interaction between {drug1.title()} and {drug2.title()} "
                f"has been identified, but the risk appears to be low. Inform your healthcare "
                f"provider about all medications you are taking.")
