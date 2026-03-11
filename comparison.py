"""
         COMPARISON — 4 Models (LightGBM, CatBoost, XGBoost, Random Forest)
         Obesity Risk Estimation | Coding Week 2026
"""

import os
import warnings
import joblib
import pickle

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from sklearn.metrics import (
    accuracy_score, 
    classification_report, 
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

warnings.filterwarnings("ignore")

# Class labels for obesity levels
CLASSES = [
    'Insufficient_Weight', 'Normal_Weight',
    'Obesity_Type_I',      'Obesity_Type_II',
    'Obesity_Type_III',    'Overweight_Level_I',
    'Overweight_Level_II'
]

# Short labels for confusion matrix visualization
CLASSES_SHORT = ['Ins', 'Nor', 'Ob1', 'Ob2', 'Ob3', 'Ow1', 'Ow2']

os.makedirs("outputs", exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════════════════════════

print("=" * 70)
print("  LOADING DATA")
print("=" * 70)

X_train = pd.read_csv("data/X_train.csv")
X_test  = pd.read_csv("data/X_test.csv")
y_train = pd.read_csv("data/y_train.csv").squeeze()
y_test  = pd.read_csv("data/y_test.csv").squeeze()

# Validate data integrity
train_cols = set(X_train.columns)
test_cols = set(X_test.columns)
if train_cols != test_cols:
    missing_in_test = train_cols - test_cols
    extra_in_test = test_cols - train_cols
    if missing_in_test:
        print(f"  ⚠️  Columns in train but not in test: {missing_in_test}")
    if extra_in_test:
        print(f"  ⚠️  Columns in test but not in train: {extra_in_test}")
    # Align columns
    X_test = X_test[X_train.columns]

print(f"  Train : {X_train.shape[0]} samples")
print(f"  Test  : {X_test.shape[0]} samples")
print(f"  Features : {X_train.shape[1]}")
print()


# ═══════════════════════════════════════════════════════════════
# TRAIN MODELS
# ═══════════════════════════════════════════════════════════════

print("=" * 70)
print("  TRAINING MODELS")
print("=" * 70)

# Store results for all models
results = {}
models = {}

# ─────────────────────────────────────────────────────────────────
# 1. LIGHTGBM
# ─────────────────────────────────────────────────────────────────
print("\n  [1/4] Training LightGBM...")

lgbm_model = LGBMClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=6,
    random_state=42,
    verbose=-1
)
lgbm_model.fit(X_train, y_train)

# Predictions
y_pred_lgbm = lgbm_model.predict(X_test)
y_prob_lgbm = lgbm_model.predict_proba(X_test)

# Metrics
results["LightGBM"] = {
    "accuracy": accuracy_score(y_test, y_pred_lgbm),
    "precision": precision_score(y_test, y_pred_lgbm, average="weighted"),
    "recall": recall_score(y_test, y_pred_lgbm, average="weighted"),
    "f1": f1_score(y_test, y_pred_lgbm, average="weighted"),
    "roc_auc": roc_auc_score(y_test, y_prob_lgbm, multi_class="ovr"),
    "y_pred": y_pred_lgbm,
    "y_prob": y_prob_lgbm
}
models["LightGBM"] = lgbm_model

# Save model
joblib.dump(lgbm_model, "outputs/lightgbm.pkl")
print(f"       ✅ LightGBM trained & saved → outputs/lightgbm.pkl")

# ─────────────────────────────────────────────────────────────────
# 2. CATBOOST
# ─────────────────────────────────────────────────────────────────
print("\n  [2/4] Training CatBoost...")

catboost_model = CatBoostClassifier(
    iterations=500,
    learning_rate=0.1,
    depth=6,
    random_seed=42,
    verbose=0
)
catboost_model.fit(X_train, y_train)

# Predictions
y_pred_cat = catboost_model.predict(X_test)
y_prob_cat = catboost_model.predict_proba(X_test)

# Metrics
results["CatBoost"] = {
    "accuracy": accuracy_score(y_test, y_pred_cat),
    "precision": precision_score(y_test, y_pred_cat, average="weighted"),
    "recall": recall_score(y_test, y_pred_cat, average="weighted"),
    "f1": f1_score(y_test, y_pred_cat, average="weighted"),
    "roc_auc": roc_auc_score(y_test, y_prob_cat, multi_class="ovr", average="weighted"),
    "y_pred": y_pred_cat,
    "y_prob": y_prob_cat
}
models["CatBoost"] = catboost_model

# Save model
joblib.dump(catboost_model, "outputs/catboost.pkl")
print(f"       ✅ CatBoost trained & saved → outputs/catboost.pkl")

# ─────────────────────────────────────────────────────────────────
# 3. XGBOOST
# ─────────────────────────────────────────────────────────────────
print("\n  [3/4] Training XGBoost...")

xgboost_model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    eval_metric='mlogloss',
    random_state=42,
    use_label_encoder=False
)
xgboost_model.fit(X_train, y_train)

# Predictions
y_pred_xgb = xgboost_model.predict(X_test)
y_prob_xgb = xgboost_model.predict_proba(X_test)

