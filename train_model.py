# Deep Learning Model Training for Drug-Drug Interaction Prediction
# Binary classification using TensorFlow/Keras

import numpy as np
import pandas as pd
import pickle
import os
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score, classification_report
import matplotlib.pyplot as plt
import seaborn as sns

# TensorFlow imports
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
from tensorflow.keras.optimizers import Adam

print("="*60)
print("Drug-Drug Interaction System - Model Training")
print("="*60)
print(f"TensorFlow version: {tf.__version__}")

# Set random seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

# ============================================================================
# STEP 1: Load Preprocessed Data
# ============================================================================
print("\n[1/5] Loading preprocessed data...")

try:
    with open('model/processed_data.pkl', 'rb') as f:
        data = pickle.load(f)
    
    X_train = data['X_train']
    X_test = data['X_test']
    y_train = data['y_train']
    y_test = data['y_test']
    scaler = data['scaler']
    feature_names = data['feature_names']
    
    print(f"✓ Training samples: {X_train.shape}")
    print(f"✓ Testing samples: {X_test.shape}")
    print(f"✓ Number of features: {X_train.shape[1]}")
    print(f"✓ Training labels - Positive: {sum(y_train)}, Negative: {len(y_train) - sum(y_train)}")
    
except Exception as e:
    print(f"✗ Error loading data: {e}")
    print("  Please run 'python preprocess_data.py' first!")
    exit(1)

# ============================================================================
# STEP 2: Build Deep Neural Network Architecture
# ============================================================================
print("\n[2/5] Building Deep Neural Network...")

def build_dnn_model(input_dim):
    """
    Build a Deep Neural Network for binary classification
    
    Architecture:
    - Input layer (input_dim features)
    - Dense layer 1: 512 units, ReLU activation, Dropout 0.3
    - Dense layer 2: 256 units, ReLU activation, Dropout 0.3
    - Dense layer 3: 128 units, ReLU activation, Dropout 0.2
    - Dense layer 4: 64 units, ReLU activation
    - Output layer: 1 unit, Sigmoid activation (binary classification)
    """
    model = models.Sequential([
        # Input layer
        layers.Input(shape=(input_dim,)),
        
        # Hidden layer 1
        layers.Dense(512, activation='relu', name='dense_1'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        
        # Hidden layer 2
        layers.Dense(256, activation='relu', name='dense_2'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        
        # Hidden layer 3
        layers.Dense(128, activation='relu', name='dense_3'),
        layers.BatchNormalization(),
        layers.Dropout(0.2),
        
        # Hidden layer 4
        layers.Dense(64, activation='relu', name='dense_4'),
        layers.BatchNormalization(),
        
        # Output layer (binary classification)
        layers.Dense(1, activation='sigmoid', name='output')
    ])
    
    return model

# Build model
input_dim = X_train.shape[1]
model = build_dnn_model(input_dim)

# Compile model
model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=[
        'accuracy',
        tf.keras.metrics.Precision(name='precision'),
        tf.keras.metrics.Recall(name='recall'),
        tf.keras.metrics.AUC(name='auc')
    ]
)

# Print model summary
print("\n" + "="*60)
print("MODEL ARCHITECTURE")
print("="*60)
model.summary()
print("="*60)

# ============================================================================
# STEP 3: Train Model
# ============================================================================
print("\n[3/5] Training model...")

# Define callbacks
early_stopping = callbacks.EarlyStopping(
    monitor='val_loss',
    patience=10,
    restore_best_weights=True,
    verbose=1
)

model_checkpoint = callbacks.ModelCheckpoint(
    'model/ddi_model.h5',
    monitor='val_loss',
    save_best_only=True,
    verbose=1
)

reduce_lr = callbacks.ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=5,
    min_lr=0.00001,
    verbose=1
)

# Train model
print("\nTraining started...")
history = model.fit(
    X_train, y_train,
    validation_split=0.2,
    epochs=100,
    batch_size=32,
    callbacks=[early_stopping, model_checkpoint, reduce_lr],
    verbose=1
)

print("\n✓ Training completed!")

# ============================================================================
# STEP 4: Evaluate Model
# ============================================================================
print("\n[4/5] Evaluating model on test set...")

# Make predictions
y_pred_proba = model.predict(X_test, verbose=0)
y_pred = (y_pred_proba > 0.5).astype(int).flatten()

# Calculate metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_pred_proba)

# Print evaluation results
print("\n" + "="*60)
print("MODEL EVALUATION RESULTS")
print("="*60)
print(f"Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-Score:  {f1:.4f}")
print(f"ROC-AUC:   {auc:.4f}")
print("="*60)

# Detailed classification report
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['No Interaction', 'Interaction']))

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
print("\nConfusion Matrix:")
print(cm)
print(f"True Negatives:  {cm[0][0]}")
print(f"False Positives: {cm[0][1]}")
print(f"False Negatives: {cm[1][0]}")
print(f"True Positives:  {cm[1][1]}")

