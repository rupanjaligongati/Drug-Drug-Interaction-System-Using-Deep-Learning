# Data Preprocessing for Drug-Drug Interaction System
# This script loads, cleans, and merges all datasets to prepare training data

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
import os
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("Drug-Drug Interaction System - Data Preprocessing")
print("="*60)

# ============================================================================
# STEP 1: Load Datasets
# ============================================================================
print("\n[1/7] Loading datasets...")

try:
    # Load drug interactions
    interactions_df = pd.read_csv('datasets/db_drug_interactions.csv')
    print(f"✓ Loaded interactions: {interactions_df.shape}")
    
    # Load side effects and clinical data
    side_effects_df = pd.read_csv('datasets/drugs_side_effects_drugs_com.csv')
    print(f"✓ Loaded side effects: {side_effects_df.shape}")
    
    # Load SMILES molecular data
    smiles_df = pd.read_csv('datasets/SMILES_Big_Data_Set.csv')
    print(f"✓ Loaded SMILES data: {smiles_df.shape}")
    
except Exception as e:
    print(f"✗ Error loading datasets: {e}")
    exit(1)

# ============================================================================
# STEP 2: Normalize Drug Names
# ============================================================================
print("\n[2/7] Normalizing drug names...")

def normalize_drug_name(name):
    """Normalize drug names for consistent matching"""
    if pd.isna(name):
        return None
    return str(name).lower().strip()

# Normalize interaction dataset
interactions_df['drug1_normalized'] = interactions_df['Drug 1'].apply(normalize_drug_name)
interactions_df['drug2_normalized'] = interactions_df['Drug 2'].apply(normalize_drug_name)

# Normalize side effects dataset
side_effects_df['drug_normalized'] = side_effects_df['drug_name'].apply(normalize_drug_name)

# Remove rows with missing drug names
interactions_df = interactions_df.dropna(subset=['drug1_normalized', 'drug2_normalized'])
side_effects_df = side_effects_df.dropna(subset=['drug_normalized'])

print(f"✓ Normalized {len(interactions_df)} interaction records")
print(f"✓ Normalized {len(side_effects_df)} drug records")

# ============================================================================
# STEP 3: Create Binary Interaction Labels
# ============================================================================
print("\n[3/7] Creating binary interaction labels...")

# All records in interactions dataset are positive examples (interaction exists)
interactions_df['has_interaction'] = 1

# Create negative examples (drug pairs without known interactions)
print("  Generating negative examples...")

# Get unique drugs from both datasets
all_drugs = set(interactions_df['drug1_normalized'].unique()) | \
            set(interactions_df['drug2_normalized'].unique())

# Create set of known interactions
known_interactions = set()
for _, row in interactions_df.iterrows():
    pair = tuple(sorted([row['drug1_normalized'], row['drug2_normalized']]))
    known_interactions.add(pair)

# Sample negative examples (non-interacting pairs)
negative_examples = []
drugs_list = list(all_drugs)
np.random.seed(42)

# Generate same number of negative examples as positive
num_negatives = len(interactions_df)
attempts = 0
max_attempts = num_negatives * 10

while len(negative_examples) < num_negatives and attempts < max_attempts:
    drug1 = np.random.choice(drugs_list)
    drug2 = np.random.choice(drugs_list)
    
    if drug1 != drug2:
        pair = tuple(sorted([drug1, drug2]))
        if pair not in known_interactions and pair not in negative_examples:
            negative_examples.append({
                'drug1_normalized': drug1,
                'drug2_normalized': drug2,
                'has_interaction': 0,
                'Interaction Description': 'No known interaction'
            })
    attempts += 1

negative_df = pd.DataFrame(negative_examples)
print(f"✓ Created {len(negative_df)} negative examples")

# Combine positive and negative examples
combined_df = pd.concat([
    interactions_df[['drug1_normalized', 'drug2_normalized', 'has_interaction', 'Interaction Description']],
    negative_df
], ignore_index=True)

print(f"✓ Total dataset size: {len(combined_df)} (Positive: {len(interactions_df)}, Negative: {len(negative_df)})")

# ============================================================================
# STEP 4: Extract SMILES Features
# ============================================================================
print("\n[4/7] Extracting molecular features from SMILES...")

def smiles_to_fingerprint(smiles, radius=2, n_bits=2048):
    """Convert SMILES to Morgan fingerprint"""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
        return np.array(fp)
    except:
        return None

def get_molecular_descriptors(smiles):
    """Extract molecular descriptors from SMILES"""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        
        descriptors = {
            'mol_weight': Descriptors.MolWt(mol),
            'logp': Descriptors.MolLogP(mol),
            'num_h_acceptors': Descriptors.NumHAcceptors(mol),
            'num_h_donors': Descriptors.NumHDonors(mol),
            'num_rotatable_bonds': Descriptors.NumRotatableBonds(mol),
            'tpsa': Descriptors.TPSA(mol)
        }
        return descriptors
    except:
        return None

