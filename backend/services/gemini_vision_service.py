"""
Gemini Vision Service for Image-Based Drug Interaction Analysis
Handles prescription image analysis and drug name extraction
"""

import os
import json
import logging
import base64
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from PIL import Image
import io

# Load environment variables
backend_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(os.path.dirname(backend_dir), '.env')
load_dotenv(env_path)

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("✅ Gemini Vision API configured")
else:
    logger.warning("⚠️ GEMINI_API_KEY not found. Vision service will fail.")

# Safety settings
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]


class GeminiVisionService:
    """Service for analyzing prescription images using Gemini Vision"""
    
    def __init__(self):
        self.model = None
        if GEMINI_API_KEY:
            try:
                # Use gemini-3-flash-preview which supports vision/image analysis
                self.model = genai.GenerativeModel('gemini-3-flash-preview')
                logger.info("✓ Gemini Vision Service initialized with gemini-3-flash-preview")
            except Exception as e:
                logger.error(f"✗ Failed to initialize Gemini Vision: {e}")
    
    def analyze_multiple_prescription_images(self, images_data: List[bytes]) -> Dict[str, Any]:
        """
        Analyze multiple prescription images and extract drug names, then perform interaction analysis.
        
        Args:
            images_data: List of raw image bytes (JPG or PNG), minimum 2, maximum 5
            
        Returns:
            Complete interaction analysis with detected drugs from all images
        """
        if not self.model:
            return {
                "error_type": "service_unavailable",
                "message": "Gemini Vision service is not available. Please check API configuration."
            }
        
        # Validate image count
        if len(images_data) < 2:
            return {
                "error_type": "insufficient_images",
                "message": "Please upload at least 2 images for analysis.",
                "images_provided": len(images_data)
            }
        
        if len(images_data) > 5:
            return {
                "error_type": "too_many_images",
                "message": "Maximum 5 images allowed. Please select up to 5 images.",
                "images_provided": len(images_data)
            }
        
        try:
            all_detected_drugs = []
            image_results = []
            
            # Step 1: Extract drugs from each image
            logger.info(f"🔍 Analyzing {len(images_data)} prescription images...")
            
            for idx, image_data in enumerate(images_data, 1):
                logger.info(f"📸 Processing image {idx}/{len(images_data)}...")
                drug_extraction_result = self._extract_drugs_from_image(image_data)
                
                if "error_type" in drug_extraction_result:
                    logger.warning(f"⚠️ Image {idx} extraction failed: {drug_extraction_result.get('message')}")
                    image_results.append({
                        "image_number": idx,
                        "status": "failed",
                        "detected_drugs": [],
                        "error": drug_extraction_result.get("message")
                    })
                    continue
                
                detected_drugs = drug_extraction_result.get("detected_drugs", [])
                all_detected_drugs.extend(detected_drugs)
                
                image_results.append({
                    "image_number": idx,
                    "status": "success",
                    "detected_drugs": detected_drugs,
                    "confidence": drug_extraction_result.get("confidence", "medium"),
                    "image_quality": drug_extraction_result.get("image_quality", "moderate")
                })
                
                logger.info(f"✅ Image {idx}: Detected {len(detected_drugs)} drugs - {', '.join(detected_drugs)}")
            
            # Remove duplicates while preserving order
            unique_drugs = []
            seen = set()
            for drug in all_detected_drugs:
                drug_lower = drug.lower()
                if drug_lower not in seen:
                    seen.add(drug_lower)
                    unique_drugs.append(drug)
            
            logger.info(f"📊 Total unique drugs detected: {len(unique_drugs)} - {', '.join(unique_drugs)}")
            
            # Validate minimum drugs detected
            if len(unique_drugs) < 2:
                return {
                    "error_type": "insufficient_visual_data",
                    "message": f"Only {len(unique_drugs)} unique drug(s) detected across all images. Please upload clearer images showing at least 2 different medications.",
                    "detected_drugs": unique_drugs,
                    "image_results": image_results
                }
            
            # Step 2: Perform full interaction analysis on all detected drugs
            logger.info("🔬 Performing comprehensive interaction analysis...")
            analysis_result = self._analyze_drug_interactions(unique_drugs)
            
            # Merge results
            final_result = {
                **analysis_result,
                "detected_drugs": unique_drugs,
                "total_images_analyzed": len(images_data),
                "successful_extractions": sum(1 for r in image_results if r["status"] == "success"),
                "image_results": image_results,
                "analysis_source": "gemini_vision_multi"
            }
            
            logger.info(f"✅ Multi-image analysis complete: {final_result.get('interaction')} interaction")
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Multi-image analysis failed: {e}", exc_info=True)
            return {
                "error_type": "analysis_failed",
                "message": f"Multi-image analysis encountered an error: {str(e)}"
            }
    
    def analyze_prescription_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze prescription image and extract drug names, then perform interaction analysis.
        
        Args:
            image_data: Raw image bytes (JPG or PNG)
            
        Returns:
            Complete interaction analysis with detected drugs
        """
        if not self.model:
            return {
                "error_type": "service_unavailable",
                "message": "Gemini Vision service is not available. Please check API configuration."
            }
        
        try:
            # Step 1: Extract drug names from image
            logger.info("🔍 Analyzing prescription image...")
            drug_extraction_result = self._extract_drugs_from_image(image_data)
            
            if "error_type" in drug_extraction_result:
                return drug_extraction_result
            
            detected_drugs = drug_extraction_result.get("detected_drugs", [])
            
            if len(detected_drugs) < 2:
                return {
                    "error_type": "insufficient_visual_data",
                    "message": "Unable to clearly detect at least two valid drug names. Please upload a clearer image showing multiple medications.",
                    "detected_drugs": detected_drugs
                }
            
            logger.info(f"✅ Detected {len(detected_drugs)} drugs: {', '.join(detected_drugs)}")
            
            # Step 2: Perform full interaction analysis
            logger.info("🔬 Performing interaction analysis...")
            analysis_result = self._analyze_drug_interactions(detected_drugs)
            
            # Merge results
            final_result = {
                **analysis_result,
                "detected_drugs": detected_drugs,
                "analysis_source": "gemini_vision"
            }
            
            logger.info(f"✅ Image analysis complete: {final_result.get('interaction')} interaction")
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Image analysis failed: {e}", exc_info=True)
            return {
                "error_type": "analysis_failed",
                "message": f"Image analysis encountered an error: {str(e)}"
            }
    
    def _extract_drugs_from_image(self, image_data: bytes) -> Dict[str, Any]:
        """Extract drug names from prescription image"""
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Construct extraction prompt
            extraction_prompt = """