# ============================================================================
# STEP 5: Save Model and Generate Visualizations
# ============================================================================
print("\n[5/5] Saving model and generating visualizations...")

# Save final model
model.save('model/ddi_model.h5')
print("✓ Model saved to model/ddi_model.h5")

# Save model metadata
metadata = {
    'input_dim': input_dim,
    'feature_names': feature_names,
    'scaler': scaler,
    'metrics': {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'roc_auc': float(auc)
    }
}

with open('model/model_metadata.pkl', 'wb') as f:
    pickle.dump(metadata, f)

print("✓ Model metadata saved to model/model_metadata.pkl")

# Create visualizations directory
os.makedirs('model/visualizations', exist_ok=True)

# Plot 1: Training history
plt.figure(figsize=(15, 5))

# Accuracy plot
plt.subplot(1, 3, 1)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy Over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True, alpha=0.3)

# Loss plot
plt.subplot(1, 3, 2)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss Over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.grid(True, alpha=0.3)

# AUC plot
plt.subplot(1, 3, 3)
plt.plot(history.history['auc'], label='Training AUC')
plt.plot(history.history['val_auc'], label='Validation AUC')
plt.title('Model AUC Over Epochs')
plt.xlabel('Epoch')
plt.ylabel('AUC')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('model/visualizations/training_history.png', dpi=300, bbox_inches='tight')
print("✓ Training history plot saved")

# Plot 2: Confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['No Interaction', 'Interaction'],
            yticklabels=['No Interaction', 'Interaction'])
plt.title('Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.savefig('model/visualizations/confusion_matrix.png', dpi=300, bbox_inches='tight')
print("✓ Confusion matrix plot saved")

# Generate evaluation report
report_path = 'model/evaluation_report.txt'
with open(report_path, 'w') as f:
    f.write("="*60 + "\n")
    f.write("DRUG-DRUG INTERACTION MODEL - EVALUATION REPORT\n")
    f.write("="*60 + "\n\n")
    
    f.write("MODEL ARCHITECTURE:\n")
    f.write("-" * 60 + "\n")
    f.write(f"Input features: {input_dim}\n")
    f.write("Hidden layers: 512 -> 256 -> 128 -> 64\n")
    f.write("Output: 1 (Sigmoid activation)\n")
    f.write("Optimizer: Adam (lr=0.001)\n")
    f.write("Loss: Binary Crossentropy\n\n")
    
    f.write("DATASET STATISTICS:\n")
    f.write("-" * 60 + "\n")
    f.write(f"Training samples: {len(X_train)}\n")
    f.write(f"Testing samples: {len(X_test)}\n")
    f.write(f"Positive samples (train): {sum(y_train)}\n")
    f.write(f"Negative samples (train): {len(y_train) - sum(y_train)}\n\n")
    
    f.write("PERFORMANCE METRICS:\n")
    f.write("-" * 60 + "\n")
    f.write(f"Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)\n")
    f.write(f"Precision: {precision:.4f}\n")
    f.write(f"Recall:    {recall:.4f}\n")
    f.write(f"F1-Score:  {f1:.4f}\n")
    f.write(f"ROC-AUC:   {auc:.4f}\n\n")
    
    f.write("CONFUSION MATRIX:\n")
    f.write("-" * 60 + "\n")
    f.write(f"True Negatives:  {cm[0][0]}\n")
    f.write(f"False Positives: {cm[0][1]}\n")
    f.write(f"False Negatives: {cm[1][0]}\n")
    f.write(f"True Positives:  {cm[1][1]}\n\n")
    
    f.write("CLASSIFICATION REPORT:\n")
    f.write("-" * 60 + "\n")
    f.write(classification_report(y_test, y_pred, target_names=['No Interaction', 'Interaction']))
    f.write("\n")
    
    f.write("="*60 + "\n")
    f.write("NOTES:\n")
    f.write("="*60 + "\n")
    f.write("- This model is for educational purposes only\n")
    f.write("- Does not replace professional medical advice\n")
    f.write("- Should be validated with clinical experts before deployment\n")
    f.write("="*60 + "\n")

print(f"✓ Evaluation report saved to {report_path}")

# Final summary
print("\n" + "="*60)
print("MODEL TRAINING COMPLETED SUCCESSFULLY!")
print("="*60)
print(f"\nModel files saved in 'model/' directory:")
print("  - ddi_model.h5 (trained model)")
print("  - model_metadata.pkl (model configuration)")
print("  - processed_data.pkl (preprocessed data)")
print("  - evaluation_report.txt (detailed metrics)")
print("  - visualizations/ (training plots)")
print("\nNext step: Run the backend API with 'cd backend && uvicorn main:app --reload'")
print("="*60 + "\n")
