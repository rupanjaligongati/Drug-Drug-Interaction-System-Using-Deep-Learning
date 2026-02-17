"""
Alternative Drug Recommendation Service
Suggests safer alternative drugs based on medical conditions and safety scores
"""

import pandas as pd
import logging
from typing import List, Dict
import os

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for recommending alternative drugs"""
    
    def __init__(self):
        self.side_effects_data = None
        self.interaction_data = None
        self.loaded = False
    
    def load_data(self):
        """Load drug metadata for recommendations"""
        try:
            # Load side effects dataset
            side_effects_path = os.path.join("datasets", "drugs_side_effects_drugs_com.csv")
            self.side_effects_data = pd.read_csv(side_effects_path)
            
            # Load interaction dataset
            interaction_path = os.path.join("datasets", "db_drug_interactions.csv")
            self.interaction_data = pd.read_csv(interaction_path)
            
            # Clean column names
            self.side_effects_data.columns = self.side_effects_data.columns.str.strip()
            self.interaction_data.columns = self.interaction_data.columns.str.strip()
            
            # Fill NaN values
            self.side_effects_data = self.side_effects_data.fillna("Unknown")
            
            self.loaded = True
            logger.info("✓ Recommendation service data loaded successfully")
            
        except Exception as e:
            logger.error(f"✗ Failed to load recommendation data: {e}")
            self.loaded = False
    
    def get_drug_medical_condition(self, drug_name: str) -> str:
        """Get the medical condition a drug treats"""
        if not self.loaded:
            return "Unknown"
        
        drug_info = self.side_effects_data[
            self.side_effects_data['drug_name'].str.lower() == drug_name.lower()
        ]
        
        if drug_info.empty:
            return "Unknown"
        
        return drug_info.iloc[0].get('medical_condition', 'Unknown')
    
    def get_related_drugs(self, drug_name: str) -> List[str]:
        """Get related drugs from the dataset"""
        if not self.loaded:
            return []
        
        drug_info = self.side_effects_data[
            self.side_effects_data['drug_name'].str.lower() == drug_name.lower()
        ]
        
        if drug_info.empty:
            return []
        
        related = drug_info.iloc[0].get('related_drugs', '')
        
        if pd.isna(related) or related == 'Unknown':
            return []
        
        # Parse related drugs (usually comma-separated)
        related_list = [d.strip() for d in str(related).split(',') if d.strip()]
        return related_list[:5]  # Return top 5
    
    def check_interaction_exists(self, drug1: str, drug2: str) -> bool:
        """Check if an interaction exists between two drugs"""
        if not self.loaded:
            return False
        
        # Check both directions
        interaction = self.interaction_data[
            ((self.interaction_data['Drug 1'].str.lower() == drug1.lower()) & 
             (self.interaction_data['Drug 2'].str.lower() == drug2.lower())) |
            ((self.interaction_data['Drug 1'].str.lower() == drug2.lower()) & 
             (self.interaction_data['Drug 2'].str.lower() == drug1.lower()))
        ]
        
        return not interaction.empty
    
    def calculate_safety_score(self, alternative_drug: str, other_drug: str) -> float:
        """
        Calculate safety score for an alternative drug
        
        Score based on:
        - No known interaction: +0.5
        - High rating: +0.3
        - Low side effects: +0.2
        
        Returns: Score between 0 and 1
        """
        score = 0.0
        
        # Check for interaction
        has_interaction = self.check_interaction_exists(alternative_drug, other_drug)
        if not has_interaction:
            score += 0.5
        
        # Get drug info
        drug_info = self.side_effects_data[
            self.side_effects_data['drug_name'].str.lower() == alternative_drug.lower()
        ]
        
        if not drug_info.empty:
            drug_data = drug_info.iloc[0]
            
            # Rating score (0-10 scale)
            try:
                rating = float(drug_data.get('rating', 0))
                if rating >= 7:
                    score += 0.3
                elif rating >= 5:
                    score += 0.15
            except:
                pass
            
            # Side effects score (fewer is better)
            side_effects = str(drug_data.get('side_effects', ''))
            if len(side_effects) < 100:  # Arbitrary threshold
                score += 0.2
            elif len(side_effects) < 200:
                score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def recommend_alternatives(self, risky_drug: str, safe_drug: str, max_recommendations: int = 3) -> List[Dict]:
        """
        Recommend alternative drugs to replace the risky drug
        
        Args:
            risky_drug: The drug that's causing the interaction
            safe_drug: The other drug in the combination
            max_recommendations: Maximum number of alternatives to return
            
        Returns:
            List of recommendation dictionaries
        """
        if not self.loaded:
            self.load_data()
        
        recommendations = []
        
        # Get medical condition for the risky drug
        medical_condition = self.get_drug_medical_condition(risky_drug)
        
        # Get related drugs
        related_drugs = self.get_related_drugs(risky_drug)
        
        # If no related drugs found, search by medical condition
        if not related_drugs and medical_condition != "Unknown":
            condition_drugs = self.side_effects_data[
                self.side_effects_data['medical_condition'].str.lower() == medical_condition.lower()
            ]
            related_drugs = condition_drugs['drug_name'].head(10).tolist()
        
        # Evaluate each alternative
        for alt_drug in related_drugs:
            if alt_drug.lower() == risky_drug.lower():
                continue
            
            # Check if this alternative also interacts
            has_interaction = self.check_interaction_exists(alt_drug, safe_drug)
            
            # Calculate safety score
            safety_score = self.calculate_safety_score(alt_drug, safe_drug)
            
            # Generate reason
            if not has_interaction:
                reason = f"{alt_drug} treats {medical_condition} and has no known interaction with {safe_drug}. Consider this as a safer alternative."
            else:
                reason = f"{alt_drug} treats {medical_condition} but may also interact with {safe_drug}. Consult your doctor."
                safety_score *= 0.5  # Reduce score if interaction exists
            
            recommendations.append({
                'alternative_drug': alt_drug,
                'reason': reason,
                'safety_score': round(safety_score, 2),
                'medical_condition': medical_condition
            })
        
        # Sort by safety score (highest first)
        recommendations.sort(key=lambda x: x['safety_score'], reverse=True)
        
        # Return top recommendations
        return recommendations[:max_recommendations]
    
    def get_recommendations_for_interaction(self, drug1: str, drug2: str) -> List[Dict]:
        """
        Get recommendations for both drugs in an interaction
        
        Returns:
            Combined list of recommendations
        """
        all_recommendations = []
        
        # Get alternatives for drug1
        recs1 = self.recommend_alternatives(drug1, drug2, max_recommendations=2)
        all_recommendations.extend(recs1)
        
        # Get alternatives for drug2
        recs2 = self.recommend_alternatives(drug2, drug1, max_recommendations=2)
        all_recommendations.extend(recs2)
        
        # If no recommendations found, provide generic advice
        if not all_recommendations:
            all_recommendations.append({
                'alternative_drug': 'Consult Healthcare Provider',
                'reason': f'No specific alternatives found in our database. Please consult your healthcare provider for safer alternatives to {drug1} or {drug2}.',
                'safety_score': 0.0,
                'medical_condition': 'Various'
            })
        
        return all_recommendations


# Create singleton instance
recommendation_service = RecommendationService()
