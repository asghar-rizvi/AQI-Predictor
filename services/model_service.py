import joblib
import numpy as np
from fastapi import HTTPException
from core.config import ARTIFACT_PATH

class ModelService:
    def __init__(self):
        self.model = None
        self.expected_features = None
        self.load_model()

    def load_model(self):
        try:
            artifact = joblib.load(ARTIFACT_PATH)
            self.model = artifact['model']
            self.expected_features = artifact['features']
        except Exception as e:
            raise RuntimeError(f"Model loading failed: {str(e)}")

    def predict(self, payload):
        if not self.model:
            raise HTTPException(status_code=503, detail="Model not loaded")

        incoming_features = payload.features
        missing_features = set(self.expected_features) - set(incoming_features.keys())
        
        if missing_features:
            raise HTTPException(status_code=422, detail=f"Missing features: {missing_features}")

        ordered_features = [incoming_features[feat] for feat in self.expected_features]
        feature_array = np.array(ordered_features).reshape(1, -1)

        predicted_delta = self.model.predict(feature_array)[0]
        predicted_pm25 = payload.current_pm25 + predicted_delta

        return {
            "predicted_pm25": max(0.0, predicted_pm25),
            "predicted_delta": float(predicted_delta)
        }
    
    def predict_3_day_forecast(self, initial_payload):
        if not self.model:
            raise HTTPException(status_code=503, detail="Model not loaded")

        current_features = initial_payload.features.copy()
        current_pm25 = initial_payload.current_pm25
        forecast_pm25 = []
        
        steps = 72 # 3 days * 24 hours

        for _ in range(steps):
            missing_features = set(self.expected_features) - set(current_features.keys())
            if missing_features:
                raise HTTPException(status_code=422, detail=f"Missing features: {missing_features}")

            ordered_features = [current_features[feat] for feat in self.expected_features]
            feature_array = np.array(ordered_features).reshape(1, -1)

            predicted_delta = self.model.predict(feature_array)[0]
            next_pm25 = max(0.0, current_pm25 + predicted_delta)
            forecast_pm25.append(float(next_pm25))

            current_features['pm2_5_lag_3'] = current_features['pm2_5_lag_2']
            current_features['pm2_5_lag_2'] = current_features['pm2_5_lag_1']
            current_features['pm2_5_lag_1'] = current_pm25
            current_features['pm2_5'] = current_pm25 
            
            # In a strictly production environment, lag_24 and rolling stats 
            # would be fetched dynamically from a Feature Store. For this architecture proof, 
            # we hold them static to prevent exponential error compounding, which is standard 
            # for short-term recursive forecasting proofs.

            current_pm25 = next_pm25

        return forecast_pm25

model_service = ModelService()