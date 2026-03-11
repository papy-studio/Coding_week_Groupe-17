# ═══════════════════════════════════════════════════════════════
# MODÈLE — RÉGRESSION LOGISTIQUE
# Obesity Risk Estimation | Coding Week 2026
# ═══════════════════════════════════════════════════════════════

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score
)
from sklearn.model_selection import cross_val_score

# ── 1. Charger la data ──────────────────────────────────────────
X_train = pd.read_csv('data/X_train.csv')
X_test  = pd.read_csv('data/X_test.csv')
y_train = pd.read_csv('data/y_train.csv').squeeze()
y_test  = pd.read_csv('data/y_test.csv').squeeze()

print("=" * 60)
print("   RÉGRESSION LOGISTIQUE — Obesity Risk Estimation")
print("=" * 60)
print(f"  Patients entraînement : {X_train.shape[0]}")
print(f"  Patients test         : {X_test.shape[0]}")
print(f"  Nombre de features    : {X_train.shape[1]}")

# ── 2. Normalisation ────────────────────────────────────────────
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# ── 3. Validation croisée ───────────────────────────────────────
# Divise le train en 5 parties → entraîne 5 fois
# Donne une mesure fiable de la vraie performance
model_cv = LogisticRegression(
    max_iter=2000,
    class_weight='balanced',
    random_state=42
)
cv_scores = cross_val_score(
    model_cv, X_train_scaled, y_train,
    cv=5, scoring='accuracy'
)

# ── 4. Entraîner le modèle final ────────────────────────────────
model = LogisticRegression(
    max_iter=2000,
    class_weight='balanced',
    random_state=42
)
model.fit(X_train_scaled, y_train)

# ── 5. Prédictions ──────────────────────────────────────────────
y_pred       = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)

# ── 6. Métriques ────────────────────────────────────────────────
accuracy = accuracy_score(y_test, y_pred)
roc_auc  = roc_auc_score(
    y_test, y_pred_proba,
    multi_class='ovr', average='weighted'
)

print("\n" + "=" * 60)
print("   RÉSULTATS")
print("=" * 60)
print(f"  Accuracy           : {accuracy*100:.2f}%")
print(f"  ROC-AUC            : {roc_auc:.4f}")
print(f"  CV Score (moyenne) : {cv_scores.mean()*100:.2f}%")
print(f"  CV Stabilité       : ±{cv_scores.std()*100:.2f}%")
print(classification_report(
    y_test, y_pred,
    target_names=['Insuf.', 'Normal', 'Obese_I',
                  'Obese_II', 'Obese_III', 'Over_I', 'Over_II']
))

# ── 7. Graphique 1 — CV Scores ──────────────────────────────────
# Montre la stabilité du modèle sur les 5 folds
# Un bon modèle = barres proches les unes des autres
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Régression Logistique — Analyse des Performances',
             fontsize=14, fontweight='bold', y=1.02)

folds = [f'Fold {i+1}' for i in range(5)]
bar_colors = ['#2ECC71' if s >= cv_scores.mean()
              else '#E74C3C' for s in cv_scores]

axes[0].bar(folds, cv_scores * 100, color=bar_colors,
            edgecolor='white', linewidth=1.5)
axes[0].axhline(y=cv_scores.mean() * 100, color='black',
                linestyle='--', linewidth=1.5,
                label=f'Moyenne = {cv_scores.mean()*100:.2f}%')
axes[0].fill_between(range(5),
    (cv_scores.mean() - cv_scores.std()) * 100,
    (cv_scores.mean() + cv_scores.std()) * 100,
    alpha=0.1, color='blue', label='±1 écart-type')
axes[0].set_title('Stabilité — Cross Validation (5 Folds)',
                  fontweight='bold')
axes[0].set_ylabel('Accuracy (%)')
axes[0].set_ylim(70, 100)
axes[0].legend()
axes[0].grid(axis='y', alpha=0.3)

# ── 8. Graphique 2 — Importance des features ────────────────────
# Rouge = au-dessus de la médiane → feature importante
# Bleu  = en-dessous de la médiane → feature moins importante
importances = np.abs(model.coef_).mean(axis=0)
importance_df = pd.DataFrame({
    'Feature'   : X_train.columns,
    'Importance': importances
}).sort_values('Importance', ascending=True)

median_imp = importance_df['Importance'].median()
bar_colors2 = ['#E74C3C' if x > median_imp
               else '#3498DB' for x in importance_df['Importance']]

axes[1].barh(importance_df['Feature'], importance_df['Importance'],
             color=bar_colors2, edgecolor='white', linewidth=1.2)
axes[1].axvline(x=median_imp, color='black', linestyle='--',
                alpha=0.6, label='Médiane')
axes[1].set_title('Importance des Features\n(|poids moyens| sur 7 classes)',
                  fontweight='bold')
axes[1].set_xlabel('Importance (valeur absolue des poids)')
axes[1].legend()
axes[1].grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('data analyse 1/logistic_results.png',
            dpi=150, bbox_inches='tight')
plt.show()

print("\n✅ Graphique sauvegardé → data analyse 1/logistic_results.png")
print(f"\n  Top 3 features les plus importantes :")
top3 = importance_df.sort_values('Importance', ascending=False).head(3)
for i, (_, row) in enumerate(top3.iterrows(), 1):
    print(f"  {i}. {row['Feature']:30} : {row['Importance']:.4f}")


# ── 9. SHAP Explainability ──────────────────────────────────────
import shap

print("\nAnalyse SHAP en cours...")

explainer   = shap.LinearExplainer(model, X_train_scaled)
shap_values = explainer.shap_values(X_test_scaled)

shap.summary_plot(
    shap_values,
    X_test_scaled,
    feature_names=X_train.columns.tolist(),
    plot_type="bar",
    show=False
)
plt.title("SHAP — Importance globale des features",
          fontweight='bold')
plt.tight_layout()
plt.savefig('data analyse 1/shap_importance.png', dpi=150, bbox_inches='tight')
plt.show()
print("Graphique SHAP sauvegardé.")