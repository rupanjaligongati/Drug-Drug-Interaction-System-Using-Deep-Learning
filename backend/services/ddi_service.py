# Drug-Drug Interaction Prediction Service

import numpy as np
import pandas as pd
import pickle
import logging
from typing import Dict, Tuple
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.preprocess import (
    normalize_drug_name,
    get_drug_features_from_db,
    prepare_feature_vector,
    get_default_drug_features,
    calculate_risk_level,
    generate_interaction_summary,
    generate_warnings
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DDIService:
    """
    Drug-Drug Interaction Prediction Service
    
    This service handles:
    - Loading the trained ML model
    - Loading drug feature database
    - Making predictions
    - Generating responses
    """
    
    def __init__(self):
        """Initialize the service"""
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.drug_features_db = None
        self.model_loaded = False
        
    def load_model(self):
        """Load the trained model and preprocessor"""
        try:
            # Import TensorFlow only when needed
            import tensorflow as tf
            
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_dir = os.path.join(project_root, 'model')
            model_path = os.path.join(model_dir, 'ddi_model.h5')
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found at {model_path}")
            
            self.model = tf.keras.models.load_model(model_path)
            logger.info("✓ Model loaded successfully")
            
            # Load metadata
            metadata_path = os.path.join(model_dir, 'model_metadata.pkl')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                    self.scaler = metadata.get('scaler')
                    self.feature_names = metadata.get('feature_names')
                logger.info("✓ Model metadata loaded")
            
            # Load preprocessed data (for drug features)
            data_path = os.path.join(model_dir, 'processed_data.pkl')
            if os.path.exists(data_path):
                with open(data_path, 'rb') as f:
                    data = pickle.load(f)
                    self.drug_features_db = data.get('drug_features', {})
                logger.info(f"✓ Drug features database loaded ({len(self.drug_features_db)} drugs)")
            
            self.model_loaded = True
            logger.info("✓ DDI Service initialized successfully")
            
        except Exception as e:
            logger.error(f"✗ Error loading model: {e}")
            raise
    
    def predict_interaction(self, drug1: str, drug2: str, user_id: int = None, db_session = None) -> Dict:
        """
        Predict drug-drug interaction with database integration
        
        Args:
            drug1: First drug name
            drug2: Second drug name
            user_id: Optional user ID for saving history
            db_session: Optional database session
            
        Returns:
            Dictionary with prediction results including explanations and recommendations
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Normalize drug names
            drug1_normalized = normalize_drug_name(drug1)
            drug2_normalized = normalize_drug_name(drug2)
            
            logger.info(f"Predicting interaction: {drug1_normalized} + {drug2_normalized}")
            
            # Get drug features
            drug1_features = get_drug_features_from_db(drug1_normalized, self.drug_features_db)
            drug2_features = get_drug_features_from_db(drug2_normalized, self.drug_features_db)
            
            # Check if drugs are in database
            drugs_found = []
            if drug1_features is None:
                drug1_features = get_default_drug_features()
                logger.warning(f"Drug not found in database: {drug1_normalized}, using defaults")
            else:
                drugs_found.append(drug1_normalized)
            
            if drug2_features is None:
                drug2_features = get_default_drug_features()
                logger.warning(f"Drug not found in database: {drug2_normalized}, using defaults")
            else:
                drugs_found.append(drug2_normalized)
            
            # Prepare feature vector
            features = prepare_feature_vector(drug1_features, drug2_features)
            
            # Convert to DataFrame for encoding
            features_df = pd.DataFrame([features])
            
            # One-hot encode categorical features
            categorical_cols = ['drug1_pregnancy', 'drug1_alcohol', 'drug1_rx_otc',
                              'drug2_pregnancy', 'drug2_alcohol', 'drug2_rx_otc']
            
            features_encoded = pd.get_dummies(features_df, columns=categorical_cols, dummy_na=True)
            
            # Align with training features
            for col in self.feature_names:
                if col not in features_encoded.columns:
                    features_encoded[col] = 0
            
            # Ensure same column order
            features_encoded = features_encoded[self.feature_names]
            
            # Scale features
            if self.scaler:
                features_scaled = self.scaler.transform(features_encoded)
            else:
                features_scaled = features_encoded.values
            
            # Make prediction
            prediction_proba = self.model.predict(features_scaled, verbose=0)[0][0]
            prediction = int(prediction_proba > 0.5)
            
            # Calculate confidence
            confidence = float(prediction_proba if prediction == 1 else 1 - prediction_proba)
            
            # Determine risk level
            risk_level = calculate_risk_level(prediction_proba)
            
            # Determine severity
            if risk_level == "High":
                severity = "Severe"
            elif risk_level == "Moderate":
                severity = "Moderate"
            else:
                severity = "Mild"
            
            # Generate response
            has_interaction = prediction == 1
            
            response = {
                "interaction": "Yes" if has_interaction else "No",
                "confidence": round(confidence, 3),
                "risk_level": risk_level,
                "severity": severity,
                "interaction_summary": generate_interaction_summary(
                    drug1, drug2, has_interaction, confidence
                ),
                "warnings": generate_warnings(drug1, drug2, has_interaction, risk_level),
                "disclaimer": (
                    "⚕️ MEDICAL DISCLAIMER: This system is for educational and decision-support "
                    "purposes only. It does NOT replace professional medical advice, diagnosis, "
                    "or treatment. Always consult qualified healthcare professionals before "
                    "making any medication decisions. Individual patient factors, dosages, and "
                    "medical conditions can significantly affect drug interactions."
                )
            }
            
            # Add warning if drugs not in database
            if len(drugs_found) < 2:
                missing_drugs = []
                if drug1_normalized not in drugs_found:
                    missing_drugs.append(drug1)
                if drug2_normalized not in drugs_found:
                    missing_drugs.append(drug2)
                
                response["warnings"] += (
                    f"\n\n⚠️ NOTE: {', '.join(missing_drugs)} not found in database. "
                    f"Prediction based on limited information. Results may be less accurate."
                )
            
            # Generate explanations using Explainable AI
            try:
                from services.explainable_ai_service import explainable_ai_service
                explanations = explainable_ai_service.generate_comprehensive_explanation(
                    drug1, drug2, confidence
                )
                response["explanations"] = explanations
            except Exception as e:
                logger.warning(f"Could not generate explanations: {e}")
                response["explanations"] = []
            
            # Generate recommendations
            try:
                from services.recommendation_service import recommendation_service
                recommendations = recommendation_service.get_recommendations_for_interaction(
                    drug1, drug2
                )
                response["recommendations"] = recommendations
            except Exception as e:
                logger.warning(f"Could not generate recommendations: {e}")
                response["recommendations"] = []
            
            # Refine with Gemini (Validation Layer)
            try:
                from services.gemini_service import gemini_service
                logger.info(f"🔮 Calling Gemini for: {drug1} + {drug2}")
                
                # Log state before calling Gemini
                logger.debug(f"State before Gemini: Explanations={len(response.get('explanations', []))}, Recommendations={len(response.get('recommendations', []))}")
                
                # Only use Gemini if interaction is predicted or if explicitly requested
                # For now, we apply it to all to improve explanations
                response = gemini_service.validate_and_refine(response, drug1, drug2)
                
                # Log state after calling Gemini
                logger.info(f"✨ Gemini returned. Explanations={len(response.get('explanations', []))}, Recommendations={len(response.get('recommendations', []))}")
                
            except Exception as e:
                logger.error(f"❌ Gemini refinement failed, proceeding with original: {e}", exc_info=True)
            
            # Save to database if user_id and db_session provided
            if user_id and db_session:
                try:
                    from models import InteractionHistory, Explanation, Recommendation
                    
                    # Create interaction history record
                    interaction_record = InteractionHistory(
                        user_id=user_id,
                        drug_1=drug1,
                        drug_2=drug2,
                        interaction=response["interaction"],
                        confidence=response["confidence"],
                        risk_level=response["risk_level"],
                        severity=severity
                    )
                    db_session.add(interaction_record)
                    db_session.flush()  # Get the ID
                    
                    # Save explanations
                    for exp in response.get("explanations", []):
                        explanation_record = Explanation(
                            interaction_id=interaction_record.id,
                            explanation_type=exp.get("explanation_type", "general"),
                            explanation_text=exp.get("explanation_text", ""),
                            severity_contribution=exp.get("severity_contribution")
                        )
                        db_session.add(explanation_record)
                    
                    # Save recommendations
                    for rec in response.get("recommendations", []):
                        recommendation_record = Recommendation(
                            interaction_id=interaction_record.id,
                            alternative_drug=rec.get("alternative_drug", ""),
                            reason=rec.get("reason", ""),
                            safety_score=rec.get("safety_score"),
                            medical_condition=rec.get("medical_condition")
                        )
                        db_session.add(recommendation_record)
                    
                    # Update analytics
                    from models import DrugAnalytics
                    from sqlalchemy import func
                    
                    for drug_name in [drug1, drug2]:
                        analytics = db_session.query(DrugAnalytics).filter(
                            DrugAnalytics.drug_name == drug_name
                        ).first()
                        
                        if analytics:
                            analytics.total_checks += 1
                            if risk_level == "High":
                                analytics.high_risk_count += 1
                            elif risk_level == "Moderate":
                                analytics.moderate_risk_count += 1
                            else:
                                analytics.low_risk_count += 1
                            analytics.last_checked = func.now()
                        else:
                            analytics = DrugAnalytics(
                                drug_name=drug_name,
                                total_checks=1,
                                high_risk_count=1 if risk_level == "High" else 0,
                                moderate_risk_count=1 if risk_level == "Moderate" else 0,
                                low_risk_count=1 if risk_level == "Low" else 0
                            )
                            db_session.add(analytics)
                    
                    db_session.commit()
                    logger.info(f"Saved interaction to database for user {user_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to save to database: {e}")
                    db_session.rollback()
            
            # Log prediction
            logger.info(
                f"Prediction complete: {drug1} + {drug2} = {response['interaction']} "
                f"(confidence: {confidence:.3f}, risk: {risk_level})"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            raise
    
    def get_health_status(self) -> Dict:
        """Get service health status"""
        return {
            "status": "healthy" if self.model_loaded else "unhealthy",
            "message": "Drug-Drug Interaction API is running",
            "model_loaded": self.model_loaded
        }


# Global service instance
ddi_service = DDIService()
