"""
models/train_crop_model.py
Train and compare multiple crop prediction models on Dataset 1.
Saves the best model (RandomForest) and a comparison report.
"""
import pandas as pd
import numpy as np
import joblib
import json
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (
    classification_report, accuracy_score, f1_score, confusion_matrix
)

os.makedirs("models", exist_ok=True)

def load_and_preprocess():
    dataset_path = "data/raw/crop_recommendation_scaled.csv"
    if not os.path.exists(dataset_path):
        print(f"Scaled dataset not found. Falling back to original.")
        dataset_path = "data/raw/crop_recommendation.csv"
        
    df = pd.read_csv(dataset_path)
    print(f"Dataset shape: {df.shape}")
    print(f"Crops: {sorted(df['label'].unique())}")
    print(f"Null values:\n{df.isnull().sum()}")

    le = LabelEncoder()
    df["crop_encoded"] = le.fit_transform(df["label"])

    feature_cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
    X = df[feature_cols].values
    y = df["crop_encoded"].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    joblib.dump(le,     "models/label_encoder.pkl")
    joblib.dump(scaler, "models/scaler.pkl")

    return X_scaled, y, le, feature_cols


def compare_models(X_train, X_test, y_train, y_test, le):
    """Train 6 models and return a comparison table."""
    models = {
        "Random Forest":     RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=200, random_state=42),
        "SVM (RBF)":         SVC(kernel="rbf", probability=True, random_state=42),
        "KNN (k=5)":         KNeighborsClassifier(n_neighbors=5),
        "Naive Bayes":       GaussianNB(),
    }

    results = {}
    trained = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        results[name] = {
            "accuracy": round(accuracy_score(y_test, y_pred) * 100, 2),
            "f1_macro": round(f1_score(y_test, y_pred, average="macro") * 100, 2),
        }
        trained[name] = model
        print(f"  {name:25s} — Accuracy: {results[name]['accuracy']:.2f}%  F1: {results[name]['f1_macro']:.2f}%")

    return results, trained


def train_main():
    X, y, le, feature_cols = load_and_preprocess()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\n--- Model Comparison ---")
    results, trained = compare_models(X_train, X_test, y_train, y_test, le)

    # Pick best model (Random Forest expected)
    best_name = max(results, key=lambda k: results[k]["accuracy"])
    best_model = trained[best_name]
    print(f"\nBest model: {best_name} ({results[best_name]['accuracy']}%)")

    # 5-fold CV on best
    cv = cross_val_score(best_model, X, y, cv=5)
    print(f"5-fold CV: {cv.mean()*100:.2f}% ± {cv.std()*100:.2f}%")

    # Full classification report
    y_pred = best_model.predict(X_test)
    print("\n" + classification_report(y_test, y_pred, target_names=le.classes_))

    # Save
    joblib.dump(best_model, "models/crop_model.pkl")

    regional_mapping = {
        "Coimbatore": {
            "agro_climatic_zone": "Western Zone",
            "soil_types": ["Red Loam", "Black Soil"],
            "crop_classes": ["banana", "coconut", "cotton", "maize", "mango", "mungbean", "papaya", "pomegranate", "pigeonpeas", "watermelon"],
            "major_excluded": ["apple", "coffee", "jute", "kidneybeans"]
        },
        "Erode": {
            "agro_climatic_zone": "Western Zone",
            "soil_types": ["Red Loam", "Alluvial"],
            "crop_classes": ["banana", "blackgram", "coconut", "maize", "mango", "mungbean", "papaya", "rice", "watermelon"],
            "major_excluded": ["apple", "coffee", "grapes", "mothbeans"]
        },
        "Salem": {
            "agro_climatic_zone": "North Western Zone",
            "soil_types": ["Red Loam", "Laterite"],
            "crop_classes": ["banana", "blackgram", "chickpea", "coffee", "cotton", "mango", "orange", "papaya", "pigeonpeas", "pomegranate", "rice"],
            "major_excluded": ["apple", "jute", "muskmelon", "watermelon"]
        },
        "Tiruppur": {
            "agro_climatic_zone": "Western Zone",
            "soil_types": ["Black Soil", "Red Sandy Loam"],
            "crop_classes": ["banana", "coconut", "cotton", "maize", "mungbean", "muskmelon", "pomegranate", "watermelon"],
            "major_excluded": ["apple", "coffee", "jute", "rice"]
        },
        "Nilgiris": {
            "agro_climatic_zone": "High Rainfall/Hilly Zone",
            "soil_types": ["Laterite", "Forest Soil"],
            "crop_classes": ["apple", "coffee", "orange", "kidneybeans"],
            "major_excluded": ["coconut", "cotton", "jute", "rice", "watermelon", "mango", "papaya"]
        }
    }

    seasonal_mapping = {
        "Kharif": [
            "rice", "maize", "cotton", "pigeonpeas", "mungbean", "banana", "coconut", "jute"
        ],
        "Rabi": [
            "chickpea", "blackgram", "lentil", "kidneybeans", "grapes", "pomegranate", "orange", "mango"
        ],
        "Summer": [
            "watermelon", "muskmelon", "mothbeans", "mungbean", "papaya", "coconut", "banana"
        ],
        "Nilgiris_Annual": [
            "coffee", "apple", "orange", "kidneybeans"
        ]
    }

    meta = {
        "feature_names":   feature_cols,
        "crop_classes":    list(le.classes_),
        "best_model":      best_name,
        "test_accuracy":   results[best_name]["accuracy"],
        "cv_mean":         round(cv.mean() * 100, 2),
        "cv_std":          round(cv.std() * 100, 2),
        "model_comparison": results,
        "regional_mapping": regional_mapping,
        "seasonal_mapping": seasonal_mapping,
        "soil_thresholds": {
            "ph_critical_low":   5.5,
            "ph_warning_low":    6.0,
            "ph_optimal_max":    7.5,
            "ec_salinity_danger":4.0,
            "oc_critical_low":   0.5,
            "n_low": 280, "p_low": 10, "k_low": 108
        }
    }
    with open("models/model_metadata.json", "w") as f:
        json.dump(meta, f, indent=2)
    print("\nSaved: models/crop_model.pkl + models/model_metadata.json")


def train_fertilizer_model():
    path = "data/raw/fertilizer_prediction.csv"
    if not os.path.exists(path):
        print("Fertilizer dataset not found — skipping.")
        return

    df = pd.read_csv(path)
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Drop duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Detect target column
    target = next((c for c in df.columns if 'fertilizer' in c.lower()), None)
    if not target:
        print("Target column not found — skipping.")
        return

    # Encode all string columns
    from sklearn.preprocessing import LabelEncoder
    le_target = LabelEncoder()
    df[target] = le_target.fit_transform(df[target].astype(str))
    
    for col in df.select_dtypes(include='object').columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))

    # Use all columns except target
    feature_cols = [c for c in df.columns if c != target]
    X = df[feature_cols].values
    y = df[target].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"Fertilizer model accuracy: {acc*100:.2f}%")

    joblib.dump(model,    "models/fertilizer_model.pkl")
    joblib.dump(le_target,"models/fertilizer_le.pkl")
    print("Saved: fertilizer_model.pkl")


if __name__ == "__main__":
    train_main()
    train_fertilizer_model()
