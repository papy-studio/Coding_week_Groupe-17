"""
Simple comparison runner - outputs results to text file
"""
import os
import sys
import joblib

# Redirect output to file
output_file = open("outputs/results.txt", "w")

class OutputLogger:
    def __init__(self, file_handle):
        self.file = file_handle
        
    def write(self, text):
        self.file.write(text)
        sys.stdout.write(text)
        
    def flush(self):
        self.file.flush()

sys.stdout = OutputLogger(output_file)
sys.stderr = OutputLogger(output_file)

import warnings
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from sklearn.metrics import (
    accuracy_score, 
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

warnings.filterwarnings("ignore")

# Class labels
CLASSES = [
    'Insufficient_Weight', 'Normal_Weight',
    'Obesity_Type_I',      'Obesity_Type_II',
    'Obesity_Type_III',    'Overweight_Level_I',
    'Overweight_Level_II'
]

os.makedirs("outputs", exist_ok=True)

print("=" * 70)
print("  LOADING DATA")
print("=" * 70)

X_train = pd.read_csv("data/X_train.csv")
X_test  = pd.read_csv("data/X_test.csv")
y_train = pd.read_csv("data/y_train.csv").squeeze()
y_test  = pd.read_csv("data/y_test.csv").squeeze()

X_test = X_test[X_train.columns]

print(f"  Train : {X_train.shape[0]} samples")
print(f"  Test  : {X_test.shape[0]} samples")
print(f"  Features : {X_train.shape[1]}")
print()

results = {}
models = {}

# 1. LightGBM
print("[1/4] Training LightGBM...")
lgbm = LGBMClassifier(n_estimators=200, learning_rate=0.05, max_depth=6, random_state=42, verbose=-1)
lgbm.fit(X_train, y_train)
y_pred = lgbm.predict(X_test)
y_prob = lgbm.predict_proba(X_test)
results["LightGBM"] = {
    "accuracy": accuracy_score(y_test, y_pred),
    "precision": precision_score(y_test, y_pred, average="weighted"),
    "recall": recall_score(y_test, y_pred, average="weighted"),
    "f1": f1_score(y_test, y_pred, average="weighted"),
    "roc_auc": roc_auc_score(y_test, y_prob, multi_class="ovr")
}
models["LightGBM"] = lgbm
joblib.dump(lgbm, "outputs/lightgbm.pkl")
print("  Done")

# 2. CatBoost
print("[2/4] Training CatBoost...")
cat = CatBoostClassifier(iterations=500, learning_rate=0.1, depth=6, random_seed=42, verbose=0)
cat.fit(X_train, y_train)
y_pred = cat.predict(X_test)
y_prob = cat.predict_proba(X_test)
results["CatBoost"] = {
    "accuracy": accuracy_score(y_test, y_pred),
    "precision": precision_score(y_test, y_pred, average="weighted"),
    "recall": recall_score(y_test, y_pred, average="weighted"),
    "f1": f1_score(y_test, y_pred, average="weighted"),
    "roc_auc": roc_auc_score(y_test, y_prob, multi_class="ovr", average="weighted")
}
models["CatBoost"] = cat
joblib.dump(cat, "outputs/catboost.pkl")
print("  Done")

# 3. XGBoost
print("[3/4] Training XGBoost...")
xgb = XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1, eval_metric='mlogloss', random_state=42, use_label_encoder=False)
xgb.fit(X_train, y_train)
y_pred = xgb.predict(X_test)
y_prob = xgb.predict_proba(X_test)
results["XGBoost"] = {
    "accuracy": accuracy_score(y_test, y_pred),
    "precision": precision_score(y_test, y_pred, average="weighted"),
    "recall": recall_score(y_test, y_pred, average="weighted"),
    "f1": f1_score(y_test, y_pred, average="weighted"),
    "roc_auc": roc_auc_score(y_test, y_prob, multi_class="ovr")
}
models["XGBoost"] = xgb
joblib.dump(xgb, "outputs/xgboost.pkl")
print("  Done")

# 4. Random Forest
print("[4/4] Training Random Forest...")
rf = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
y_prob = rf.predict_proba(X_test)
results["Random Forest"] = {
    "accuracy": accuracy_score(y_test, y_pred),
    "precision": precision_score(y_test, y_pred, average="weighted"),
    "recall": recall_score(y_test, y_pred, average="weighted"),
    "f1": f1_score(y_test, y_pred, average="weighted"),
    "roc_auc": roc_auc_score(y_test, y_prob, multi_class="ovr")
}
models["Random Forest"] = rf
joblib.dump(rf, "outputs/random_forest.pkl")
print("  Done")

# Display metrics
print("\n" + "=" * 70)
print("  MODEL COMPARISON - METRICS")
print("=" * 70)
print(f"\n  {'Model':<15} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1-Score':>10} {'ROC-AUC':>10}")
print("-" * 70)

for name, m in results.items():
    print(f"  {name:<15} {m['accuracy']*100:>9.2f}% {m['precision']*100:>9.2f}% {m['recall']*100:>9.2f}% {m['f1']*100:>9.2f}% {m['roc_auc']:>9.4f}")

best_acc = max(results, key=lambda n: results[n]["accuracy"])
best_roc = max(results, key=lambda n: results[n]["roc_auc"])

print("\n" + "=" * 70)
print("  WINNER")
print("=" * 70)
print(f"\n  🏆 Best Model (Accuracy): {best_acc} ({results[best_acc]['accuracy']*100:.2f}%)")
print(f"  🏆 Best Model (ROC-AUC): {best_roc} ({results[best_roc]['roc_auc']:.4f})")

# List saved files
print("\n  Saved files:")
for f in os.listdir("outputs"):
    print(f"    - {f}")

output_file.close()
print("\n✅ Results saved to outputs/results.txt")

