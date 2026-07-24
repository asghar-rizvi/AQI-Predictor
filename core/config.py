import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACT_PATH = os.path.join(BASE_DIR, "artifacts", "models", "aqi_model_v1.joblib")

STREAMLIT_URL = os.environ.get("STREAMLIT_URL", "http://localhost:8501")
ALLOWED_ORIGINS = [
    STREAMLIT_URL,
    "http://localhost:8501", 
    "http://localhost:3000"  
]