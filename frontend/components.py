import streamlit as st
import pandas as pd
import altair as alt  # ADD THIS LINE
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime, timedelta

def inject_css():
    with open("frontend/style.css", "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    st.markdown('<div class="bg-orb orb-1"></div>', unsafe_allow_html=True)
    st.markdown('<div class="bg-orb orb-2"></div>', unsafe_allow_html=True)
    st.markdown('<div class="bg-orb orb-3"></div>', unsafe_allow_html=True)

def render_header():
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem;">
                10Pearls AQI Predictor
            </h1>
            <p style="color: #a5b4fc; font-size: 1.1rem; font-weight: 300;">
                Advanced Delta-Based Forecasting Engine
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

def render_result_card(data):
    if "error" in data:
        st.markdown(f'<div class="error-card">Connection Failed: {data["error"]}</div>', unsafe_allow_html=True)
        return

    pred_pm25 = data.get("predicted_pm25", 0)
    pred_delta = data.get("predicted_delta", 0)
    
    delta_color = "#34d399" if pred_delta <= 0 else "#f87171"
    delta_symbol = "+" if pred_delta > 0 else ""
    
    html = f"""
    <div style="display: flex; gap: 20px; justify-content: center; margin-top: 2rem;">
        <div class="metric-card">
            <div class="metric-title">Forecasted PM2.5</div>
            <div class="metric-value">{pred_pm25:.2f}</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">Predicted Delta</div>
            <div class="metric-value" style="font-size: 2rem;">{delta_symbol}{pred_delta:.2f}</div>
            <div class="metric-delta" style="color: {delta_color};">Change from current hour</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    
def render_alerts(forecast_data):
    forecast_list = forecast_data.get("forecast_72h", [])
    if not forecast_list:
        return

    max_pm25 = max(forecast_list)
    
    alert_html = None
    if max_pm25 > 250:
        alert_html = '<div class="error-card" style="background: rgba(127, 29, 29, 0.4); border-color: #ef4444;">SEVERE ALERT: Hazardous AQI levels detected in the 3-day window.</div>'
    elif max_pm25 > 150:
        alert_html = '<div class="error-card" style="background: rgba(120, 53, 15, 0.4); border-color: #f97316;">WARNING: Unhealthy AQI levels expected. Limit outdoor activity.</div>'
    elif max_pm25 > 100:
        alert_html = '<div class="error-card" style="background: rgba(113, 63, 18, 0.4); border-color: #eab308;">CAUTION: Moderate to Unhealthy for Sensitive Groups.</div>'

    if alert_html:
        st.markdown(alert_html, unsafe_allow_html=True)

def get_aqi_status(pm25):
    if pm25 <= 12.0: return "Good", "#00e400"
    elif pm25 <= 35.4: return "Moderate", "#ffff00"
    elif pm25 <= 55.4: return "Unhealthy for Sensitive", "#ff7e00"
    elif pm25 <= 150.4: return "Unhealthy", "#ff0000"
    elif pm25 <= 250.4: return "Very Unhealthy", "#8f3f97"
    else: return "Hazardous", "#7e0023"

def render_3_day_forecast(forecast_data):
    if "error" in forecast_data:
        st.markdown(f'<div class="error-card">Forecast Failed: {forecast_data["error"]}</div>', unsafe_allow_html=True)
        return

    forecast_list = forecast_data.get("forecast_72h", [])
    if not forecast_list or len(forecast_list) < 72:
        return

    # Calculate daily averages (Next 3 days, 24 hours each)
    day1_avg = sum(forecast_list[0:24]) / 24
    day2_avg = sum(forecast_list[24:48]) / 24
    day3_avg = sum(forecast_list[48:72]) / 24

    days_data = [
        {"avg": day1_avg, "date": datetime.now() + timedelta(days=1)},
        {"avg": day2_avg, "date": datetime.now() + timedelta(days=2)},
        {"avg": day3_avg, "date": datetime.now() + timedelta(days=3)}
    ]

    st.markdown('<div class="section-header">3-Day PM2.5 Outlook</div>', unsafe_allow_html=True)
    
    # Use Streamlit columns for perfect, bug-free grid alignment
    col1, col2, col3 = st.columns(3)
    
    for i, day in enumerate(days_data):
        status, color = get_aqi_status(day["avg"])
        day_name = day["date"].strftime("%A")
        date_str = day["date"].strftime("%b %d")
        
        # Clean, isolated HTML block for each card
        card_html = f'''
        <div class="metric-card" style="border-top: 4px solid {color}; height: 100%;">
            <div class="metric-title" style="font-size: 1.1rem; font-weight: 600;">{day_name}</div>
            <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 1rem;">{date_str}</div>
            <div class="metric-value" style="margin: 1.5rem 0;">
                {day["avg"]:.1f}
            </div>
            <div style="background-color: {color}; color: #000; padding: 6px 16px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; display: inline-block; text-transform: uppercase;">
                {status}
            </div>
        </div>
        '''
        
        # Inject into respective column
        if i == 0:
            with col1:
                st.markdown(card_html, unsafe_allow_html=True)
        elif i == 1:
            with col2:
                st.markdown(card_html, unsafe_allow_html=True)
        else:
            with col3:
                st.markdown(card_html, unsafe_allow_html=True)