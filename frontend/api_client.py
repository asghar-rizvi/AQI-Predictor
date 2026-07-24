import requests

def predict_aqi(payload):
    url = "http://localhost:8000/api/v1/predict"
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def forecast_3_days(payload):
    url = "http://localhost:8000/api/v1/forecast"
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}