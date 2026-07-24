from pydantic import BaseModel, Field

class AQIRequestPayload(BaseModel):
    current_pm25: float = Field(..., description="Absolute PM2.5 of the current hour for delta reconstruction")
    features: dict = Field(..., description="Dictionary of the exact engineered features required by the model")

    class Config:
        json_schema_extra = {
            "example": {
                "current_pm25": 85.5,
                "features": {
                    "pm10": 120.0, "pm2_5": 82.0, "carbon_monoxide": 450.0,
                    "nitrogen_dioxide": 25.0, "sulphur_dioxide": 8.0, "ozone": 30.0,
                    "temperature_2m": 28.0, "relative_humidity_2m": 65.0,
                    "wind_speed_10m": 12.0, "wind_direction_10m": 180.0,
                    "hour_sin": 0.5, "hour_cos": -0.86, "month_sin": 0.0, "month_cos": -1.0,
                    "pm2_5_lag_1": 80.0, "pm2_5_lag_2": 79.0, "pm2_5_lag_3": 76.0,
                    "pm2_5_lag_24": 90.0, "pm2_5_rolling_24_mean": 85.0,
                    "pm2_5_rolling_24_std": 15.0
                }
            }
        }

class AQIResponse(BaseModel):
    predicted_pm25: float
    predicted_delta: float
    status: str

class ForecastResponse(BaseModel):
    forecast_72h: list
    status: str