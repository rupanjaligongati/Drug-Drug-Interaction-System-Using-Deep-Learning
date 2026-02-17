"""
Explainable AI Service
Provides explanations for drug interactions based on:
- Drug class conflicts
- Side effect overlaps
- Pregnancy category risks
- Alcohol interaction warnings
"""

import pandas as pd
import logging
from typing import List, Dict, Tuple
import os

logger = logging.getLogger(__name__)


class ExplainableAIService:
    """Service for generating explanations for drug interactions"""
    
    def __init__(self):
        self.side_effects_data = None
        self.interaction_data = None
        self.loaded = False
    
    def load_data(self):
        """Load drug metadata for explanations"""
        try:
            # Get the project root directory (3 levels up from services/)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Load side effects dataset
            side_effects_path = os.path.join(project_root, "datasets", "drugs_side_effects_drugs_com.csv")
            if not os.path.exists(side_effects_path):
                logger.warning(f"⚠️ Side effects dataset not found at {side_effects_path}")
                self.loaded = False
                return
                
            self.side_effects_data = pd.read_csv(side_effects_path)
            
            # Load interaction dataset
            interaction_path = os.path.join(project_root, "datasets", "db_drug_interactions.csv")
            if not os.path.exists(interaction_path):
                logger.warning(f"⚠️ Interaction dataset not found at {interaction_path}")
            else:
                self.interaction_data = pd.read_csv(interaction_path)
            
            # Clean column names
            self.side_effects_data.columns = self.side_effects_data.columns.str.strip()
            if self.interaction_data is not None:
                self.interaction_data.columns = self.interaction_data.columns.str.strip()
            
            # Fill NaN values
            self.side_effects_data = self.side_effects_data.fillna("Unknown")
            
            self.loaded = True
            logger.info(f"✓ Explainable AI data loaded successfully ({len(self.side_effects_data)} drugs)")
            
        except Exception as e:
            logger.error(f"✗ Failed to load explainable AI data: {e}")
            self.loaded = False
    
    def get_drug_info(self, drug_name: str) -> Dict:
        """Get comprehensive drug information"""
        if not self.loaded:
            return {}
        
        # Search for drug (case-insensitive)
        drug_info = self.side_effects_data[
            self.side_effects_data['drug_name'].str.lower() == drug_name.lower()
        ]
        
        if drug_info.empty:
            return {}
        
        drug_info = drug_info.iloc[0]
        
        return {
            'drug_name': drug_info.get('drug_name', 'Unknown'),
            'medical_condition': drug_info.get('medical_condition', 'Unknown'),
            'side_effects': drug_info.get('side_effects', 'Unknown'),
            'drug_classes': drug_info.get('drug_classes', 'Unknown'),
            'pregnancy_category': drug_info.get('pregnancy_category', 'Unknown'),
            'alcohol': drug_info.get('alcohol', 'Unknown'),
            'related_drugs': drug_info.get('related_drugs', 'Unknown'),
            'rating': drug_info.get('rating', 0)
        }
    
    def analyze_drug_class_conflict(self, drug1: str, drug2: str) -> Tuple[bool, str, str]:
        """
        Analyze if drugs have conflicting drug classes
        
        Returns:
            (has_conflict, explanation, severity)
        """
        info1 = self.get_drug_info(drug1)
        info2 = self.get_drug_info(drug2)
        
        if not info1 or not info2:
            return False, "Drug class information not available", "Unknown"
        
        class1 = str(info1.get('drug_classes', 'Unknown'))
        class2 = str(info2.get('drug_classes', 'Unknown'))
        
        # High-risk drug class combinations
        high_risk_combinations = [
            ('anticoagulant', 'nsaid'),
            ('anticoagulant', 'antiplatelet'),
            ('ssri', 'maoi'),
            ('benzodiazepine', 'opioid'),
            ('ace inhibitor', 'potassium-sparing diuretic'),
        ]
        
        class1_lower = class1.lower()
        class2_lower = class2.lower()
        
        for combo in high_risk_combinations:
            if (combo[0] in class1_lower and combo[1] in class2_lower) or \
               (combo[1] in class1_lower and combo[0] in class2_lower):
                explanation = f"⚠️ Drug Class Conflict: {drug1} ({class1}) and {drug2} ({class2}) belong to drug classes that are known to interact dangerously."
                return True, explanation, "High"
        
        # Check if same class (may have additive effects)
        if class1_lower != 'unknown' and class1_lower == class2_lower:
            explanation = f"⚡ Same Drug Class: Both drugs belong to {class1}, which may cause additive effects or increased side effects."
            return True, explanation, "Moderate"
        
        return False, f"Drug classes: {drug1} ({class1}), {drug2} ({class2})", "Low"
    
    def analyze_side_effect_overlap(self, drug1: str, drug2: str) -> Tuple[bool, str, str]:
        """
        Analyze overlapping side effects
        
        Returns:
            (has_overlap, explanation, severity)
        """
        info1 = self.get_drug_info(drug1)
        info2 = self.get_drug_info(drug2)
        
        if not info1 or not info2:
            return False, "Side effect information not available", "Unknown"
        
        se1 = str(info1.get('side_effects', '')).lower()
        se2 = str(info2.get('side_effects', '')).lower()
        
        # Critical side effects to watch for
        critical_effects = [
            'bleeding', 'hemorrhage', 'seizure', 'cardiac arrest',
            'respiratory depression', 'liver failure', 'kidney failure'
        ]
        
        moderate_effects = [
            'dizziness', 'drowsiness', 'nausea', 'headache',
            'fatigue', 'confusion', 'low blood pressure'
        ]
        
        # Check for critical overlaps
        critical_overlaps = []
        for effect in critical_effects:
            if effect in se1 and effect in se2:
                critical_overlaps.append(effect)
        
        if critical_overlaps:
            explanation = f"🚨 Critical Side Effect Overlap: Both drugs can cause {', '.join(critical_overlaps)}. Combined use significantly increases risk."
            return True, explanation, "High"
        
        # Check for moderate overlaps
        moderate_overlaps = []
        for effect in moderate_effects:
            if effect in se1 and effect in se2:
                moderate_overlaps.append(effect)
        
        if moderate_overlaps:
            explanation = f"⚠️ Side Effect Overlap: Both drugs may cause {', '.join(moderate_overlaps[:3])}. Monitor for increased severity."
            return True, explanation, "Moderate"
        
        return False, "No significant side effect overlap detected", "Low"
    
    def analyze_pregnancy_risk(self, drug1: str, drug2: str) -> Tuple[bool, str, str]:
        """
        Analyze pregnancy category risks
        
        Returns:
            (has_risk, explanation, severity)
        """
        info1 = self.get_drug_info(drug1)
        info2 = self.get_drug_info(drug2)
        
        if not info1 or not info2:
            return False, "Pregnancy category information not available", "Unknown"
        
        preg1 = str(info1.get('pregnancy_category', 'Unknown'))
        preg2 = str(info2.get('pregnancy_category', 'Unknown'))
        
        high_risk_categories = ['D', 'X']
        moderate_risk_categories = ['C']
        
        risks = []
        if preg1 in high_risk_categories:
            risks.append(f"{drug1} (Category {preg1})")
        if preg2 in high_risk_categories:
            risks.append(f"{drug2} (Category {preg2})")
        
        if risks:
            explanation = f"🤰 Pregnancy Warning: {', '.join(risks)} - High risk during pregnancy. Avoid use if pregnant or planning pregnancy."
            return True, explanation, "High"
        
        moderate_risks = []
        if preg1 in moderate_risk_categories:
            moderate_risks.append(f"{drug1} (Category {preg1})")
        if preg2 in moderate_risk_categories:
            moderate_risks.append(f"{drug2} (Category {preg2})")
        
        if moderate_risks:
            explanation = f"⚠️ Pregnancy Caution: {', '.join(moderate_risks)} - Use only if benefits outweigh risks."
            return True, explanation, "Moderate"
        
        return False, "No specific pregnancy warnings for this combination", "Low"
    
    def analyze_alcohol_interaction(self, drug1: str, drug2: str) -> Tuple[bool, str, str]:
        """
        Analyze alcohol interaction warnings
        
        Returns:
            (has_warning, explanation, severity)
        """
        info1 = self.get_drug_info(drug1)
        info2 = self.get_drug_info(drug2)
        
        if not info1 or not info2:
            return False, "Alcohol interaction information not available", "Unknown"
        
        alc1 = str(info1.get('alcohol', 'Unknown')).lower()
        alc2 = str(info2.get('alcohol', 'Unknown')).lower()
        
        warnings = []
        
        if 'avoid' in alc1 or 'not recommended' in alc1:
            warnings.append(drug1)
        if 'avoid' in alc2 or 'not recommended' in alc2:
            warnings.append(drug2)
        
        if len(warnings) == 2:
            explanation = f"🍷 Alcohol Warning: Both {drug1} and {drug2} should not be combined with alcohol. Combined use may cause severe reactions."
            return True, explanation, "High"
        elif len(warnings) == 1:
            explanation = f"⚠️ Alcohol Caution: {warnings[0]} should not be combined with alcohol. Exercise caution with this drug combination."
            return True, explanation, "Moderate"
        
        return False, "No specific alcohol warnings for this combination", "Low"
    
    def generate_comprehensive_explanation(self, drug1: str, drug2: str, prediction_confidence: float) -> List[Dict]:
        """
        Generate comprehensive explanations for the interaction
        
        Returns:
            List of explanation dictionaries
        """
        if not self.loaded:
            self.load_data()
        
        explanations = []
        
        # 1. Drug class analysis
        has_conflict, class_exp, class_sev = self.analyze_drug_class_conflict(drug1, drug2)
        explanations.append({
            'explanation_type': 'drug_class',
            'explanation_text': class_exp,
            'severity_contribution': class_sev
        })
        
        # 2. Side effect overlap
        has_overlap, se_exp, se_sev = self.analyze_side_effect_overlap(drug1, drug2)
        explanations.append({
            'explanation_type': 'side_effect',
            'explanation_text': se_exp,
            'severity_contribution': se_sev
        })
        
        # 3. Pregnancy risk
        has_preg_risk, preg_exp, preg_sev = self.analyze_pregnancy_risk(drug1, drug2)
        explanations.append({
            'explanation_type': 'pregnancy',
            'explanation_text': preg_exp,
            'severity_contribution': preg_sev
        })
        
        # 4. Alcohol interaction
        has_alc_warning, alc_exp, alc_sev = self.analyze_alcohol_interaction(drug1, drug2)
        explanations.append({
            'explanation_type': 'alcohol',
            'explanation_text': alc_exp,
            'severity_contribution': alc_sev
        })
        
        return explanations


# Create singleton instance
explainable_ai_service = ExplainableAIService()
