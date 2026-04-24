import pandas as pd
import json
import os
from sklearn.ensemble import IsolationForest

def detect_anomalies_ml():
    print("Running Isolation Forest anomaly detection...")

    df = pd.read_csv("transformed_data/orbital_positions.csv")
    df = df.dropna()

    features = ["x_km", "y_km", "z_km", "distance_from_earth_km"]
    X = df[features]

    model = IsolationForest(contamination=0.1, random_state=42)
    df["anomaly_score"] = model.fit_predict(X)
    df["is_anomaly"] = df["anomaly_score"] == -1

    anomalies = df[df["is_anomaly"]]
    print(f"Detected {len(anomalies)} anomalies using Isolation Forest")
    print(anomalies[["timestamp", "distance_from_earth_km", "anomaly_score"]])

    os.makedirs("raw_data", exist_ok=True)
    df.to_csv("transformed_data/orbital_with_anomalies.csv", index=False)
    print("Saved to transformed_data/orbital_with_anomalies.csv")
    return df

if __name__ == "__main__":
    detect_anomalies_ml()