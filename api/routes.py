from fastapi import APIRouter, HTTPException
from models.schemas import AQIRequestPayload, AQIResponse, ForecastResponse
from services.model_service import model_service

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model_service.model is not None,
        "features_expected": model_service.expected_features
    }

@router.post("/predict", response_model=AQIResponse)
def predict_aqi(payload: AQIRequestPayload):
    try:
        result = model_service.predict(payload)
        return AQIResponse(
            predicted_pm25=result["predicted_pm25"],
            predicted_delta=result["predicted_delta"],
            status="success"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/forecast", response_model=ForecastResponse)
def forecast_3_days(payload: AQIRequestPayload):
    try:
        forecast_data = model_service.predict_3_day_forecast(payload)
        return ForecastResponse(
            forecast_72h=forecast_data,
            status="success"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))