import pandas as pd
df = pd.read_csv("data/raw/crop_recommendation.csv")
print("Shape:", df.shape)
print("Columns:", df.columns.tolist())
print("Crops:", sorted(df["label"].unique()))
print("\nSamples per crop:")
print(df["label"].value_counts().to_string())
print("\nCoffee rows sample:")
coffee = df[df["label"] == "coffee"]
print(coffee.describe().to_string())
print("\nFeature ranges:")
print(df.describe().to_string())
