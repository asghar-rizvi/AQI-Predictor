# 10Pearls AQI Predictor

## Overview

This project predicts the Air Quality Index (PM2.5) up to 72 hours ahead using a serverless machine learning pipeline. Instead of following a typical forecasting tutorial, I focused on building a pipeline that handles time-series data correctly, avoids data leakage, and can be retrained automatically through GitHub Actions.

---

## Design Decisions

Rather than only chasing a higher accuracy score, I spent most of the project making sure the data pipeline and forecasting approach were mathematically correct and easy to maintain.

### 1. Predicting the Change Instead of the Value (ΔPM2.5)

One limitation of tree-based models like Random Forest and XGBoost is that they generally don't predict values much higher than what they have already seen during training. For example, if the highest PM2.5 value in the training data is 200, the model is unlikely to predict 250 even if the conditions suggest it.

To work around this, the model predicts the hourly **change** in PM2.5 instead of the absolute value.

**Training Target**

```
Δyₜ = PM₂.₅(t) − PM₂.₅(t−1)
```

**Inference**

```
ŷₜ = PM₂.₅(t−1) + Δŷₜ
```

By predicting the change rather than the value itself, the model only has to learn normal hourly fluctuations. The final reconstructed predictions achieved an **R² score of 0.937**.

---

### 2. Combining Air Quality and Weather Data

Most free APIs either separate weather and air quality data or restrict historical requests.

To solve this, the pipeline fetches data from both Open-Meteo Air Quality and Archive Weather APIs in parallel and merges everything using a common datetime index. This creates a single feature dataset without relying on paid services.

---

### 3. Keeping the Time Order Intact

Since this is a time-series problem, preserving the order of the data is important.

The dataset is split chronologically:

- First 80% → Training
- Last 20% → Testing

No random shuffling is used, which prevents the model from accidentally learning information from the future.

---

### 4. Cyclical Time Features

Hours are cyclical, but integer encoding doesn't capture that relationship.

For example, Hour 23 and Hour 0 are only one hour apart, yet numerically they look far apart.

To represent time correctly, hour-based features are converted using sine and cosine transformations.

```
Hour_sin = sin(2π × hour / 24)
Hour_cos = cos(2π × hour / 24)
```

This helps the model understand that midnight naturally follows 11 PM.

---

## System Architecture

```text
[ GitHub Actions Cron Jobs ]
       |                   |
 (Hourly)             (Daily)
       v                   v
[ Feature Pipeline ] -> [ Training Pipeline ]
 (Open-Meteo API)      (XGBoost Delta Fit)
       |                   |
       v                   v
[ GitHub Artifacts ] <- [ Retrained .joblib ]

===========================================

[ Streamlit Frontend ]          [ FastAPI Backend ]
 (Streamlit Cloud)      <--->   (Render.com)
 (iOS-style UI)         CORS    (Artifact Serving)
 (72hr Autoregressive)          (Delta Reconstruction)
```

---

## Tech Stack

### Data & Feature Engineering

- Python
- Pandas
- NumPy
- Open-Meteo APIs

### Machine Learning

- XGBoost
- Scikit-Learn (Ridge)
- SHAP

### Backend

- FastAPI
- Uvicorn
- Pydantic
- Joblib

### Frontend

- Streamlit
- Custom CSS

### Automation

- GitHub Actions
- Scheduled Workflows
- GitHub Artifacts

### Deployment

- Render
- Streamlit Community Cloud

---

## Project Structure

```text
├── .github/
│   └── workflows/
│       └── mlops_pipeline.yml
├── api/
│   └── routes.py
├── artifacts/
│   └── models/
│       └── aqi_model_v1.joblib
├── core/
│   └── config.py
├── frontend/
│   ├── app.py
│   ├── api_client.py
│   ├── components.py
│   └── style.css
├── models/
│   └── schemas.py
├── pipelines/
│   ├── feature_pipeline.py
│   └── train_pipeline.py
├── services/
│   └── model_service.py
├── tests/
│   └── test_model.py
├── main.py
└── requirements.txt
```

---

## 72-Hour Forecasting

The model predicts one hour ahead, so generating a 72-hour forecast requires an autoregressive loop.

For each prediction:

1. Predict the next hourly change (ΔPM2.5).
2. Reconstruct the actual PM2.5 value.
3. Update the lag features with the new prediction.
4. Repeat the process 72 times.
5. Average every 24 predictions to generate the daily forecast shown in the dashboard.

---

## GitHub Actions Workflow

The CI/CD pipeline is split into separate jobs.

### Push or Pull Request

- Run unit tests
- Verify model loading
- Check prediction outputs

### Every Hour

- Fetch the latest weather and AQI data for Karachi
- Apply feature engineering
- Save the dataset as a GitHub Artifact

### Every Day

- Load the latest feature dataset
- Retrain the XGBoost model
- Compare performance against Ridge Regression
- Upload the updated model artifact

---

## Local Setup

### Clone the repository

```bash
git clone <repository_url>
cd 10Pearls_AQI_Project
```

### Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### Start the backend

```bash
uvicorn main:app --reload
```

API documentation:

```
http://localhost:8000/docs
```

### Start the frontend

```bash
streamlit run frontend/app.py
```

Dashboard:

```
http://localhost:8501
```

---

## Model Explainability

To better understand what the model was learning, I used SHAP's `TreeExplainer`.

The feature importance results matched expectations. The previous PM2.5 lag values (`lag_1` and `lag_2`) contributed the most to predictions, showing that the model relied primarily on recent historical trends rather than unrelated features.

To better understand what the model was learning, I used SHAP's `TreeExplainer`.

The feature importance results matched expectations. The previous PM2.5 lag values (`lag_1` and `lag_2`) contributed the most to predictions, showing that the model relied primarily on recent historical trends rather than unrelated features.

<p align="center">
  <img src="https://github.com/asghar-rizvi/AQI-Predictor/blob/main/artifacts/models/shap_summary_plot.png?raw=true" alt="SHAP Summary Plot" width="800">
</p>

---

## Possible Improvements

Some improvements I'd like to explore in the future include:

- Replacing local `.joblib` files with a model registry such as MLflow or Vertex AI.
- Updating rolling statistics dynamically during long autoregressive forecasts instead of keeping them fixed.
- Supporting multiple cities by making latitude and longitude configurable from the Streamlit interface.