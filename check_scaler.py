import joblib
import pandas as pd
import os

with open("out.txt", "w") as f:
    try:
        scaler = joblib.load("models/scaler.pkl")
        f.write(f"Scaler mean: {scaler.mean_}\n")
        f.write(f"Scaler scale (std): {scaler.scale_}\n")
    except Exception as e:
        f.write(f"Error loading scaler: {e}\n")

    path = "data/raw/crop_recommendation_scaled.csv"
    if os.path.exists(path):
        f.write("Found scaled dataset. Head:\n")
        f.write(str(pd.read_csv(path).head(2)) + "\n")
    else:
        f.write("Scaled dataset NOT found. Using standard dataset:\n")
        f.write(str(pd.read_csv("data/raw/crop_recommendation.csv").head(2)) + "\n")