# Metrics
results["XGBoost"] = {
    "accuracy": accuracy_score(y_test, y_pred_xgb),
    "precision": precision_score(y_test, y_pred_xgb, average="weighted"),
    "recall": recall_score(y_test, y_pred_xgb, average="weighted"),
    "f1": f1_score(y_test, y_pred_xgb, average="weighted"),
    "roc_auc": roc_auc_score(y_test, y_prob_xgb, multi_class="ovr"),
    "y_pred": y_pred_xgb,
    "y_prob": y_prob_xgb
}
models["XGBoost"] = xgboost_model

# Save model
joblib.dump(xgboost_model, "outputs/xgboost.pkl")
print(f"       ✅ XGBoost trained & saved → outputs/xgboost.pkl")

# ─────────────────────────────────────────────────────────────────
# 4. RANDOM FOREST
# ─────────────────────────────────────────────────────────────────
print("\n  [4/4] Training Random Forest...")

rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)

# Predictions
y_pred_rf = rf_model.predict(X_test)
y_prob_rf = rf_model.predict_proba(X_test)

# Metrics
results["Random Forest"] = {
    "accuracy": accuracy_score(y_test, y_pred_rf),
    "precision": precision_score(y_test, y_pred_rf, average="weighted"),
    "recall": recall_score(y_test, y_pred_rf, average="weighted"),
    "f1": f1_score(y_test, y_pred_rf, average="weighted"),
    "roc_auc": roc_auc_score(y_test, y_prob_rf, multi_class="ovr"),
    "y_pred": y_pred_rf,
    "y_prob": y_prob_rf
}
models["Random Forest"] = rf_model

# Save model
joblib.dump(rf_model, "outputs/random_forest.pkl")
print(f"       ✅ Random Forest trained & saved → outputs/random_forest.pkl")


# ═══════════════════════════════════════════════════════════════
# DISPLAY METRICS COMPARISON
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("  MODEL COMPARISON — METRICS")
print("=" * 70)

print(f"\n  {'Model':<15} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1-Score':>10} {'ROC-AUC':>10}")
print(f"  {'-'*70}")

for name, metrics in results.items():
    print(f"  {name:<15} {metrics['accuracy']*100:>9.2f}% {metrics['precision']*100:>9.2f}% {metrics['recall']*100:>9.2f}% {metrics['f1']*100:>9.2f}% {metrics['roc_auc']:>9.4f}")

# Find best model
best_model = max(results, key=lambda n: results[n]["accuracy"])
print(f"\n  🏆 Best Model (Accuracy): {best_model} ({results[best_model]['accuracy']*100:.2f}%)")

best_roc = max(results, key=lambda n: results[n]["roc_auc"])
print(f"  🏆 Best Model (ROC-AUC): {best_roc} ({results[best_roc]['roc_auc']:.4f})")


# ═══════════════════════════════════════════════════════════════
# DETAILED CLASSIFICATION REPORTS
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("  DETAILED CLASSIFICATION REPORTS")
print("=" * 70)

for name, metrics in results.items():
    print(f"\n  ▶ {name}")
    print("-" * 50)
    print(classification_report(y_test, metrics["y_pred"], target_names=CLASSES))


# ═══════════════════════════════════════════════════════════════
# VISUALIZATIONS
# ═══════════════════════════════════════════════════════════════

print("\n  Generating comparison plots...")

n_models = len(results)
model_names = list(results.keys())
colors = ["#3498DB", "#E74C3C", "#2ECC71", "#9B59B6"]  # Blue, Red, Green, Purple

# ── Figure 1: Confusion matrices ──────────────────────────────
fig1, axes = plt.subplots(2, 2, figsize=(14, 12))
fig1.suptitle("Confusion Matrices — Obesity Level Prediction", 
              fontsize=16, fontweight="bold", y=1.02)

