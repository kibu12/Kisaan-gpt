import pandas as pd
import os

def scale_dataset():
    input_path = "data/raw/crop_recommendation.csv"
    output_path = "data/raw/crop_recommendation_scaled.csv"
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    df = pd.read_csv(input_path)
    print(f"Original shape: {df.shape}")
    
    # Scale NPK values to match realistic Indian soil ranges
    # Original Max: N=140, P=145, K=205
    # Target Max: N~420 (x3.0), P~200 (x1.4), K~410 (x2.0)
    
    df["N"] = (df["N"] * 3.0).astype(int)
    df["P"] = (df["P"] * 1.4).astype(int)
    df["K"] = (df["K"] * 2.0).astype(int)
    
    df.to_csv(output_path, index=False)
    print(f"Successfully saved scaled dataset to {output_path}")
    print("\nNew NPK Ranges:")
    print(df[["N", "P", "K"]].describe())

if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    scale_dataset()
