"""
╔══════════════════════════════════════════════════════════════╗
║         OBESITY LEVEL PREDICTION — FULL ML PIPELINE         ║
╚══════════════════════════════════════════════════════════════╝
Dataset  : UCI Obesity Levels (id=544)
Target   : NObeyesdad (7 classes)
Models   : Random Forest, Gradient Boosting, XGBoost, Logistic Regression
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

from ucimlrepo import fetch_ucirepo
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

import os
os.makedirs("data",    exist_ok=True)
os.makedirs("outputs", exist_ok=True)


# ══════════════════════════════════════════════════════════════
# 1. CHARGEMENT & ENCODAGE
# ══════════════════════════════════════════════════════════════
print("=" * 55)
print("  ÉTAPE 1 — Chargement & encodage")
print("=" * 55)

dataset    = fetch_ucirepo(id=544)
df         = pd.concat([dataset.data.features, dataset.data.targets], axis=1)
df_encoded = df.copy()

# Encodage binaire
binary_cols = ["family_history_with_overweight", "FAVC", "SMOKE", "SCC"]
for col in binary_cols:
    df_encoded[col] = df_encoded[col].map({"yes": 1, "no": 0})

# Label Encoding des colonnes catégorielles
le = LabelEncoder()
for col in ["Gender", "CAEC", "CALC", "MTRANS"]:
    df_encoded[col] = le.fit_transform(df_encoded[col])

# Encodage de la cible (on garde le mapping pour l'affichage)
le_target  = LabelEncoder()
df_encoded["NObeyesdad"] = le_target.fit_transform(df_encoded["NObeyesdad"])
class_names = le_target.classes_

print(f"✅ Dataset chargé : {df_encoded.shape[0]} lignes × {df_encoded.shape[1]} colonnes")
print(f"   Classes cible  : {list(class_names)}\n")


# ══════════════════════════════════════════════════════════════
# 2. OPTIMISATION MÉMOIRE
# ══════════════════════════════════════════════════════════════
def optimize_memory(df):
    before = df.memory_usage(deep=True).sum() / 1024
    for col in df.select_dtypes(include=["float64"]).columns:
        df[col] = df[col].astype("float32")
    for col in df.select_dtypes(include=["int64"]).columns:
        df[col] = df[col].astype("int32")
    after = df.memory_usage(deep=True).sum() / 1024
    print(f"   Mémoire avant : {before:.1f} KB")
    print(f"   Mémoire après : {after:.1f} KB  (−{((before-after)/before*100):.1f}%)\n")
    return df

print("=" * 55)
print("  ÉTAPE 2 — Optimisation mémoire")
print("=" * 55)
df_encoded = optimize_memory(df_encoded)


# ══════════════════════════════════════════════════════════════
# 3. SPLIT TRAIN / TEST
# ══════════════════════════════════════════════════════════════
print("=" * 55)
print("  ÉTAPE 3 — Split Train / Test")
print("=" * 55)

X = df_encoded.drop(columns=["NObeyesdad"])
y = df_encoded["NObeyesdad"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"   Total  : {len(df_encoded)} lignes")
print(f"   Train  : {X_train.shape[0]} lignes  (80%)")
print(f"   Test   : {X_test.shape[0]} lignes  (20%)\n")

# Sauvegarde des splits
X_train.to_csv("data/X_train.csv", index=False)
X_test.to_csv("data/X_test.csv",   index=False)
y_train.to_csv("data/y_train.csv", index=False)
y_test.to_csv("data/y_test.csv",   index=False)
print("   ✅ Splits sauvegardés dans data/\n")


# ══════════════════════════════════════════════════════════════
# 4. ENTRAÎNEMENT — PLUSIEURS MODÈLES
# ══════════════════════════════════════════════════════════════
print("=" * 55)
print("  ÉTAPE 4 — Entraînement des modèles")
print("=" * 55)

models = {
    "Random Forest":       RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
    "Gradient Boosting":   GradientBoostingClassifier(n_estimators=200, random_state=42),
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1),
}

# Optionally add XGBoost if installed
try:
    from xgboost import XGBClassifier
    models["XGBoost"] = XGBClassifier(
        n_estimators=200, random_state=42, n_jobs=-1,
        eval_metric="mlogloss", verbosity=0
    )
    print("   XGBoost détecté ✅")
except ImportError:
    print("   XGBoost non installé (pip install xgboost) — ignoré.")

results = {}

for name, model in models.items():
    print(f"\n  ▶ {name} ...")
    model.fit(X_train, y_train)
    y_pred   = model.predict(X_test)
    acc      = accuracy_score(y_test, y_pred)
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="accuracy", n_jobs=-1)
    results[name] = {
        "model":    model,
        "y_pred":   y_pred,
        "accuracy": acc,
        "cv_mean":  cv_scores.mean(),
        "cv_std":   cv_scores.std(),
    }
    print(f"     Test accuracy  : {acc:.4f}")
    print(f"     CV  accuracy   : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")


# ══════════════════════════════════════════════════════════════
# 5. COMPARAISON DES MODÈLES
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("  ÉTAPE 5 — Comparaison")
print("=" * 55)

comparison = pd.DataFrame([
    {
        "Modèle":         name,
        "Test Accuracy":  f"{r['accuracy']:.4f}",
        "CV Mean":        f"{r['cv_mean']:.4f}",
        "CV Std":         f"±{r['cv_std']:.4f}",
    }
    for name, r in results.items()
])
print(comparison.to_string(index=False))

best_name = max(results, key=lambda n: results[n]["accuracy"])
best      = results[best_name]
print(f"\n  🏆 Meilleur modèle : {best_name}  ({best['accuracy']:.4f})\n")


# ══════════════════════════════════════════════════════════════
# 6. RAPPORT DÉTAILLÉ DU MEILLEUR MODÈLE
# ══════════════════════════════════════════════════════════════
print("=" * 55)
print(f"  ÉTAPE 6 — Rapport : {best_name}")
print("=" * 55)

print(classification_report(
    y_test, best["y_pred"],
    target_names=class_names
))


# ══════════════════════════════════════════════════════════════
# 7. VISUALISATIONS
# ══════════════════════════════════════════════════════════════
print("=" * 55)
print("  ÉTAPE 7 — Génération des graphiques")
print("=" * 55)

fig = plt.figure(figsize=(18, 14))
fig.suptitle("Obesity Level Prediction — ML Report", fontsize=16, fontweight="bold", y=0.98)
gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.35)

# ── (a) Comparaison accuracy ──────────────────────────────────
ax1   = fig.add_subplot(gs[0, 0])
names = list(results.keys())
accs  = [results[n]["accuracy"] for n in names]
bars  = ax1.barh(names, accs, color=["#4C72B0","#DD8452","#55A868","#C44E52"][:len(names)])
ax1.set_xlim(0, 1)
ax1.set_xlabel("Test Accuracy")
ax1.set_title("(a) Comparaison des modèles")
for bar, acc in zip(bars, accs):
    ax1.text(acc + 0.005, bar.get_y() + bar.get_height()/2,
             f"{acc:.3f}", va="center", fontsize=10)

# ── (b) CV scores avec barres d'erreur ───────────────────────
ax2     = fig.add_subplot(gs[0, 1])
cv_mean = [results[n]["cv_mean"] for n in names]
cv_std  = [results[n]["cv_std"]  for n in names]
ax2.bar(names, cv_mean, yerr=cv_std, capsize=5,
        color=["#4C72B0","#DD8452","#55A868","#C44E52"][:len(names)])
ax2.set_ylim(0, 1)
ax2.set_ylabel("CV Accuracy")
ax2.set_title("(b) Cross-Validation (5-fold)")
ax2.tick_params(axis="x", rotation=15)

# ── (c) Matrice de confusion du meilleur modèle ───────────────
ax3 = fig.add_subplot(gs[1, 0])
cm  = confusion_matrix(y_test, best["y_pred"])
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
disp.plot(ax=ax3, colorbar=False, xticks_rotation=45)
ax3.set_title(f"(c) Confusion Matrix — {best_name}")

# ── (d) Feature Importances (si dispo) ────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
if hasattr(best["model"], "feature_importances_"):
    importances = pd.Series(
        best["model"].feature_importances_,
        index=X.columns
    ).sort_values()
    importances.plot(kind="barh", ax=ax4, color="#4C72B0")
    ax4.set_title(f"(d) Feature Importances — {best_name}")
    ax4.set_xlabel("Importance")
else:
    coef = np.abs(best["model"].coef_).mean(axis=0)
    importances = pd.Series(coef, index=X.columns).sort_values()
    importances.plot(kind="barh", ax=ax4, color="#4C72B0")
    ax4.set_title(f"(d) Coef. moyens — {best_name}")
    ax4.set_xlabel("|Coefficient|")

plt.savefig("outputs/ml_report.png", dpi=150, bbox_inches="tight")
plt.show()
print("   ✅ Graphique sauvegardé : outputs/ml_report.png\n")


# ══════════════════════════════════════════════════════════════
# 8. SAUVEGARDE DU MEILLEUR MODÈLE
# ══════════════════════════════════════════════════════════════
import joblib

joblib.dump(best["model"], f"outputs/best_model_{best_name.replace(' ','_')}.pkl")
print("=" * 55)
print("  ÉTAPE 8 — Sauvegarde")
print("=" * 55)
print(f"   ✅ Modèle sauvegardé : outputs/best_model_{best_name.replace(' ','_')}.pkl")
print(f"\n{'='*55}")
print(f"  ✅ Pipeline terminé ! Meilleur modèle : {best_name}")
print(f"     Accuracy : {best['accuracy']:.4f}")
print(f"{'='*55}")