You are a medical AI assistant analyzing a prescription image or medication packaging.

TASK: Extract ALL visible drug names from this image.

STRICT RULES:
1. Only extract drug names that are CLEARLY VISIBLE in the image
2. Do NOT guess or hallucinate drug names
3. Do NOT fabricate brand names
4. Extract both generic and brand names if visible
5. Return at least 2 drug names if possible
6. If fewer than 2 drugs are clearly visible, return what you can see

OUTPUT FORMAT (JSON only):
{
  "detected_drugs": ["Drug1", "Drug2", "Drug3"],
  "confidence": "high/medium/low",
  "image_quality": "clear/moderate/poor"
}

Return ONLY valid JSON. No additional text.
"""
            
            response = self.model.generate_content(
                [extraction_prompt, image],
                safety_settings=SAFETY_SETTINGS,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=512,
                )
            )
            
            if not response.text:
                return {
                    "error_type": "extraction_failed",
                    "message": "Unable to extract text from image"
                }
            
            # Parse JSON response
            cleaned_text = response.text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text.replace("```json", "").replace("```", "")
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text.replace("```", "")
            
            result = json.loads(cleaned_text)
            
            # Validate result
            if not isinstance(result.get("detected_drugs"), list):
                return {
                    "error_type": "invalid_response",
                    "message": "Invalid response format from vision model"
                }
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return {
                "error_type": "parsing_failed",
                "message": "Failed to parse drug extraction results"
            }
        except Exception as e:
            logger.error(f"Drug extraction error: {e}")
            return {
                "error_type": "extraction_failed",
                "message": str(e)
            }
    
    def _analyze_drug_interactions(self, drugs: List[str]) -> Dict[str, Any]:
        """Perform comprehensive drug interaction analysis using Gemini"""
        try:
            drugs_text = ", ".join(drugs)
            
            analysis_prompt = f"""
You are a clinical pharmacology AI analyzing drug-drug interactions.

DRUGS TO ANALYZE: {drugs_text}

TASK: Provide a comprehensive drug interaction analysis.

CLASSIFICATION REQUIREMENTS:
1. interaction: "Yes" or "No" (whether clinically significant interaction exists)
2. confidence_level: "High", "Medium", or "Low" (your reasoning confidence)
3. risk_level: "Low", "Moderate", or "High" (clinical risk if interaction exists)
4. severity: "Mild", "Moderate", "Severe", or "Toxic" (potential severity)

CONTENT REQUIREMENTS:
- explanation: Detailed mechanism of interaction (2-3 sentences)
- high_risk_drug: Which drug(s) pose the highest risk in this combination
- toxic_reactions: Specific toxic reactions that may occur
- symptoms: Clinical symptoms to monitor for
- precautions: Specific precautions and monitoring recommendations
- side_effect_overlap: Array of 3-6 overlapping side effects
- recommendations: Array of 2-3 alternative drug suggestions with reasons

