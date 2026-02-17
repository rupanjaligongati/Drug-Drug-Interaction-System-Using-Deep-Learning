
import sys
import os
import json
import logging

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ddi_service import ddi_service

def run_test():
    print("-" * 50)
    print("🧪 STARTING PREDICTION FORCE TEST")
    print("-" * 50)

    try:
        # load model first
        print("📥 Loading Model...")
        ddi_service.load_model()
        print("✅ Model Loaded!")

        drug1 = "Aspirin"
        drug2 = "Warfarin"
        
        print(f"🔬 Predicting: {drug1} + {drug2}")
        
        # Call predict_interaction without DB session (so no saving, just logic check)
        # This will trigger Gemini refinement if configured correctly
        result = ddi_service.predict_interaction(drug1, drug2)
        
        print("\n📊 RESULT SUMMARY:")
        print(f"Interaction: {result.get('interaction')}")
        print(f"Risk Level: {result.get('risk_level')}")
        
        print("\n📝 EXPLANATIONS:")
        explanations = result.get('explanations', [])
        if not explanations:
            print("❌ NO EXPLANATIONS FOUND!")
        else:
            for exp in explanations:
                print(f" - [{exp.get('explanation_type')}]: {exp.get('explanation_text')}")
                
        print("\n💊 RECOMMENDATIONS:")
        recommendations = result.get('recommendations', [])
        if not recommendations:
            print("❌ NO RECOMMENDATIONS FOUND!")
        else:
            for rec in recommendations:
                print(f" - Alternative: {rec.get('alternative_drug')}")
                print(f"   Reason: {rec.get('reason')}")
                
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