# Create SMILES lookup dictionary (simplified - using first 1000 for demo)
smiles_lookup = {}
print("  Processing SMILES data (this may take a moment)...")

for idx, row in smiles_df.head(1000).iterrows():
    if pd.notna(row['SMILES']):
        descriptors = get_molecular_descriptors(row['SMILES'])
        if descriptors:
            # Store with a generic drug identifier
            smiles_lookup[f'drug_{idx}'] = descriptors

print(f"✓ Processed {len(smiles_lookup)} SMILES entries")

# ============================================================================
# STEP 5: Merge Clinical Features
# ============================================================================
print("\n[5/7] Merging clinical features...")

# Select relevant clinical features
clinical_features = ['drug_classes', 'pregnancy_category', 'alcohol', 'rating', 'rx_otc']

# Create drug feature lookup
drug_features = {}
for _, row in side_effects_df.iterrows():
    drug_name = row['drug_normalized']
    if drug_name not in drug_features:
        drug_features[drug_name] = {
            'drug_classes': row.get('drug_classes', 'Unknown'),
            'pregnancy_category': row.get('pregnancy_category', 'Unknown'),
            'alcohol': row.get('alcohol', 'Unknown'),
            'rating': row.get('rating', 0),
            'rx_otc': row.get('rx_otc', 'Unknown')
        }

print(f"✓ Created feature lookup for {len(drug_features)} drugs")

# ============================================================================
# STEP 6: Create Feature Vectors
# ============================================================================
print("\n[6/7] Creating feature vectors...")

def get_drug_features(drug_name):
    """Get features for a drug"""
    features = {}
    
    # Clinical features
    if drug_name in drug_features:
        features.update(drug_features[drug_name])
    else:
        # Default values if drug not found
        features = {
            'drug_classes': 'Unknown',
            'pregnancy_category': 'Unknown',
            'alcohol': 'Unknown',
            'rating': 0,
            'rx_otc': 'Unknown'
        }
    
    return features

# Build feature matrix
X_data = []
y_data = []
valid_indices = []

for idx, row in combined_df.iterrows():
    drug1_features = get_drug_features(row['drug1_normalized'])
    drug2_features = get_drug_features(row['drug2_normalized'])
    
    # Combine features
    combined_features = {
        # Drug 1 features
        'drug1_rating': drug1_features['rating'],
        'drug1_pregnancy': drug1_features['pregnancy_category'],
        'drug1_alcohol': drug1_features['alcohol'],
        'drug1_rx_otc': drug1_features['rx_otc'],
        
        # Drug 2 features
        'drug2_rating': drug2_features['rating'],
        'drug2_pregnancy': drug2_features['pregnancy_category'],
        'drug2_alcohol': drug2_features['alcohol'],
        'drug2_rx_otc': drug2_features['rx_otc'],
    }
    
    X_data.append(combined_features)
    y_data.append(row['has_interaction'])
    valid_indices.append(idx)

# Convert to DataFrame for easier encoding
X_df = pd.DataFrame(X_data)
y = np.array(y_data)

print(f"✓ Created feature matrix: {X_df.shape}")

# Encode categorical features
print("  Encoding categorical features...")

categorical_cols = ['drug1_pregnancy', 'drug1_alcohol', 'drug1_rx_otc',
                   'drug2_pregnancy', 'drug2_alcohol', 'drug2_rx_otc']

# One-hot encode categorical features
X_encoded = pd.get_dummies(X_df, columns=categorical_cols, dummy_na=True)

# Handle numerical features
numerical_cols = ['drug1_rating', 'drug2_rating']
X_encoded[numerical_cols] = X_encoded[numerical_cols].fillna(0)

print(f"✓ Encoded features: {X_encoded.shape}")

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_encoded)

print(f"✓ Scaled feature matrix: {X_scaled.shape}")

# ============================================================================
# STEP 7: Save Processed Data
# ============================================================================
print("\n[7/7] Saving processed data...")

# Create model directory
os.makedirs('model', exist_ok=True)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# Save processed data
data_to_save = {
    'X_train': X_train,
    'X_test': X_test,
    'y_train': y_train,
    'y_test': y_test,
    'scaler': scaler,
    'feature_names': X_encoded.columns.tolist(),
    'drug_features': drug_features,
    'interactions_df': combined_df.loc[valid_indices]
}

with open('model/processed_data.pkl', 'wb') as f:
    pickle.dump(data_to_save, f)

print(f"✓ Saved processed data to model/processed_data.pkl")

# Print summary statistics
print("\n" + "="*60)
print("PREPROCESSING SUMMARY")
print("="*60)
print(f"Total samples: {len(X_scaled)}")
print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")
print(f"Number of features: {X_scaled.shape[1]}")
print(f"Positive samples (interactions): {sum(y)}")
print(f"Negative samples (no interaction): {len(y) - sum(y)}")
print(f"Class balance: {sum(y)/len(y)*100:.1f}% positive")
print("="*60)
print("\n✓ Data preprocessing completed successfully!")
print("  Next step: Run 'python train_model.py' to train the model\n")