for idx, (name, metrics) in enumerate(results.items()):
    ax = axes[idx // 2, idx % 2]
    cm_mat = confusion_matrix(y_test, metrics["y_pred"])
    sns.heatmap(cm_mat, annot=True, fmt="d", cmap="Blues", ax=ax,
                xticklabels=CLASSES_SHORT,
                yticklabels=CLASSES_SHORT,
                cbar=False, linewidths=0.5)
    ax.set_title(f"{name}\nAcc: {metrics['accuracy']*100:.1f}% | ROC-AUC: {metrics['roc_auc']:.4f}", 
                 fontsize=12, fontweight="bold")
    ax.set_xlabel("Predicted", fontsize=10)
    ax.set_ylabel("True", fontsize=10)
    ax.tick_params(labelsize=9)

plt.tight_layout()
plt.savefig("outputs/confusion_matrices.png", dpi=150, bbox_inches="tight")
print("  ✅ Saved → outputs/confusion_matrices.png")

# ── Figure 2: Metrics Comparison Bar Charts ───────────────────
fig2, axes = plt.subplots(2, 3, figsize=(18, 10))
fig2.suptitle("Model Performance Comparison", fontsize=16, fontweight="bold")

metrics_list = ["accuracy", "precision", "recall", "f1", "roc_auc"]
titles = ["Accuracy", "Precision (weighted)", "Recall (weighted)", 
          "F1-Score (weighted)", "ROC-AUC (ovr, weighted)"]

for idx, (metric, title) in enumerate(zip(metrics_list, titles)):
    ax = axes[idx // 3, idx % 3]
    values = [results[name][metric] * 100 for name in model_names]
    bars = ax.bar(model_names, values, color=colors, edgecolor="white", linewidth=1.5)
    ax.set_ylim(0, 115)
    ax.set_ylabel(f"{title} (%)", fontsize=10)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.tick_params(axis="x", rotation=15)
    
    # Add value labels on bars
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{val:.2f}%", ha="center", fontsize=10, fontweight="bold")
    
    ax.grid(axis="y", alpha=0.3)

# Hide the last empty subplot
axes[1, 2].axis("off")

plt.tight_layout()
plt.savefig("outputs/metrics_comparison.png", dpi=150, bbox_inches="tight")
print("  ✅ Saved → outputs/metrics_comparison.png")

# ── Figure 3: Combined Radar Chart Style Comparison ───────────
fig3, ax = plt.subplots(figsize=(12, 8))

x = np.arange(len(model_names))
width = 0.15

metrics_for_grouped = [
    ("Accuracy", "accuracy"),
    ("Precision", "precision"),
    ("Recall", "recall"),
    ("F1-Score", "f1"),
    ("ROC-AUC", "roc_auc")
]

grouped_colors = ["#3498DB", "#E74C3C", "#2ECC71", "#9B59B6", "#F39C12"]

for i, (label, metric) in enumerate(metrics_for_grouped):
    values = [results[name][metric] * 100 for name in model_names]
    bars = ax.bar(x + i * width - 2*width, values, width, label=label, 
                 color=grouped_colors[i], edgecolor="white", linewidth=1)

ax.set_ylabel("Score (%)", fontsize=12)
ax.set_title("All Metrics Comparison", fontsize=14, fontweight="bold")
ax.set_xticks(x + width * 2)
ax.set_xticklabels(model_names, fontsize=11)
ax.legend(loc="lower right", fontsize=10)
ax.set_ylim(0, 110)
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig("outputs/all_metrics_comparison.png", dpi=150, bbox_inches="tight")
print("  ✅ Saved → outputs/all_metrics_comparison.png")

# ── Figure 4: Feature Importance for Each Model ───────────────
fig4, axes = plt.subplots(2, 2, figsize=(16, 14))
fig4.suptitle("Feature Importance Comparison", fontsize=16, fontweight="bold", y=1.02)

# Get feature importances
for idx, (name, model) in enumerate(models.items()):
    ax = axes[idx // 2, idx % 2]
    
    # Get feature importance based on model type
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    elif hasattr(model, 'get_feature_importance'):
        importances = model.get_feature_importance()
    else:
        importances = np.zeros(len(X_train.columns))
    
    # Create DataFrame for sorting
    importance_df = pd.DataFrame({
        'Feature': X_train.columns,
        'Importance': importances
    }).sort_values('Importance', ascending=True)
    
    # Color bars based on importance
    median_imp = importance_df['Importance'].median()
    bar_colors = ['#E74C3C' if x > median_imp else '#3498DB' 
                  for x in importance_df['Importance']]
    
    ax.barh(importance_df['Feature'], importance_df['Importance'],
            color=bar_colors, edgecolor="white", linewidth=1.2)
    ax.axvline(x=median_imp, color="black", linestyle="--", 
               alpha=0.6, label=f"Median: {median_imp:.2f}")
    ax.set_title(f"{name} — Feature Importance", fontsize=12, fontweight="bold")
    ax.set_xlabel("Importance Score", fontsize=10)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="x", alpha=0.3)

plt.tight_layout()
plt.savefig("outputs/feature_importance_comparison.png", dpi=150, bbox_inches="tight")
print("  ✅ Saved → outputs/feature_importance_comparison.png")

# Close all figures to free memory
plt.close('all')

print("\n" + "=" * 70)
print("  ✅ COMPARISON COMPLETE!")
print("=" * 70)
print(f"\n  📊 Summary:")
print(f"     • Best Accuracy : {best_model} ({results[best_model]['accuracy']*100:.2f}%)")
print(f"     • Best ROC-AUC  : {best_roc} ({results[best_roc]['roc_auc']:.4f})")
print(f"\n  📁 Saved Models:")
print(f"     • outputs/lightgbm.pkl")
print(f"     • outputs/catboost.pkl")
print(f"     • outputs/xgboost.pkl")
print(f"     • outputs/random_forest.pkl")
print(f"\n  📈 Saved Visualizations:")
print(f"     • outputs/confusion_matrices.png")
print(f"     • outputs/metrics_comparison.png")
print(f"     • outputs/all_metrics_comparison.png")
print(f"     • outputs/feature_importance_comparison.png")
print("=" * 70)

