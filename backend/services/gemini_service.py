
import os
import json
import logging
import time
import traceback
import google.generativeai as genai
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from backend/.env
backend_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(os.path.dirname(backend_dir), '.env')
load_dotenv(env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info(f"✅ Gemini API key loaded: {GEMINI_API_KEY[:20]}...")
else:
    logger.warning("⚠️ GEMINI_API_KEY not found in environment variables. Gemini service will use fallback.")

# Safety settings to prevent blocking of medical content
SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

class GeminiService:
    """
    Service to refine and validate DDI predictions using Google Gemini API.
    Acts as a refinement layer, NOT a decision engine.
    """

    def __init__(self):
        self.model = None
        if GEMINI_API_KEY:
            try:
                self.model = genai.GenerativeModel('gemini-3-flash-preview')
                logger.info("✓ Gemini Service initialized successfully")
            except Exception as e:
                logger.error(f"✗ Failed to initialize Gemini model: {e}")

    def validate_and_refine(self, prediction_data: Dict[str, Any], drug1: str, drug2: str) -> Dict[str, Any]:
        """
        Refines the deep learning prediction using Gemini.
        
        Args:
            prediction_data: The output from the DL model
            drug1: Name of first drug
            drug2: Name of second drug
            
        Returns:
            Refined dictionary with valid medical text
        """
        logger.info(f"🔄 Gemini refinement requested for {drug1} + {drug2}")
        
        # If Gemini is not configured, return original data with basic fallbacks
        if not self.model:
            logger.warning("⚠️ Gemini model not initialized, using local fallback")
            return self._apply_local_fallback(prediction_data, drug1, drug2)

        start_time = time.time()
        
        try:
            # Construct the prompt
            prompt = self._construct_prompt(prediction_data, drug1, drug2)
            print("DEBUG GEMINI: Prompt constructed, sending request...")
            logger.info(f"📝 Sending request to Gemini API...")
            
            # Call Gemini with timeout handling (simulated via thread or just simple call)
            # note: genai python client doesn't have a direct timeout param in generate_content easily exposed in all versions,
            # but we will rely on standard execution. For production, async/await or wrapping in a thread with timeout is better.
            # Here we wrap in try/except.
            
            response = self.model.generate_content(
                prompt,
                safety_settings=SAFETY_SETTINGS,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2, # Low temperature for factual consistency
                    max_output_tokens=1024,
                )
            )
            
            print(f"DEBUG GEMINI: Response received. Text len: {len(response.text) if response.text else 0}")
            
            # Parse response
            if response.text:
                cleaned_text = response.text.strip()
                logger.info(f"✅ Gemini response received ({len(cleaned_text)} chars)")
                
                # Remove markdown code blocks if present
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text.replace("```json", "").replace("```", "")
                elif cleaned_text.startswith("```"):
                    cleaned_text = cleaned_text.replace("```", "")
                
                refined_data = json.loads(cleaned_text)
                print("DEBUG GEMINI: JSON parsed successfully")
                print(f"DEBUG GEMINI: Output Keys: {list(refined_data.keys())}")
                
                # Merge and validate
                final_data = self._merge_results(prediction_data, refined_data)
                
                duration = time.time() - start_time
                print(f"DEBUG GEMINI: Complete! Explanations count: {len(final_data.get('explanations', []))}")
                
                return final_data
            else:
                print("DEBUG GEMINI: Empty response text")
                raise ValueError("Empty response from Gemini")

        except json.JSONDecodeError as e:
            print(f"DEBUG GEMINI: JSON Error: {e}")
            print(f"DEBUG GEMINI: Raw Response: {cleaned_text[:500]}") # Keep original slicing for raw response
            logger.error(f"❌ JSON parsing failed: {e}")
            return self._apply_local_fallback(prediction_data, drug1, drug2)
        except Exception as e:
            print(f"DEBUG GEMINI: General Error: {e}")
            traceback.print_exc()
            logger.error(f"❌ Gemini refinement failed: {e}. Using fallback.")
            return self._apply_local_fallback(prediction_data, drug1, drug2)

    def _construct_prompt(self, data: Dict[str, Any], drug1: str, drug2: str) -> str:
        """Constructs the strict prompt for Gemini"""
        
        # Simplify input for the prompt to ensure it focuses on what matters
        input_summary = {
            "drugs": [drug1, drug2],
            "predicted_interaction": data.get("interaction"),
            "predicted_confidence": data.get("confidence"),
            "predicted_risk": data.get("risk_level"),
            "predicted_severity": data.get("severity"),
            "current_summary": data.get("interaction_summary"),
            "wording_to_refine": data.get("explanations", [])
        }

        return f'''
You are a clinical AI refinement assistant. 
The Deep Learning model has already predicted the DDI (Drug-Drug Interaction) classification.

INPUT DATA:
{json.dumps(input_summary, indent=2)}

YOUR CORE TASK: FILL MISSING INFORMATION.
The input data contains fields with "Unknown", "not available", or generic text.
You MUST replace these with clinically accurate information based on your medical knowledge base.

SPECIFIC INSTRUCTIONS:
1. "explanations": 
   - IF THE INPUT LIST IS EMPTY: You MUST GENERATE 4 explanations covering: Drug Class Conflict, Side Effect Overlap, Pregnancy Risk, and Alcohol Interaction.
   - IF ITEMS EXIST: Check each. If an explanation says "information not available" or "Unknown", YOU MUST REPLACE IT with a valid medical explanation.
2. "recommendations": 
   - IF THE LIST IS EMPTY or GENERIC: GENERATE 2-3 specific alternative drugs or clinical management strategies based on the interaction mechanism.
3. "interaction_summary": Synthesize a professional clinical summary explaining WHY these drugs interact.
4. "side_effect_overlap": 
   - GENERATE a list of 3-6 specific overlapping side effects between {drug1} and {drug2}.
   - These should be concise clinical labels (e.g., "Dizziness", "Nausea", "QT Prolongation", "Bleeding Risk").
   - Base this on your medical knowledge of these specific drugs.
   - NEVER return an empty array. If no major overlaps exist, list common mild effects.

CRITICAL RULES:
1. DO NOT change the "interaction" (Yes/No), "confidence", "risk_level", or "severity" values. Keep them EXACTLY as provided.
2. NEVER return "No information available", "Unknown", or empty strings. Function as a clinical knowledge base to fill gaps.
3. Output MUST be valid JSON matching the structure below.

REQUIRED JSON STRUCTURE:
{{
  "interaction": "{data.get('interaction')}",
  "confidence": {data.get('confidence')},
  "risk_level": "{data.get('risk_level')}",
  "severity": "{data.get('severity')}",
  "interaction_summary": "Refined clinical summary...",
  "warnings": "Refined warning text...",
  "side_effect_overlap": ["Side Effect 1", "Side Effect 2", "Side Effect 3"],
  "explanations": [
    {{
      "explanation_type": "drug_class", 
      "explanation_text": "Detailed comparison of drug classes...",
      "severity_contribution": "Low/Moderate/High"
    }},
    {{
      "explanation_type": "side_effect",
      "explanation_text": "Analysis of potential overlapping side effects...",
      "severity_contribution": "Low/Moderate/High"
    }},
    {{
      "explanation_type": "pregnancy",
      "explanation_text": "Specific pregnancy safety advice...",
      "severity_contribution": "Low/Moderate/High"
    }},
    {{
      "explanation_type": "alcohol",
      "explanation_text": "Specific alcohol interaction advice...",
      "severity_contribution": "Low/Moderate/High"
    }}
  ],
  "recommendations": [
    {{
       "alternative_drug": "Specific Drug Name",
       "reason": "Clinical reason for alternative...",
       "safety_score": 0.9,
       "medical_condition": "Reason for use"
    }}
  ]
}}
'''

    def _merge_results(self, original: Dict[str, Any], refined: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merges Gemini results with original, STRICTLY preserving classification.
        """
        merged = original.copy()
        
        # 1. Enforce Original Classification (Security Rule)
        merged["interaction"] = original["interaction"]
        merged["confidence"] = original["confidence"]
        merged["risk_level"] = original["risk_level"]
        merged["severity"] = original["severity"]
        
        # 2. Update Text Fields (Refinement)
        if refined.get("interaction_summary"):
            merged["interaction_summary"] = refined["interaction_summary"]
            
        if refined.get("warnings"):
            merged["warnings"] = refined["warnings"]
            
        # 3. Update Explanations - INTELLIGENT MERGE
        # Replace "Unknown" original explanations with Gemini's detailed ones
        if refined.get("explanations") and isinstance(refined["explanations"], list):
            # Create a map of Gemini explanations by type
            gemini_exps = {
                exp.get("explanation_type", "general").lower(): exp 
                for exp in refined["explanations"]
            }
            
            # Start with original explanations, but replace if Gemini has something better
            final_explanations = []
            
            # We want to cover all 4 main types: drug_class, side_effect, pregnancy, alcohol
            required_types = ["drug_class", "side_effect", "pregnancy", "alcohol"]
            
            # Map existing originals
            original_map = {
                exp.get("explanation_type", "general").lower(): exp 
                for exp in original.get("explanations", [])
            }
            
            for exp_type in required_types:
                orig_exp = original_map.get(exp_type)
                gemini_exp = gemini_exps.get(exp_type)
                
                # Log for debugging
                if not gemini_exp:
                     logger.warning(f"⚠️ Gemini missing explanation for type: {exp_type}. Available types: {list(gemini_exps.keys())}")
                
                # Decision logic: Use Gemini if Original is missing or "Unknown"/"not available"
                use_gemini = False
                if not orig_exp:
                    use_gemini = True
                else:
                    text = orig_exp.get("explanation_text", "").lower()
                    if "unknown" in text or "not available" in text or "no specific" in text:
                        use_gemini = True
                
                if use_gemini and gemini_exp:
                    final_explanations.append({
                        "explanation_type": exp_type,
                        "explanation_text": gemini_exp.get("explanation_text", "Detailed information provided by clinical AI."),
                        "severity_contribution": gemini_exp.get("severity_contribution", "Low")
                    })
                elif orig_exp:
                     final_explanations.append(orig_exp)
                elif gemini_exp:
                    # If original didn't even have this type, add Gemini's
                    final_explanations.append({
                        "explanation_type": exp_type,
                        "explanation_text": gemini_exp.get("explanation_text", "Detailed information provided by clinical AI."),
                        "severity_contribution": gemini_exp.get("severity_contribution", "Low")
                    })
            
            # Add any other types Gemini might have added
            for g_type, g_exp in gemini_exps.items():
                if g_type not in required_types:
                    final_explanations.append({
                        "explanation_type": g_exp.get("explanation_type", "general"),
                        "explanation_text": g_exp.get("explanation_text"),
                        "severity_contribution": g_exp.get("severity_contribution", "Low")
                    })
            
            merged["explanations"] = final_explanations
                
        # 4. Update Side Effect Overlap
        if refined.get("side_effect_overlap") and isinstance(refined["side_effect_overlap"], list):
            # Filter out empty strings and ensure we have valid side effects
            side_effects = [se.strip() for se in refined["side_effect_overlap"] if se and se.strip()]
            if side_effects:
                merged["side_effect_overlap"] = side_effects
                logger.info(f"✅ Added {len(side_effects)} side effects from Gemini")
        
        # 5. Update Recommendations
        if refined.get("recommendations") and isinstance(refined["recommendations"], list):
            valid_recs = []
            for rec in refined["recommendations"]:
                # Handle both string recommendations and dict structure
                if isinstance(rec, str):
                    valid_recs.append({
                        "alternative_drug": "Consult Doctor",
                        "reason": rec,
                        "safety_score": 0.0,
                        "medical_condition": "N/A"
                    })
                elif isinstance(rec, dict):
                    valid_recs.append({
                        "alternative_drug": rec.get("alternative_drug", "Alternative"),
                        "reason": rec.get("reason", "Better safety profile."),
                        "safety_score": rec.get("safety_score", 0.8),
                        "medical_condition": rec.get("medical_condition", "N/A")
                    })
            if valid_recs:
                merged["recommendations"] = valid_recs
        
        return merged

    def _apply_local_fallback(self, data: Dict[str, Any], drug1: str, drug2: str) -> Dict[str, Any]:
        """
        Ensures no empty fields if Gemini fails.
        """
        logger.info(f"🔧 Applying local fallback for {drug1} + {drug2}")
        fallback = data.copy()
        
        fields_filled = []
        
        if not fallback.get("interaction_summary"):
             fallback["interaction_summary"] = (
                 f"The deep learning model has analyzed the properties of {drug1} and {drug2}. "
                 f"Based on structural similarity and known patterns, the interaction risk is classified as {fallback.get('risk_level', 'Unknown')}."
             )
             fields_filled.append("interaction_summary")
             
        if not fallback.get("warnings"):
            fallback["warnings"] = (
                f"Concurrent use of {drug1} and {drug2} should be monitored. "
                "Consult a healthcare professional for specific advice."
            )
            fields_filled.append("warnings")
            
        if not fallback.get("explanations") or len(fallback.get("explanations", [])) == 0:
            fallback["explanations"] = [{
                "explanation_type": "Precautionary",
                "explanation_text": "Detailed interaction mechanism is not currently available in the database, but caution is advised based on predictive modeling.",
                "severity_contribution": fallback.get("severity", "Unknown")
            }]
            fields_filled.append("explanations")
            
        if not fallback.get("recommendations") or len(fallback.get("recommendations", [])) == 0:
            fallback["recommendations"] = [{
                "alternative_drug": "Consult Healthcare Provider",
                "reason": "Please consult a pharmacist or physician for suitable alternatives based on your specific medical condition.",
                "safety_score": 0.0,
                "medical_condition": "General"
            }]
            fields_filled.append("recommendations")
        
        if not fallback.get("side_effect_overlap") or len(fallback.get("side_effect_overlap", [])) == 0:
            # Provide generic common side effects as fallback
            fallback["side_effect_overlap"] = [
                "Dizziness",
                "Nausea",
                "Headache",
                "Fatigue"
            ]
            fields_filled.append("side_effect_overlap")
        
        if fields_filled:
            logger.info(f"📝 Fallback filled fields: {', '.join(fields_filled)}")
            
        return fallback

# Singleton instance
gemini_service = GeminiService()
