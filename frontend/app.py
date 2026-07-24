import streamlit as st
from api_client import predict_aqi, forecast_3_days
from components import inject_css, render_header, render_result_card, render_3_day_forecast, render_alerts

inject_css()
render_header()

st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown('<div class="section-header">Current State</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    current_pm25 = st.number_input("Current PM2.5", min_value=0.0, max_value=500.0, value=85.5, step=0.1)
with col2:
    pm10 = st.number_input("PM10", min_value=0.0, max_value=600.0, value=120.0, step=0.1)

st.markdown('<div class="section-header">Pollutants</div>', unsafe_allow_html=True)
col3, col4, col5 = st.columns(3)
with col3:
    co = st.number_input("Carbon Monoxide", min_value=0.0, max_value=5000.0, value=450.0, step=1.0)
with col4:
    no2 = st.number_input("Nitrogen Dioxide", min_value=0.0, max_value=200.0, value=25.0, step=0.1)
with col5:
    so2 = st.number_input("Sulphur Dioxide", min_value=0.0, max_value=200.0, value=8.0, step=0.1)

o3 = st.number_input("Ozone", min_value=0.0, max_value=200.0, value=30.0, step=0.1)

st.markdown('<div class="section-header">Weather</div>', unsafe_allow_html=True)
col6, col7, col8, col9 = st.columns(4)
with col6:
    temp = st.number_input("Temperature (C)", min_value=-20.0, max_value=60.0, value=28.0, step=0.1)
with col7:
    humidity = st.number_input("Relative Humidity", min_value=0.0, max_value=100.0, value=65.0, step=0.1)
with col8:
    wind_speed = st.number_input("Wind Speed", min_value=0.0, max_value=150.0, value=12.0, step=0.1)
with col9:
    wind_dir = st.number_input("Wind Direction", min_value=0.0, max_value=360.0, value=180.0, step=0.1)

st.markdown('<div class="section-header">Temporal Cyclic Features</div>', unsafe_allow_html=True)
col10, col11, col12, col13 = st.columns(4)
with col10:
    h_sin = st.number_input("Hour Sin", min_value=-1.0, max_value=1.0, value=0.5, step=0.01)
with col11:
    h_cos = st.number_input("Hour Cos", min_value=-1.0, max_value=1.0, value=-0.86, step=0.01)
with col12:
    m_sin = st.number_input("Month Sin", min_value=-1.0, max_value=1.0, value=0.0, step=0.01)
with col13:
    m_cos = st.number_input("Month Cos", min_value=-1.0, max_value=1.0, value=-1.0, step=0.01)

st.markdown('<div class="section-header">Autoregressive Lags & Rollings</div>', unsafe_allow_html=True)
col14, col15, col16, col17 = st.columns(4)
with col14:
    lag1 = st.number_input("PM2.5 Lag 1", min_value=0.0, max_value=500.0, value=82.0, step=0.1)
with col15:
    lag2 = st.number_input("PM2.5 Lag 2", min_value=0.0, max_value=500.0, value=79.0, step=0.1)
with col16:
    lag3 = st.number_input("PM2.5 Lag 3", min_value=0.0, max_value=500.0, value=76.0, step=0.1)
with col17:
    lag24 = st.number_input("PM2.5 Lag 24", min_value=0.0, max_value=500.0, value=90.0, step=0.1)

col18, col19 = st.columns(2)
with col18:
    roll_mean = st.number_input("Rolling Mean 24", min_value=0.0, max_value=500.0, value=85.0, step=0.1)
with col19:
    roll_std = st.number_input("Rolling Std 24", min_value=0.0, max_value=200.0, value=15.0, step=0.1)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    predict_btn = st.button("Execute 1-Hour Forecast")
with col_btn2:
    forecast_btn = st.button("Execute 72-Hour Forecast", type="primary")

payload = {
    "current_pm25": current_pm25,
    "features": {
        "pm10": pm10,
        "pm2_5": lag1,
        "carbon_monoxide": co,
        "nitrogen_dioxide": no2,
        "sulphur_dioxide": so2,
        "ozone": o3,
        "temperature_2m": temp,
        "relative_humidity_2m": humidity,
        "wind_speed_10m": wind_speed,
        "wind_direction_10m": wind_dir,
        "hour_sin": h_sin,
        "hour_cos": h_cos,
        "month_sin": m_sin,
        "month_cos": m_cos,
        "pm2_5_lag_1": lag1,
        "pm2_5_lag_2": lag2,
        "pm2_5_lag_3": lag3,
        "pm2_5_lag_24": lag24,
        "pm2_5_rolling_24_mean": roll_mean,
        "pm2_5_rolling_24_std": roll_std
    }
}

if predict_btn:
    with st.spinner("Computing Delta..."):
        result = predict_aqi(payload)
    render_result_card(result)

if forecast_btn:
    with st.spinner("Running 72-Hour Autoregressive Simulation..."):
        forecast_result = forecast_3_days(payload)
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    render_3_day_forecast(forecast_result)
    render_alerts(forecast_result)
    st.markdown('</div>', unsafe_allow_html=True)