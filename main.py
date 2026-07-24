from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="10Pearls AQI Predictor API",
    description="Advanced Delta-based AQI forecasting API",
    version="1.0"
)

app.include_router(router, prefix="/api/v1")