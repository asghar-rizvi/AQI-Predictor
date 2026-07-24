from fastapi import FastAPI
from api.routes import router
from core.config import ALLOWED_ORIGINS
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="10Pearls AQI Predictor API",
    description="Advanced Delta-based AQI forecasting API",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")