import requests
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def run():
    print("Connecting to Open-Meteo Dual Endpoints for Karachi")
    
    LAT, LON = 24.8607, 67.0011
    BACKFILL_DAYS = 180
    end_date = datetime.now()
    start_date = end_date - timedelta(days=BACKFILL_DAYS)

    # Firstly i will be fetching air quality
    air_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    air_params = {
        "latitude": LAT, "longitude": LON,
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "hourly": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone"
    }
    res_air = requests.get(air_url, params=air_params).json()
    df_air = pd.DataFrame(res_air['hourly'])
    df_air['datetime'] = pd.to_datetime(df_air['time'])
    df_air = df_air.drop('time', axis=1).set_index('datetime')

    # Secondly i will be fetching weather
    weather_url = "https://archive-api.open-meteo.com/v1/archive"
    weather_params = {
        "latitude": LAT, "longitude": LON,
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"
    }
    res_weather = requests.get(weather_url, params=weather_params).json()
    df_weather = pd.DataFrame(res_weather['hourly'])
    df_weather['datetime'] = pd.to_datetime(df_weather['time'])
    df_weather = df_weather.drop('time', axis=1).set_index('datetime')

    # Thirdly i will concat the dataframes as i did in model training under my notebook
    df = pd.concat([df_air, df_weather], axis=1)
    df = df.replace(-999, np.nan)
    df = df.ffill().bfill()

    # Applying the same feature engineering that i did while training
    df['hour'] = df.index.hour
    df['dayofweek'] = df.index.dayofweek
    df['month'] = df.index.month

    df['hour_sin'] = np.sin(2 * np.pi * df['hour']/24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour']/24)
    df['month_sin'] = np.sin(2 * np.pi * df['month']/12)
    df['month_cos'] = np.cos(2 * np.pi * df['month']/12)

    target_col = 'pm2_5'
    df[f'{target_col}_lag_1'] = df[target_col].shift(1)
    df[f'{target_col}_lag_24'] = df[target_col].shift(24)
    df[f'{target_col}_rolling_24_mean'] = df[target_col].rolling(window=24).mean()
    df[f'{target_col}_rolling_24_std'] = df[target_col].rolling(window=24).std()

    df = df.dropna()

    # Same goes for feature selection
    unnecessary_cols = [
        'wind_speed_10m', 'wind_direction_10m', 'relative_humidity_2m', 
        'temperature_2m', 'pm2_5_rolling_24_mean', 'pm2_5_rolling_24_std', 
        'pm2_5_lag_24', 'month_sin', 'month_cos'
    ]
    df = df.drop(columns=unnecessary_cols, errors='ignore')

    # saving for my training pipeline
    os.makedirs("artifacts/data/live", exist_ok=True)
    out_path = "artifacts/data/live/engineered_features.csv"
    df.to_csv(out_path)
    
    print(f"SUCCESS: Fetched and engineered {len(df)} rows for Karachi. Saved to {out_path}")

if __name__ == "__main__":
    run()