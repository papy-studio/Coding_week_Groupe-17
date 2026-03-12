# ═══════════════════════════════════════════════════════════════
# MODÈLE — CATBOOST CLASSIFIER
# Obesity Risk Estimation | Coding Week 2026
# ═══════════════════════════════════════════════════════════════

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.model_selection import cross_val_score

# ── 1. Charger la data ──────────────────────────────────────────
X_train = pd.read_csv('data/X_train.csv')
X_test  = pd.read_csv('data/X_test.csv')
y_train = pd.read_csv('data/y_train.csv').squeeze()
y_test  = pd.read_csv('data/y_test.csv').squeeze()

print("=" * 60)
print("   CATBOOST — Obesity Risk Estimation")
print("=" * 60)
print(f"  Patients entraînement : {X_train.shape[0]}")
print(f"  Patients test         : {X_test.shape[0]}")
print(f"  Nombre de features    : {X_train.shape[1]}")

# ── 2. Validation croisée ───────────────────────────────────────
# CatBoost n'a pas besoin de normalisation
# 3 folds suffisent pour valider la stabilité du modèle
model_cv = CatBoostClassifier(
    iterations=300,      # réduit pour la CV → plus rapide
    learning_rate=0.1,
    depth=6,
    random_seed=42,
    verbose=0
)
cv_scores = cross_val_score(
    model_cv, X_train, y_train,
    cv=3,
    scoring='accuracy'
)
print(f"\n  CV Scores : {cv_scores.round(3)}")
print(f"  Moyenne   : {cv_scores.mean():.3f}")
print(f"  Stabilité : ±{cv_scores.std():.3f}")

# ── 3. Entraîner le modèle final ────────────────────────────────
model = CatBoostClassifier(
    iterations=500,
    learning_rate=0.1,
    depth=6,
    random_seed=42,
    verbose=0
)
model.fit(X_train, y_train)

# ── 4. Prédictions ──────────────────────────────────────────────
y_pred       = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

# ── 5. Métriques ────────────────────────────────────────────────
accuracy = accuracy_score(y_test, y_pred)
roc_auc  = roc_auc_score(
    y_test, y_pred_proba,
    multi_class='ovr', average='weighted'
)

print("\n" + "=" * 60)
print("   RÉSULTATS FINAUX")
print("=" * 60)
print(f"  Accuracy           : {accuracy*100:.2f}%")
print(f"  ROC-AUC            : {roc_auc:.4f}")
print(f"  CV Score (moyenne) : {cv_scores.mean()*100:.2f}%")
print(f"  CV Stabilité       : ±{cv_scores.std()*100:.2f}%")

class_names = ['Insuf.', 'Normal', 'Obese_I',
               'Obese_II', 'Obese_III', 'Over_I', 'Over_II']
print(classification_report(y_test, y_pred, target_names=class_names))

# ── 6. Graphiques ───────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('CatBoost — Analyse des Performances',
             fontsize=14, fontweight='bold')

# Graphique 1 : CV Scores
folds      = [f'Fold {i+1}' for i in range(3)]
bar_colors = ['#2ECC71' if s >= cv_scores.mean()
              else '#E74C3C' for s in cv_scores]

axes[0].bar(folds, cv_scores * 100, color=bar_colors,
            edgecolor='white', linewidth=1.5)
axes[0].axhline(y=cv_scores.mean() * 100, color='black',
                linestyle='--', linewidth=1.5,
                label=f'Moyenne = {cv_scores.mean()*100:.2f}%')
axes[0].fill_between(range(3),
    (cv_scores.mean() - cv_scores.std()) * 100,
    (cv_scores.mean() + cv_scores.std()) * 100,
    alpha=0.1, color='blue', label='±1 écart-type')
axes[0].set_title('Stabilité — Cross Validation (3 Folds)',
                  fontweight='bold')
axes[0].set_ylabel('Accuracy (%)')
axes[0].set_ylim(70, 100)
axes[0].legend()
axes[0].grid(axis='y', alpha=0.3)

# Graphique 2 : Importance des features
importances   = model.get_feature_importance()
importance_df = pd.DataFrame({
    'Feature'   : X_train.columns,
    'Importance': importances
}).sort_values('Importance', ascending=True)

median_imp  = importance_df['Importance'].median()
bar_colors2 = ['#E74C3C' if x > median_imp
               else '#3498DB' for x in importance_df['Importance']]

axes[1].barh(importance_df['Feature'], importance_df['Importance'],
             color=bar_colors2, edgecolor='white', linewidth=1.2)
axes[1].axvline(x=median_imp, color='black', linestyle='--',
                alpha=0.6, label='Médiane')
axes[1].set_title('Importance des Features\n(score CatBoost natif)',
                  fontweight='bold')
axes[1].set_xlabel('Importance')
axes[1].legend()
axes[1].grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('data/catboost_results.png', dpi=150, bbox_inches='tight')
plt.show()