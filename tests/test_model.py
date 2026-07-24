import os
import joblib

def test_model_artifact_exists():
    artifact_path = "artifacts/models/aqi_model_v1.joblib"
    assert os.path.exists(artifact_path), "Model artifact missing!"

def test_model_loads_and_predicts():
    artifact_path = "artifacts/models/aqi_model_v1.joblib"
    if not os.path.exists(artifact_path):
        return  
    
    artifact = joblib.load(artifact_path)
    model = artifact['model']
    features = artifact['features']
    
    dummy_input = [[50.0] * len(features)]
    prediction = model.predict(dummy_input)
    
    assert prediction is not None, "Model returned None"
    assert len(prediction) == 1, "Model returned incorrect shape"