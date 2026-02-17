"""
Test script to diagnose and verify the Explainable AI explanations issue
"""

import sys
import os

# Add backend to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

print("=" * 80)
print("EXPLAINABLE AI DIAGNOSTIC TEST")
print("=" * 80)

# Test 1: Check if datasets exist
print("\n[TEST 1] Checking Dataset Files...")
project_root = os.path.dirname(backend_dir)
datasets_dir = os.path.join(project_root, "datasets")

side_effects_path = os.path.join(datasets_dir, "drugs_side_effects_drugs_com.csv")
interactions_path = os.path.join(datasets_dir, "db_drug_interactions.csv")

print(f"  Side Effects CSV: {'✓ Found' if os.path.exists(side_effects_path) else '✗ NOT FOUND'}")
print(f"    Path: {side_effects_path}")
print(f"  Interactions CSV: {'✓ Found' if os.path.exists(interactions_path) else '✗ NOT FOUND'}")
print(f"    Path: {interactions_path}")

# Test 2: Load Explainable AI Service
print("\n[TEST 2] Loading Explainable AI Service...")
try:
    from services.explainable_ai_service import explainable_ai_service
    print("  ✓ Service imported successfully")
    
    # Force load data
    explainable_ai_service.load_data()
    print(f"  Data loaded: {explainable_ai_service.loaded}")
    
    if explainable_ai_service.side_effects_data is not None:
        print(f"  Drugs in database: {len(explainable_ai_service.side_effects_data)}")
        print(f"  Sample drugs: {list(explainable_ai_service.side_effects_data['drug_name'].head(5))}")
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test explanation generation
print("\n[TEST 3] Testing Explanation Generation...")
try:
    # Test with common drugs
    test_drugs = [
        ("Aspirin", "Warfarin"),
        ("Ibuprofen", "Lisinopril"),
        ("Metformin", "Insulin")
    ]
    
    for drug1, drug2 in test_drugs:
        print(f"\n  Testing: {drug1} + {drug2}")
        explanations = explainable_ai_service.generate_comprehensive_explanation(
            drug1, drug2, 0.85
        )
        
        print(f"    Generated {len(explanations)} explanations:")
        for exp in explanations:
            exp_type = exp.get('explanation_type', 'unknown')
            severity = exp.get('severity_contribution', 'Unknown')
            text_preview = exp.get('explanation_text', '')[:80] + "..."
            
            # Check if it's a placeholder/unknown
            is_unknown = any(keyword in text_preview.lower() 
                           for keyword in ['unknown', 'not available', 'no specific'])
            status = "⚠️ PLACEHOLDER" if is_unknown else "✓ VALID"
            
            print(f"      [{status}] {exp_type}: {severity}")
            print(f"        {text_preview}")
        
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check Gemini Service
print("\n[TEST 4] Checking Gemini Service...")
try:
    from services.gemini_service import gemini_service
    print(f"  Gemini model initialized: {gemini_service.model is not None}")
    
    from dotenv import load_dotenv
    load_dotenv(os.path.join(backend_dir, '.env'))
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        print(f"  API Key found: {api_key[:20]}...")
    else:
        print("  ⚠️ WARNING: GEMINI_API_KEY not found in .env")
        print("     Explanations will use fallback mode")
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Full Integration Test
print("\n[TEST 5] Full Integration Test (DDI Service)...")
try:
    from services.ddi_service import ddi_service
    
    # Load model
    print("  Loading model...")
    ddi_service.load_model()
    print(f"  Model loaded: {ddi_service.model_loaded}")
    
    # Make a prediction
    print("\n  Making prediction for: Aspirin + Warfarin")
    result = ddi_service.predict_interaction("Aspirin", "Warfarin")
    
    print(f"  Interaction: {result.get('interaction')}")
    print(f"  Risk Level: {result.get('risk_level')}")
    print(f"  Confidence: {result.get('confidence')}")
    
    explanations = result.get('explanations', [])
    print(f"\n  Explanations ({len(explanations)}):")
    for i, exp in enumerate(explanations, 1):
        exp_type = exp.get('explanation_type', 'unknown')
        text = exp.get('explanation_text', '')
        severity = exp.get('severity_contribution', 'Unknown')
        
        # Check if it's meaningful
        is_meaningful = not any(keyword in text.lower() 
                               for keyword in ['unknown', 'not available', 'no specific'])
        status = "✓" if is_meaningful else "⚠️"
        
        print(f"    {status} [{i}] {exp_type} ({severity})")
        print(f"        {text[:100]}...")
    
    recommendations = result.get('recommendations', [])
    print(f"\n  Recommendations ({len(recommendations)}):")
    for i, rec in enumerate(recommendations, 1):
        alt_drug = rec.get('alternative_drug', 'N/A')
        reason = rec.get('reason', '')[:80]
        print(f"    [{i}] {alt_drug}")
        print(f"        {reason}...")
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