CRITICAL RULES:
1. Base analysis on established pharmacological knowledge
2. NEVER leave any field empty or null
3. NEVER return "No Data" or "Unknown"
4. If limited data exists, provide safe generalized clinical guidance
5. Maintain professional medical terminology
6. Be specific and actionable

OUTPUT FORMAT (JSON only):
{{
  "interaction": "Yes/No",
  "confidence_level": "High/Medium/Low",
  "risk_level": "Low/Moderate/High",
  "severity": "Mild/Moderate/Severe/Toxic",
  "explanation": "Detailed interaction mechanism...",
  "high_risk_drug": "Drug name or combination",
  "toxic_reactions": "Specific toxic reactions...",
  "symptoms": "Clinical symptoms to monitor...",
  "precautions": "Monitoring and management recommendations...",
  "side_effect_overlap": ["Effect1", "Effect2", "Effect3"],
  "recommendations": [
    {{
      "alternative_drug": "Drug Name",
      "reason": "Clinical rationale...",
      "safety_score": 0.85,
      "medical_condition": "Indication"
    }}
  ]
}}

Return ONLY valid JSON. No additional text.
"""
            
            response = self.model.generate_content(
                analysis_prompt,
                safety_settings=SAFETY_SETTINGS,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=2048,
                )
            )
            
            if not response.text:
                return self._get_fallback_analysis(drugs)
            
            # Parse JSON response
            cleaned_text = response.text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text.replace("```json", "").replace("```", "")
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text.replace("```", "")
            
            result = json.loads(cleaned_text)
            
            # Validate and ensure no empty fields
            result = self._validate_and_fill_analysis(result, drugs)
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Analysis JSON parsing error: {e}")
            return self._get_fallback_analysis(drugs)
        except Exception as e:
            logger.error(f"Interaction analysis error: {e}")
            return self._get_fallback_analysis(drugs)
    
    def _validate_and_fill_analysis(self, result: Dict[str, Any], drugs: List[str]) -> Dict[str, Any]:
        """Ensure all required fields are present and non-empty"""
        drugs_text = " + ".join(drugs)
        
        # Required fields with fallbacks
        defaults = {
            "interaction": result.get("interaction", "Yes"),
            "confidence_level": result.get("confidence_level", "Medium"),
            "risk_level": result.get("risk_level", "Moderate"),
            "severity": result.get("severity", "Moderate"),
            "explanation": result.get("explanation") or f"The combination of {drugs_text} requires clinical monitoring due to potential pharmacological interactions.",
            "high_risk_drug": result.get("high_risk_drug") or drugs[0],
            "toxic_reactions": result.get("toxic_reactions") or "Potential additive effects may increase side effect burden.",
            "symptoms": result.get("symptoms") or "Monitor for increased drowsiness, dizziness, or changes in vital signs.",
            "precautions": result.get("precautions") or f"Close monitoring recommended when using {drugs_text} concurrently. Consult healthcare provider.",
            "side_effect_overlap": result.get("side_effect_overlap") or ["Dizziness", "Nausea", "Headache", "Fatigue"],
            "recommendations": result.get("recommendations") or [
                {
                    "alternative_drug": "Consult Physician",
                    "reason": "Professional evaluation recommended for safer alternatives based on patient profile.",
                    "safety_score": 0.0,
                    "medical_condition": "General"
                }
            ]
        }
        
        return defaults
    
    def _get_fallback_analysis(self, drugs: List[str]) -> Dict[str, Any]:
        """Provide safe fallback analysis when Gemini fails"""
        drugs_text = " + ".join(drugs)
        
        return {
            "interaction": "Yes",
            "confidence_level": "Low",
            "risk_level": "Moderate",
            "severity": "Moderate",
            "explanation": f"Analysis of {drugs_text} suggests potential interaction. Professional medical consultation is strongly recommended.",
            "high_risk_drug": drugs[0] if drugs else "Unknown",
            "toxic_reactions": "Potential for additive pharmacological effects. Monitor closely.",
            "symptoms": "Watch for unusual drowsiness, dizziness, changes in heart rate, or other unexpected symptoms.",
            "precautions": f"Consult a healthcare professional before combining {drugs_text}. Regular monitoring advised.",
            "side_effect_overlap": ["Dizziness", "Nausea", "Fatigue", "Headache"],
            "recommendations": [
                {
                    "alternative_drug": "Healthcare Provider Consultation",
                    "reason": "Professional evaluation needed to determine safer alternatives for your specific condition.",
                    "safety_score": 0.0,
                    "medical_condition": "General"
                }
            ]
        }


# Singleton instance
gemini_vision_service = GeminiVisionService()
