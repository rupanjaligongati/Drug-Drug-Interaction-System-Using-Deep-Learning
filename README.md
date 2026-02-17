# Drug-Drug Interaction Prediction System Using Deep Learning

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![React](https://img.shields.io/badge/React-18.2-61dafb.svg)
![License](https://img.shields.io/badge/License-Academic-yellow.svg)

## 📋 Project Overview

An AI-powered healthcare decision-support system that predicts drug-drug interactions using deep learning. This final year major project combines molecular data (SMILES), clinical metadata, and interaction records to provide risk assessments and safety warnings.

### ⚠️ Important Disclaimer

**This system is for educational and academic purposes only.** It does NOT replace professional medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals before making any medication decisions.

---

## 🎯 Key Features

- ✅ **AI-Powered Predictions**: Deep neural network trained on drug interaction databases
- ✅ **Molecular Analysis**: SMILES-based molecular feature extraction using RDKit
- ✅ **Risk Assessment**: Confidence scores and risk level classification (Low/Moderate/High)
- ✅ **Modern Web Interface**: Professional React frontend with real-time predictions
- ✅ **RESTful API**: FastAPI backend with comprehensive error handling
- ✅ **Clinical Metadata**: Integration of drug classes, pregnancy categories, and side effects

---

## 🏗️ System Architecture

```
Drug_DDI_Project/
│
├── datasets/                          # Dataset files
│   ├── db_drug_interactions.csv
│   ├── drugs_side_effects_drugs_com.csv
│   └── SMILES_Big_Data_Set.csv
│
├── model/                             # Trained model and data
│   ├── ddi_model.h5                  # Trained Keras model
│   ├── processed_data.pkl            # Preprocessed training data
│   ├── model_metadata.pkl            # Model configuration
│   ├── evaluation_report.txt         # Performance metrics
│   └── visualizations/               # Training plots
│
├── backend/                           # FastAPI Backend
│   ├── main.py                       # FastAPI application
│   ├── schemas.py                    # Pydantic models
│   ├── routes/
│   │   └── predict.py               # API endpoints
│   ├── services/
│   │   └── ddi_service.py           # Prediction logic
│   └── utils/
│       └── preprocess.py            # Utility functions
│
├── frontend/                          # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── DrugInput.jsx        # Input component
│   │   │   └── ResultCard.jsx       # Results display
│   │   ├── services/
│   │   │   └── api.js               # API integration
│   │   ├── App.jsx                  # Main app
│   │   └── main.jsx                 # Entry point
│   ├── package.json
│   └── vite.config.js
│
├── preprocess_data.py                 # Data preprocessing script
├── train_model.py                     # Model training script
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ and npm
- 8GB+ RAM recommended
- Windows/Linux/macOS

### Step 1: Clone/Download Project

```bash
cd "Drug–Drug Interaction System Using Deep Learning"
```

### Step 2: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Note**: RDKit installation may take time. If you encounter issues:
```bash
# Alternative installation via conda
conda install -c conda-forge rdkit
```

### Step 3: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

---

## 📊 Usage Instructions

### Phase 1: Data Preprocessing

Process and merge all datasets:

```bash
python preprocess_data.py
```

**Expected Output:**
- `model/processed_data.pkl` (preprocessed features)
- Console logs showing dataset statistics
- Processing time: ~2-5 minutes

### Phase 2: Model Training

Train the deep learning model:

```bash
python train_model.py
```

**Expected Output:**
- `model/ddi_model.h5` (trained model)
- `model/model_metadata.pkl` (model config)
- `model/evaluation_report.txt` (metrics)
- `model/visualizations/` (training plots)
- Training time: ~10-30 minutes (depending on hardware)

**Expected Performance:**
- Accuracy: >75%
- F1-Score: >0.70
- ROC-AUC: >0.80

### Phase 3: Start Backend API

```bash
cd backend
python main.py
```

**API will be available at:**
- Main API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

**API Endpoints:**
- `GET /` - API information
- `GET /health` - Health check
- `POST /predict` - Predict drug interaction

### Phase 4: Start Frontend

Open a **new terminal** and run:

```bash
cd frontend
npm run dev
```

**Frontend will open at:** http://localhost:3000

---

## 🧪 Testing the System

### Test Case 1: Known Interaction (High Risk)

**Input:**
- Drug 1: `Aspirin`
- Drug 2: `Warfarin`

**Expected Result:**
- Interaction: Yes
- Risk Level: High
- Warning about bleeding risk

### Test Case 2: Moderate Risk

**Input:**
- Drug 1: `Ibuprofen`
- Drug 2: `Lisinopril`

**Expected Result:**
- Interaction: Yes/Moderate
- NSAID and ACE inhibitor interaction

### Test Case 3: Low/No Interaction

**Input:**
- Drug 1: `Metformin`
- Drug 2: `Vitamin D`

**Expected Result:**
- Interaction: No/Low
- Minimal interaction risk

---

## 🔬 Technology Stack

### Machine Learning
- **TensorFlow/Keras**: Deep neural network implementation
- **Scikit-learn**: Data preprocessing and evaluation
- **RDKit**: Molecular feature extraction from SMILES
- **Pandas/NumPy**: Data manipulation

### Backend
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

### Frontend
- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **Axios**: HTTP client
- **CSS3**: Modern styling with gradients and animations

### Data Sources
1. **db_drug_interactions.csv**: Drug interaction pairs and descriptions
2. **drugs_side_effects_drugs_com.csv**: Clinical metadata and side effects
3. **SMILES_Big_Data_Set.csv**: Molecular structures and properties

---

## 📈 Model Architecture

```
Input Layer (n features)
    ↓
Dense Layer (512 units, ReLU) + Dropout(0.3)
    ↓
Dense Layer (256 units, ReLU) + Dropout(0.3)
    ↓
Dense Layer (128 units, ReLU) + Dropout(0.2)
    ↓
Dense Layer (64 units, ReLU)
    ↓
Output Layer (1 unit, Sigmoid)
```

**Training Configuration:**
- Loss: Binary Crossentropy
- Optimizer: Adam (lr=0.001)
- Batch Size: 32
- Early Stopping: Patience 10
- Validation Split: 20%

---

## 🎓 Academic Context

### Problem Statement

Drug-drug interactions (DDIs) are a significant cause of adverse drug reactions, leading to hospitalizations and increased healthcare costs. Manual checking of interactions is time-consuming and error-prone. This system demonstrates how AI can assist healthcare professionals in identifying potential DDIs.

### Methodology

1. **Data Collection**: Integrated three datasets containing interaction records, clinical data, and molecular structures
2. **Feature Engineering**: Extracted molecular descriptors from SMILES and merged with clinical features
3. **Model Development**: Designed and trained a deep neural network for binary classification
4. **Evaluation**: Assessed model using accuracy, precision, recall, F1-score, and ROC-AUC
5. **Deployment**: Created a full-stack web application for real-time predictions

### Limitations

- **Dataset Coverage**: Limited to drugs in training datasets
- **Binary Classification**: Only predicts yes/no, not severity levels
- **Patient-Specific Factors**: Does not account for age, weight, medical conditions
- **Static Data**: No real-time updates from medical databases
- **Validation**: Requires clinical validation before real-world use

### Future Scope

1. **Multi-Class Classification**: Predict interaction severity (mild/moderate/severe)
2. **Personalized Predictions**: Incorporate patient demographics and medical history
3. **Real-Time Updates**: Integration with FDA/WHO databases
4. **Hospital Integration**: EHR system compatibility
5. **Mobile Application**: Native iOS/Android apps for healthcare providers
6. **Explainable AI**: Mechanism-based explanations for interactions
7. **Multi-Drug Analysis**: Support for 3+ drug combinations

---

## 🛠️ Troubleshooting

### Issue: RDKit Installation Fails

**Solution:**
```bash
# Use conda instead
conda install -c conda-forge rdkit
```

### Issue: Backend Can't Find Model

**Solution:**
- Ensure you've run `python train_model.py` first
- Check that `model/ddi_model.h5` exists
- Verify working directory is project root

### Issue: Frontend Can't Connect to Backend

**Solution:**
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Verify API_BASE_URL in `frontend/src/services/api.js`

### Issue: Out of Memory During Training

**Solution:**
- Reduce batch size in `train_model.py` (line with `batch_size=32`)
- Use fewer samples for initial testing
- Close other applications

---

## 📝 API Documentation

### POST /predict

**Request:**
```json
{
  "drug1": "Aspirin",
  "drug2": "Warfarin"
}
```

**Response:**
```json
{
  "interaction": "Yes",
  "confidence": 0.92,
  "risk_level": "High",
  "interaction_summary": "A potential drug-drug interaction has been detected...",
  "warnings": "⚠️ HIGH RISK: The combination may pose significant health risks...",
  "disclaimer": "⚕️ MEDICAL DISCLAIMER: This system is for educational purposes only..."
}
```

---

## 👥 Contributors

**Final Year Project**
- Academic Year: 2025-2026
- Institution: [Your Institution Name]
- Department: Computer Science / AI & ML

---

## 📄 License

This project is for **academic and educational purposes only**. Not licensed for commercial or clinical use.

---

## 🙏 Acknowledgments

- Drug interaction data from public databases
- SMILES molecular data from chemical repositories
- Clinical metadata from Drugs.com
- TensorFlow and FastAPI communities
- React and Vite development teams

---

## 📞 Support

For academic inquiries or project-related questions, please contact your project supervisor or institution.

---

**⚕️ FINAL REMINDER**: This system is a demonstration of AI capabilities in healthcare. It is NOT a substitute for professional medical advice. Always consult qualified healthcare professionals for medication decisions.
