import pandas as pd
import numpy as np
import joblib
import os
from xgboost import XGBRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def run():
    print("Starting Delta-Based Model Retraining...")
    
    live_path = "artifacts/data/live/engineered_features.csv"
    
    if not os.path.exists(live_path):
        print("ERROR: Engineered features not found. Did the feature pipeline run?")
        return

    df = pd.read_csv(live_path, parse_dates=['datetime'], index_col='datetime')
    target_col = 'pm2_5'

    # My delta tageting logic, means my y column
    df['pm2_5_delta'] = df[target_col].diff()
    df = df.dropna()

    # choronological split (same as i chose for my training)
    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]

    features_to_drop = [target_col, 'pm2_5_delta', 'hour', 'dayofweek', 'month']
    X_train = train_df.drop(features_to_drop, axis=1)
    y_train_delta = train_df['pm2_5_delta']

    X_test = test_df.drop(features_to_drop, axis=1)
    y_test_delta = test_df['pm2_5_delta']
    actual_y_test = test_df[target_col]
    lag_1_test = test_df['pm2_5_lag_1']

    print(f"Training on {len(X_train)} samples, Testing on {len(X_test)} samples...")
    print(f"Features used: {list(X_train.columns)}")

    # model hyperparameters
    models = {
        "Ridge_Baseline": Ridge(alpha=10.0),
        "XGBoost_Delta": XGBRegressor(
            n_estimators=100,
            learning_rate=0.03,
            max_depth=4,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
    }

    results = {}
    best_model = None
    best_rmse = float('inf')
    best_model_name = ""

    for name, model in models.items():
        model.fit(X_train, y_train_delta)
        predicted_delta = model.predict(X_test)
        final_preds = lag_1_test + predicted_delta

        rmse = np.sqrt(mean_squared_error(actual_y_test, final_preds))
        mae = mean_absolute_error(actual_y_test, final_preds)
        r2 = r2_score(actual_y_test, final_preds)
        results[name] = {'RMSE': rmse, 'MAE': mae, 'R2': r2}
        print(f"{name} -> RMSE: {rmse:.2f}, MAE: {mae:.2f}, R2: {r2:.3f}")

        if rmse < best_rmse:
            best_rmse = rmse
            best_model = model
            best_model_name = name

    # saving under artifacts
    os.makedirs("artifacts/models", exist_ok=True)
    out_model_path = "artifacts/models/retrained_model.joblib"
    
    artifact = {
        'model': best_model,
        'features': list(X_train.columns),
        'metrics': results[best_model_name]
    }
    joblib.dump(artifact, out_model_path)
    
    print(f"\nSUCCESS: Winner is {best_model_name}. Saved to {out_model_path}")

if __name__ == "__main__":
    run()