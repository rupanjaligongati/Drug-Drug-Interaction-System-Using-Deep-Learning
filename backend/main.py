# FastAPI Backend for Drug-Drug Interaction Prediction System v2.0

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.predict import router as predict_router
from routes.auth import router as auth_router
from routes.history import router as history_router
from routes.analytics import router as analytics_router
from routes.files import router as files_router
from services.ddi_service import ddi_service
from services.explainable_ai_service import explainable_ai_service
from services.recommendation_service import recommendation_service
from database import init_db, check_db_connection

from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ddi_api.log')
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Life span event handler
    Initializes database, loads ML model, and prepares services
    """
    logger.info("="*60)
    logger.info("Drug-Drug Interaction API v2.0 - Starting Up")
    logger.info("="*60)
    
    try:
        # Change to parent directory to access model files
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # os.chdir(parent_dir)  # Avoid changing CWD globally if possible, but keeping for now as it seems intentional
        logger.info(f"Working directory: {os.getcwd()}")
        
        # Ensure uploads directory exists
        from utils.file_upload import ensure_upload_directory
        ensure_upload_directory()
        logger.info("✓ Uploads directory ready")
        
        # Initialize database
        logger.info("Initializing database...")
        try:
            init_db()
            if check_db_connection():
                logger.info("✓ Database initialized and connected")
            else:
                logger.warning("⚠ Database connection failed - some features may not work")
        except Exception as e:
            logger.error(f"✗ Database initialization failed: {e}")
            logger.warning("⚠ API will run but database features will be disabled")
        
        import threading
        
        def load_heavy_models():
            # Load ML model
            logger.info("Loading ML model in background...")
            try:
                ddi_service.load_model()
                logger.info("✓ ML model loaded successfully")
            except Exception as e:
                logger.error(f"✗ Model loading failed: {e}")
                logger.warning("⚠ Predictions will fail until model is loaded")
            
            # Load Explainable AI data
            logger.info("Loading Explainable AI service...")
            try:
                explainable_ai_service.load_data()
                logger.info("✓ Explainable AI service ready")
            except Exception as e:
                logger.warning(f"⚠ Explainable AI service failed to load: {e}")
            
            # Load Recommendation service data
            logger.info("Loading Recommendation service...")
            try:
                recommendation_service.load_data()
                logger.info("✓ Recommendation service ready")
            except Exception as e:
                logger.warning(f"⚠ Recommendation service failed to load: {e}")
                
        # Start loading in background thread to avoid blocking port binding (Render timeout issue)
        threading.Thread(target=load_heavy_models, daemon=True).start()
        
        logger.info("="*60)
        logger.info("API is ready to accept requests! Models are loading in background.")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"✗ Startup failed: {e}")
        logger.error("API may not function correctly")

    yield

    """Shutdown event handler"""
    logger.info("Shutting down Drug-Drug Interaction API v2.0...")


# Create FastAPI app
app = FastAPI(
    title="Drug-Drug Interaction Prediction API v2.0",
    description="""
    AI-powered healthcare decision-support system for predicting drug-drug interactions.
    
    ## Features
    - 🤖 Deep Learning Predictions
    - 🔍 Explainable AI
    - 💊 Alternative Drug Recommendations
    - 📊 User History & Analytics
    - 🔐 Secure Authentication
    - 📸 Image Analysis (Gemini Vision)
    
    ## Disclaimer
    This system is for educational and decision-support purposes only.
    It does NOT replace professional medical advice.
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predict_router)
app.include_router(auth_router)
app.include_router(history_router)
app.include_router(analytics_router)
app.include_router(files_router)





if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("Starting Drug-Drug Interaction Prediction API v2.0")
    print("="*60)
    print("\n🚀 Multi-Dashboard Healthcare Decision-Support System")
    print("\nAPI will be available at:")
    print("  - Main API: http://localhost:8000")
    print("  - Documentation: http://localhost:8000/docs")
    print("  - Alternative docs: http://localhost:8000/redoc")
    print("\n📋 Available Endpoints:")
    print("  - POST /predict - Predict drug interactions")
    print("  - POST /auth/register - Register new user")
    print("  - POST /auth/login - User login")
    print("  - GET /history/me - Get user history")
    print("  - GET /analytics/system - System analytics")
    print("\n⚠️  MEDICAL DISCLAIMER:")
    print("  This system is for educational purposes only.")
    print("  Always consult healthcare professionals.")
    print("\nPress CTRL+C to stop the server")
    print("="*60 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

