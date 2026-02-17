# API Routes for Drug-Drug Interaction Prediction

from fastapi import APIRouter, HTTPException, status, Depends, Header, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import logging
import sys
import os
import re

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import PredictionRequest, PredictionResponse, HealthResponse
from services.ddi_service import ddi_service
from utils.preprocess import validate_drug_input
from database import get_db, check_db_connection
from models import User

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.get("/", tags=["Info"])
async def root():
    """API information endpoint"""
    return {
        "name": "Drug-Drug Interaction Prediction API",
        "version": "1.0.0",
        "description": "AI-powered system for predicting drug-drug interactions using deep learning",
        "endpoints": {
            "POST /predict": "Predict drug-drug interaction",
            "GET /health": "Health check",
            "GET /docs": "API documentation"
        },
        "disclaimer": "For educational and decision-support purposes only. Not a replacement for professional medical advice."
    }


@router.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    
    Returns the current status of the API, model, and database
    """
    try:
        health_status = ddi_service.get_health_status()
        db_connected = check_db_connection()
        
        return {
            "status": "healthy" if health_status["model_loaded"] and db_connected else "degraded",
            "timestamp": None,  # Will be set by response
            "database_connected": db_connected,
            "model_loaded": health_status["model_loaded"],
            "version": "2.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": None,
            "database_connected": False,
            "model_loaded": False,
            "version": "2.0.0",
            "error": str(e)
        }


@router.post("/predict", tags=["Prediction"])
async def predict_interaction(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Predict drug-drug interaction
    
    This endpoint takes two drug names and returns:
    - Whether an interaction is predicted
    - Confidence score (0-1)
    - Risk level (Low/Moderate/High)
    - Severity (Mild/Moderate/Severe)
    - Interaction summary
    - Warnings and precautions
    - Explainable AI explanations
    - Alternative drug recommendations
    - Medical disclaimer
    
    If authenticated, saves prediction to user history
    
    Args:
        request: PredictionRequest with drug1 and drug2
        db: Database session
        authorization: Optional Bearer token from header
        
    Returns:
        PredictionResponse with prediction results
        
    Raises:
        HTTPException: If validation fails or prediction error occurs
    """
    try:
        if not ddi_service.model_loaded:
            try:
                ddi_service.load_model()
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Model load failed: {str(e)}"
                )
        
        # Check if user is authenticated (optional)
        user_id = None
        if authorization and authorization.startswith("Bearer "):
            try:
                from services.auth_service import auth_service
                token = authorization.split(" ")[1]
                payload = auth_service.verify_token(token)
                if payload:
                    user_id = payload.get("user_id")
                    logger.info(f"Authenticated prediction for user_id: {user_id}")
            except Exception as e:
                logger.warning(f"Token verification failed: {e}")
                pass  # Continue without authentication

        # Collect all valid drugs
        drugs = [d for d in [request.drug1, request.drug2, request.drug3, request.drug4, request.drug5] if d and d.strip()]
        
        # Validate unique drugs (at least 2)
        unique_drugs = sorted(list(set(drugs)))
        if len(unique_drugs) < 2:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least 2 unique drugs are required for interaction analysis"
            )
            
        # Generate all unique pairs
        import itertools
        pairs = list(itertools.combinations(unique_drugs, 2))
        
        results = []
        for d1, d2 in pairs:
            # Validate input for each pair
            is_valid, _ = validate_drug_input(d1, d2)
            if not is_valid:
                continue
                
            # Predict
            res = ddi_service.predict_interaction(
                d1,
                d2,
                user_id=user_id,
                db_session=db if user_id else None
            )
            results.append({
                "pair": (d1, d2),
                "result": res
            })
            
        if not results:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid drug pairs found for analysis"
            )
            
        # If only one pair, return it directly (backward compatibility)
        if len(results) == 1:
            return results[0]["result"]
            
        # If multiple pairs, find the worst interaction
        # Priority: High > Moderate > Low > No Interaction
        risk_priority = {"High": 3, "Moderate": 2, "Low": 1, "None": 0}
        
        sorted_results = sorted(
            results,
            key=lambda x: (
                1 if x["result"]["interaction"] == "Yes" else 0,
                risk_priority.get(x["result"]["risk_level"], 0),
                x["result"]["confidence"]
            ),
            reverse=True
        )
        
        # The main result is the worst case
        worst_case = sorted_results[0]["result"]
        
        # Aggregate Explanations and Recommendations from all pairs if multiple interactions found
        if len(results) > 1:
            all_explanations = []
            all_recommendations = []
            
            # Use results (all pairs) or sorted_results (prioritized)
            # Using sorted_results puts highest risk first
            for item in sorted_results:
                d1, d2 = item["pair"]
                res = item["result"]
                
                # Only include detailed explanations if an interaction was found or if it's the primary pair
                # Actually, useful to see "No interaction" reasons too if available
                # But to avoid clutter, maybe focus on detected interactions?
                # Let's include all for completeness, labelled.
                
                # Append explanations
                for exp in res.get("explanations", []):
                    new_exp = exp.copy()
                    new_exp["explanation_text"] = f"[{d1} + {d2}] {new_exp['explanation_text']}"
                    all_explanations.append(new_exp)
                
                # Append recommendations
                for rec in res.get("recommendations", []):
                    new_rec = rec.copy()
                    new_rec["reason"] = f"[{d1} + {d2}] {new_rec['reason']}"
                    all_recommendations.append(new_rec)
            
            worst_case["explanations"] = all_explanations
            worst_case["recommendations"] = all_recommendations
        
        # Create summary of all interactions
        interaction_summaries = []
        found_interactions = [r for r in sorted_results if r["result"]["interaction"] == "Yes"]
        
        if found_interactions:
            for item in found_interactions:
                d1, d2 = item["pair"]
                risk = item["result"]["risk_level"]
                interaction_summaries.append(f"• {d1} + {d2}: {risk} Risk Detected")
            
            multi_summary = (
                f"Analyzed {len(pairs)} pairs from {len(unique_drugs)} drugs.\n"
                f"⚠️ DETECTED {len(found_interactions)} INTERACTION(S):\n" + 
                "\n".join(interaction_summaries)
            )
        else:
            multi_summary = (
                f"Analyzed {len(pairs)} pairs from {len(unique_drugs)} drugs.\n"
                "✅ No significant interactions detected among any combination."
            )
            
        # Update the main response
        worst_case["interaction_summary"] = multi_summary + "\n\n" + worst_case.get("interaction_summary", "")
        
        # Add note about multi-drug analysis
        if len(results) > 1:
            d1, d2 = sorted_results[0]["pair"]
            worst_case["warnings"] = (
                f"NOTE: Analysis covers all combinations of: {', '.join(unique_drugs)}.\n"
                f"Primary risk shown for: {d1} + {d2}."
            ) + "\n\n" + worst_case.get("warnings", "")
        
        # Add list of analyzed drugs for frontend
        worst_case["analyzed_drugs"] = unique_drugs
        
        return worst_case
        
    except HTTPException:
        raise


