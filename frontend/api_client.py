import os
import requests

def get_base_url():
    return os.environ.get("BACKEND_URL", "http://localhost:8000")

def predict_aqi(payload):
    url = f"{get_base_url()}/api/v1/predict"
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def forecast_3_days(payload):
    url = f"{get_base_url()}/api/v1/forecast"
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}