@router.post("/model/predict", tags=["Prediction"])
async def model_predict_adapter(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Compatibility adapter for the NEW frontend.
    
    This endpoint:
    - Delegates to the existing /predict logic for model inference
    - Maps the rich backend response into a stable, structured schema
      expected by the NEW frontend.
    
    Backend prediction remains the single source of truth for:
    - interaction
    - confidence
    - risk_level
    - severity
    """
    try:
        base_result = await predict_interaction(request, db, authorization)

        interaction = base_result.get("interaction")
        confidence = base_result.get("confidence")
        risk_level = base_result.get("risk_level")
        severity = base_result.get("severity")

        analyzed_drugs = base_result.get("analyzed_drugs", [])

        structured_features = {
            "analyzed_drugs": analyzed_drugs,
            "interaction": interaction,
            "risk_level": risk_level,
            "severity": severity,
            "confidence": confidence,
        }

        base_explanation = base_result.get("interaction_summary") or ""
        base_precautions = base_result.get("warnings") or ""
        base_recommendations = base_result.get("recommendations") or []

        # Get side_effect_overlap directly from Gemini response
        side_effect_overlap = base_result.get("side_effect_overlap", [])
        
        # If not available from Gemini, try to extract from explanations as fallback
        if not side_effect_overlap:
            explanations = base_result.get("explanations", []) or []
            raw_side_effect_texts = [
                str(exp.get("explanation_text", "")).strip()
                for exp in explanations
                if str(exp.get("explanation_type", "")).lower() == "side_effect"
            ]

            for text in raw_side_effect_texts:
                if not text:
                    continue
                parts = re.split(r"[;\n]", text)
                for part in parts:
                    label = part.strip(" .;-")
                    if label and len(label) > 2:
                        side_effect_overlap.append(label)

        return {
            "interaction": interaction,
            "confidence": confidence,
            "risk_level": risk_level,
            "severity": severity,
            "structured_features": structured_features,
            "base_explanation": base_explanation,
            "base_precautions": base_precautions,
            "base_recommendations": base_recommendations,
            "side_effect_overlap": side_effect_overlap,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model adapter error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model prediction adapter failed"
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/analyze-image", tags=["Prediction"])
async def analyze_prescription_image(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Analyze prescription images using Gemini Vision (supports 2-5 images)
    
    This endpoint:
    - Accepts 2-5 JPG or PNG images of prescriptions or medication packaging
    - Saves images to local uploads directory
    - Uses Gemini Vision to extract drug names from all images
    - Performs comprehensive interaction analysis on all detected drugs
    - Saves results to database if user is authenticated
    - Returns same schema as text-based prediction
    
    Independent from the deep learning model pipeline.
    
    Args:
        files: List of image files (JPG or PNG), minimum 2, maximum 5
        db: Database session
        authorization: Optional Bearer token
        
    Returns:
        Complete interaction analysis based on detected drugs from all images
    """
    try:
        # Validate file count
        if len(files) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Please upload at least 2 images. You uploaded {len(files)} image(s)."
            )
        
        if len(files) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum 5 images allowed. You uploaded {len(files)} images."
            )
        
        images_data = []
        total_size = 0
        
        # Process each file
        for idx, file in enumerate(files, 1):
            # Validate file type
            if not file.content_type in ["image/jpeg", "image/jpg", "image/png"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image {idx} has invalid file type. Only JPG and PNG images are supported."
                )
            
            # Read file contents
            contents = await file.read()
            
            # Validate individual file size (max 10MB)
            if len(contents) > 10 * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image {idx} is too large. Maximum size is 10MB per image."
                )
            
            total_size += len(contents)
            images_data.append(contents)
        
        logger.info(f"📸 Received {len(files)} image uploads (total: {total_size / 1024:.1f} KB)")
        
        # Save uploaded files to disk
        from utils.file_upload import save_multiple_files
        files_to_save = [(images_data[i], files[i].filename) for i in range(len(files))]
        saved_paths = save_multiple_files(files_to_save)
        
        if len(saved_paths) != len(files):
            logger.warning(f"⚠️ Only {len(saved_paths)}/{len(files)} files saved successfully")
        
        logger.info(f"💾 Saved {len(saved_paths)} images to disk")
        
        # Import vision service
        from services.gemini_vision_service import gemini_vision_service
        
        # Analyze multiple images
        result = gemini_vision_service.analyze_multiple_prescription_images(images_data)
        
        # Check for errors
        if "error_type" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Image analysis failed")
            )
        
        # Map to standard response format
        detected_drugs = result.get("detected_drugs", [])
        
        # Map confidence_level to numeric confidence
        confidence_map = {"High": 0.9, "Medium": 0.75, "Low": 0.6}
        confidence = confidence_map.get(result.get("confidence_level", "Medium"), 0.75)
        
        # Map to standard schema
        response = {
            "interaction": result.get("interaction", "Yes"),
            "confidence": confidence,
            "risk_level": result.get("risk_level", "Moderate"),
            "severity": result.get("severity", "Moderate"),
            "interaction_summary": result.get("explanation", ""),
            "warnings": result.get("precautions", ""),
            "side_effect_overlap": result.get("side_effect_overlap", []),
            "analyzed_drugs": detected_drugs,
            "total_images_analyzed": result.get("total_images_analyzed", len(files)),
            "successful_extractions": result.get("successful_extractions", 0),
            "image_results": result.get("image_results", []),
            "analysis_source": "gemini_vision_multi",
            "explanations": [
                {
                    "explanation_type": "image_analysis",
                    "explanation_text": result.get("explanation", ""),
                    "severity_contribution": result.get("severity", "Moderate")
                },
                {
                    "explanation_type": "side_effect",
                    "explanation_text": result.get("toxic_reactions", ""),
                    "severity_contribution": result.get("severity", "Moderate")
                },
                {
                    "explanation_type": "monitoring",
                    "explanation_text": result.get("symptoms", ""),
                    "severity_contribution": result.get("severity", "Moderate")
                }
            ],
            "recommendations": result.get("recommendations", []),
            "disclaimer": (
                "⚕️ MEDICAL DISCLAIMER: This image-based analysis is for educational and decision-support "
                "purposes only. It does NOT replace professional medical advice, diagnosis, "
                "or treatment. Always consult qualified healthcare professionals before "
                "making any medication decisions. Image quality and clarity can affect accuracy."
            )
        }
        
        # Save to database if user is authenticated
        user_id = None
        if authorization and authorization.startswith("Bearer "):
            try:
                token = authorization.replace("Bearer ", "")
                from utils.auth import decode_token
                payload = decode_token(token)
                user_id = payload.get("user_id")
                
                if user_id:
                    logger.info(f"👤 Authenticated user: {user_id}")
                    
                    # Import models
                    from models import InteractionHistory, Explanation, Recommendation
                    import json
                    
                    # For database, we need drug_1 and drug_2
                    # Use first two detected drugs, or duplicate if only one
                    drug_1 = detected_drugs[0] if len(detected_drugs) > 0 else "Unknown"
                    drug_2 = detected_drugs[1] if len(detected_drugs) > 1 else detected_drugs[0] if len(detected_drugs) > 0 else "Unknown"
                    
                    # Create interaction history record
                    interaction_record = InteractionHistory(
                        user_id=user_id,
                        drug_1=drug_1,
                        drug_2=drug_2,
                        interaction=response["interaction"],
                        confidence=response["confidence"],
                        risk_level=response["risk_level"],
                        severity=response["severity"],
                        analysis_mode="image",
                        image_paths=json.dumps(saved_paths),  # Store as JSON array
                        detected_drugs=json.dumps(detected_drugs)  # Store all detected drugs
                    )
                    db.add(interaction_record)
                    db.flush()  # Get the ID
                    
                    # Save explanations
                    for exp in response["explanations"]:
                        if exp.get("explanation_text"):
                            explanation_record = Explanation(
                                interaction_id=interaction_record.id,
                                explanation_type=exp.get("explanation_type", "general"),
                                explanation_text=exp.get("explanation_text", ""),
                                severity_contribution=exp.get("severity_contribution")
                            )
                            db.add(explanation_record)
                    
                    # Save recommendations
                    for rec in response["recommendations"]:
                        recommendation_record = Recommendation(
                            interaction_id=interaction_record.id,
                            alternative_drug=rec.get("alternative_drug", ""),
                            reason=rec.get("reason", ""),
                            safety_score=rec.get("safety_score"),
                            medical_condition=rec.get("medical_condition")
                        )
                        db.add(recommendation_record)
                    
                    db.commit()
                    logger.info(f"💾 Saved image analysis to database for user {user_id} (ID: {interaction_record.id})")
                    
            except Exception as e:
                logger.error(f"❌ Failed to save to database: {e}")
                db.rollback()
        
        logger.info(f"✅ Multi-image analysis complete: {len(detected_drugs)} drugs detected from {len(files)} images, {response['interaction']} interaction")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image analysis failed: {str(e)}"
        )


