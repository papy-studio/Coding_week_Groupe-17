# DOCUMENTATION PROMPT ENGINEERING
## Projet : MediObes - Application d'Aide à la Décision Médicale
### Coding Week 2026 - Groupe 17

---

## 📌 Introduction

Nous sommes un groupe d'étudiants en coding week, **pas des experts en programmation**. Nous avons utilisé l'IA (ChatGPT) pour nous aider à développer ce projet. Ce document présente tous les prompts que nous avons utilisés, nos difficultés, et ce que l'IA nous a appris.

**Notre niveau :** Débutants en Python, première expérience avec Streamlit et le machine learning.

---

## INFORMATIONS SUR LE DATASET

Nous avons consulté la page officielle du dataset sur l'UCI :
[https://archive.ics.uci.edu/dataset/544/estimation+of+obesity+levels+based+on+eating+habits+and+physical+condition](https://archive.ics.uci.edu/dataset/544/estimation+of+obesity+levels+based+on+eating+habits+and+physical+condition)

**Ce que nous avons appris de la documentation :**
- **Source** : Données collectées au Mexique, au Pérou et en Colombie.
- **Composition** : **77% des données sont synthétiques** (générées avec l'outil Weka et le filtre SMOTE) et 23% proviennent de vraies personnes via une plateforme web.
- **Taille** : 2111 instances, 16 attributs (features).
- **Valeurs manquantes** : Aucune (ce qui nous a simplifié la tâche).
- **Variable cible** : `NObesidad` avec 7 niveaux d'obésité :
  - Insufficient Weight
  - Normal Weight
  - Overweight Level I
  - Overweight Level II
  - Obesity Type I
  - Obesity Type II
  - Obesity Type III
- **Types de variables** : Mélange de variables continues (Âge, Taille, Poids) et catégorielles (Sexe, Antécédents familiaux, Habitudes alimentaires, etc.).

**Prompt utilisé pour trouver ces informations :**
"Nous utilisons le dataset UCI sur l'obésité (ID 544). Peux-tu nous donner plus d'informations sur ce dataset ? Sa provenance, sa composition, et s'il y a des particularités à connaître ?"

text

---

## PARTIE 1 : ANALYSE DES DONNÉES (DATA ANALYSIS & PREPROCESSING)

### 👤 Membre 1 - Exploration et préparation des données

---

### Prompt 1.1 : Charger et découvrir le dataset

**Ce qu'on a tapé dans ChatGPT :**
"Salut, on doit faire un projet sur l'obésité avec un dataset de l'UCI.
On est pas très forts en code.
Peux-tu nous donner un script simple pour :

Charger le dataset

Voir à quoi ressemblent les données

Vérifier s'il y a des valeurs manquantes

Connaître les types de données (texte, nombre, etc.)

On veut des commentaires dans le code pour comprendre ce qui se passe."

text

**Ce que ChatGPT nous a répondu :**
```python
import pandas as pd

# Charger le fichier CSV
df = pd.read_csv("data/ObesityDataSet.csv")

# Afficher les 5 premières lignes pour voir la structure
print("🔍 PREMIÈRES LIGNES :")
print(df.head())
print("-" * 50)

# Afficher des infos générales (types de données, valeurs non-nulles)
print("📊 INFORMATIONS SUR LES COLONNES :")
print(df.info())
print("-" * 50)

# Vérifier s'il y a des valeurs manquantes
print("❓ VALEURS MANQUANTES PAR COLONNE :")
print(df.isnull().sum())
print("-" * 50)

# Statistiques de base pour les colonnes numériques
print("📈 STATISTIQUES DESCRIPTIVES :")
print(df.describe())
Notre réaction : "Ah cool, ça marche ! On voit qu'il y a 2111 lignes et pas de valeurs manquantes. C'est déjà ça de gagné."

Prompt 1.2 : Vérifier si les classes sont équilibrées
Ce qu'on a tapé dans ChatGPT :

text
"Le dataset a 7 niveaux d'obésité différents. 
On veut savoir si certaines catégories ont beaucoup plus de patients que d'autres.
Si c'est déséquilibré, ça peut poser problème pour le machine learning.

Peux-tu nous montrer :
- Le nombre de patients dans chaque catégorie
- Le pourcentage pour chaque catégorie
- Un graphique pour visualiser

Et explique-nous ce que ça signifie."
Ce que ChatGPT nous a répondu :

python
import matplotlib.pyplot as plt

# Compter le nombre de patients par catégorie
print("=== DISTRIBUTION DES CLASSES (NOMBRE) ===")
print(df['NObeyesdad'].value_counts())
print()

# Calculer les pourcentages
print("=== DISTRIBUTION DES CLASSES (POURCENTAGE) ===")
pourcentages = df['NObeyesdad'].value_counts(normalize=True).mul(100).round(1)
print(pourcentages)
print()

# Créer un graphique à barres
plt.figure(figsize=(10, 5))
df['NObeyesdad'].value_counts().plot(kind='bar', color='steelblue')
plt.title("Distribution des niveaux d'obésité", fontsize=14)
plt.xlabel("Niveau d'obésité")
plt.ylabel("Nombre de patients")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
Explication de l'IA :

text
📢 INTERPRÉTATION :
- Les pourcentages vont de 12.9% à 16.6%
- C'est considéré comme "équilibré" (aucune classe ne dépasse 20%)
- BONNE NOUVELLE : vous n'aurez pas besoin de faire de rééquilibrage compliqué
- Vous pouvez entraîner vos modèles directement avec ces données
Notre réaction : "Ouf ! On avait peur que ce soit déséquilibré. L'IA nous a rassurés."

Prompt 1.3 : Analyser les variables numériques (âge, poids, taille...)
Ce qu'on a tapé dans ChatGPT :

text
"On veut comprendre les variables numériques comme l'âge, le poids, la taille.
Peux-tu nous aider à :
1. Voir leur distribution (est-ce que c'est normal ou bizarre ?)
2. Détecter s'il y a des valeurs aberrantes (outliers)
3. Voir les corrélations entre elles

On veut des graphiques parce que c'est plus facile à comprendre."
Ce que ChatGPT nous a répondu :

python
import matplotlib.pyplot as plt
import seaborn as sns

# Liste des colonnes numériques
colonnes_numeriques = ['Age', 'Height', 'Weight', 'FCVC', 'NCP', 'CH2O', 'FAF', 'TUE']

# 1. Histogrammes pour voir la distribution
df[colonnes_numeriques].hist(figsize=(14, 10), bins=20, color='steelblue', edgecolor='black')
plt.suptitle("Distribution des variables numériques", fontsize=16)
plt.tight_layout()
plt.show()

# 2. Boxplots pour détecter les outliers
plt.figure(figsize=(12, 6))
df[colonnes_numeriques].boxplot()
plt.title("Détection des outliers", fontsize=14)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 3. Matrice de corrélation
plt.figure(figsize=(10, 8))
sns.heatmap(df[colonnes_numeriques].corr(), annot=True, fmt=".2f", 
            cmap="coolwarm", square=True)
plt.title("Matrice de corrélation", fontsize=14)
plt.tight_layout()
plt.show()
Ce qu'on a observé :

Âge : distribution normale (beaucoup de jeunes adultes)

Poids : quelques valeurs très élevées (outliers)

Taille : corrélation forte avec le poids (logique)

FCVC, NCP : quelques valeurs étranges

Prompt 1.4 : Gestion des outliers - question importante !
Ce qu'on a tapé dans ChatGPT :

text
"On voit des outliers dans le poids (des personnes très lourdes).
Normalement, en stats, on supprime les outliers.
Mais c'est un dataset médical sur l'obésité.

QUESTION : Est-ce qu'on doit supprimer ces personnes très lourdes ?
Ça va fausser nos modèles si on les garde ?
On sait pas quoi faire, aide-nous !"
Ce que ChatGPT nous a répondu (explication super importante) :

text
⚠️ ATTENTION - CONTEXTE MÉDICAL ⚠️

Dans un dataset médical sur l'obésité, les "outliers" ne sont PAS des erreurs !
Ce sont des patients avec une obésité sévère, exactement ce que vous voulez prédire.

SI VOUS SUPPRIMEZ CES PATIENTS :
❌ Votre modèle ne saura pas reconnaître l'obésité sévère
❌ Vous allez under-estimer les risques
❌ Votre modèle sera inutile en pratique

RECOMMANDATION :
✅ GARDEZ tous les outliers
✅ C'est normal d'avoir des poids élevés dans ce contexte
✅ La médecine, c'est justement d'étudier les cas extrêmes

RÈGLE D'OR : Ne supprimez JAMAIS des données médicales sans raison valide !
Notre réaction : "Ouf, on allait faire une grosse bêtise ! L'IA nous a sauvés."

Prompt 1.5 : Encoder les variables catégorielles
Ce qu'on a tapé dans ChatGPT :

text
"Le dataset a des colonnes avec du texte :
- 'Gender' : Male/Female
- 'SMOKE' : yes/no
- 'CAEC' : Sometimes/Frequently/Always/No
- etc.

Pour le machine learning, il faut des nombres.
Peux-tu nous expliquer comment faire ?
Il y a différents types de colonnes, on veut bien faire."
Ce que ChatGPT nous a répondu :

python
from sklearn.preprocessing import LabelEncoder

# Copie du dataset pour l'encodage
df_encoded = df.copy()

print("=" * 60)
print("ÉTAPE 1 : COLONNES BINAIRES (yes/no)")
print("=" * 60)
print("Pour ces colonnes, on utilise .map() qui est simple et efficace")

colonnes_binaires = ['family_history_with_overweight', 'FAVC', 'SMOKE', 'SCC']
for col in colonnes_binaires:
    df_encoded[col] = df_encoded[col].map({'yes': 1, 'no': 0})
    print(f"✅ {col}: yes→1, no→0")

print("\n" + "=" * 60)
print("ÉTAPE 2 : COLONNES CATÉGORIELLES (plus de 2 valeurs)")
print("=" * 60)
print("Pour ces colonnes, on utilise LabelEncoder()")
print("Il attribue un numéro unique à chaque catégorie (0,1,2,3...)")

colonnes_categorielles = ['Gender', 'CAEC', 'CALC', 'MTRANS']
le = LabelEncoder()
for col in colonnes_categorielles:
    df_encoded[col] = le.fit_transform(df_encoded[col])
    valeurs_uniques = df[col].unique()
    print(f"✅ {col}: {len(valeurs_uniques)} catégories → {valeurs_uniques}")

print("\n" + "=" * 60)
print("ÉTAPE 3 : ENCODER LA VARIABLE CIBLE")
print("=" * 60)
print("La variable qu'on veut prédire (NObeyesdad) doit aussi être encodée")

df_encoded['NObeyesdad'] = le.fit_transform(df_encoded['NObeyesdad'])
print("✅ Variable cible encodée")

print("\n" + "=" * 60)
print("RÉSULTAT FINAL")
print("=" * 60)
print(df_encoded.head())
Explication supplémentaire de l'IA :

text
📝 POURQUOI DEUX MÉTHODES DIFFÉRENTES ?

1. .map() pour les colonnes binaires :
   - Plus simple et plus rapide
   - On contrôle exactement les valeurs (1 pour yes, 0 pour no)
   - Pas de risque de mauvaise interprétation

2. LabelEncoder() pour les catégories multiples :
   - Convertit automatiquement toutes les valeurs
   - Parfait pour les colonnes avec 3, 4 ou 5 catégories
   - Attention : crée un ordre (0,1,2,3) mais c'est OK pour les modèles d'arbres
Prompt 1.6 : Optimiser la mémoire du dataframe
Ce qu'on a tapé dans ChatGPT :

text
"Le prof nous a demandé de créer une fonction optimize_memory().
Il faut convertir :
- float64 → float32
- int64 → int32

Et afficher la mémoire avant/après et le pourcentage gagné.
On comprend pas trop pourquoi faire ça, mais c'est dans le sujet.

Peux-tu nous aider à écrire cette fonction ?"
Ce que ChatGPT nous a répondu :

python
def optimize_memory(df):
    """
    Optimise la mémoire d'un dataframe en réduisant les types
    float64 → float32, int64 → int32
    """
    print("=" * 60)
    print("OPTIMISATION MÉMOIRE")
    print("=" * 60)
    
    # Mémoire avant optimisation
    memoire_avant = df.memory_usage(deep=True).sum() / 1024
    print(f"📊 Mémoire AVANT : {memoire_avant:.1f} KB")
    
    # Optimiser les colonnes float64
    colonnes_float = df.select_dtypes(include=['float64']).columns
    for col in colonnes_float:
        df[col] = df[col].astype('float32')
    print(f"✅ {len(colonnes_float)} colonnes float64 → float32")
    
    # Optimiser les colonnes int64
    colonnes_int = df.select_dtypes(include=['int64']).columns
    for col in colonnes_int:
        df[col] = df[col].astype('int32')
    print(f"✅ {len(colonnes_int)} colonnes int64 → int32")
    
    # Mémoire après optimisation
    memoire_apres = df.memory_usage(deep=True).sum() / 1024
    pourcentage_gagne = ((memoire_avant - memoire_apres) / memoire_avant) * 100
    
    print(f"📊 Mémoire APRÈS  : {memoire_apres:.1f} KB")
    print(f"💰 GAIN : {pourcentage_gagne:.1f}%")
    print("=" * 60)
    
    return df

# Tester la fonction
df_optimise = optimize_memory(df_encoded)
Résultat obtenu :

text
============================================================
OPTIMISATION MÉMOIRE
============================================================
📊 Mémoire AVANT : 280.5 KB
✅ 6 colonnes float64 → float32
✅ 10 colonnes int64 → int32
📊 Mémoire APRÈS  : 140.3 KB
💰 GAIN : 50.0%
============================================================
Ce qu'on a appris : "Wow, 50% de mémoire en moins ! Ça sert à quelque chose finalement."

Prompt 1.7 : Split train/test
Ce qu'on a tapé dans ChatGPT :

text
"Maintenant qu'on a les données propres, il faut les séparer :
- 80% pour entraîner les modèles
- 20% pour tester

Peux-tu nous montrer comment faire avec scikit-learn ?
Et afficher le nombre de lignes dans chaque ensemble."
Ce que ChatGPT nous a répondu :

python
from sklearn.model_selection import train_test_split

# Séparer les features (X) et la cible (y)
X = df_optimise.drop(columns=['NObeyesdad'])
y = df_optimise['NObeyesdad']

# Split train/test (80% - 20%)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("=" * 60)
print("SÉPARATION TRAIN / TEST")
print("=" * 60)
print(f"📊 Total d'échantillons : {len(df_optimise)}")
print(f"🎓 Train (80%) : {X_train.shape[0]} échantillons")
print(f"🧪 Test  (20%) : {X_test.shape[0]} échantillons")
print("=" * 60)

# Sauvegarder pour réutilisation
import os
os.makedirs("data", exist_ok=True)

X_train.to_csv('data/X_train.csv', index=False)
X_test.to_csv('data/X_test.csv', index=False)
y_train.to_csv('data/y_train.csv', index=False)
y_test.to_csv('data/y_test.csv', index=False)

print("✅ Données sauvegardées dans le dossier 'data/'")
Explication de l'IA :

text
📝 POURQUOI random_state=42 ?
- Ça fixe la graine aléatoire
- Comme ça, si on relance le code, on a la même séparation
- Important pour pouvoir reproduire les résultats
RÉSUMÉ PARTIE 1 (Analyse de données) :
Prompt	Sujet	Ce qu'on a appris
1.1	Chargement	Comment explorer un dataset
1.2	Distribution des classes	Les classes sont équilibrées
1.3	Analyse numérique	Visualiser avec des graphiques
1.4	Outliers	En médecine, on ne supprime pas les outliers !
1.5	Encodage	Différence entre map() et LabelEncoder
1.6	Optimisation mémoire	Gagner 50% de mémoire
1.7	Train/test split	Préparer pour le ML



## PARTIE 2 : MODÈLES MACHINE LEARNING (dossier src/)

### Contexte :
Nous devons comparer 4 modèles de machine learning différents pour prédire les 7 niveaux d'obésité. Chaque membre de l'équipe a été responsable d'un modèle spécifique, et un membre a été chargé de la comparaison finale et de l'explicabilité avec SHAP.

---

### 👤 Membre 2A - Modèle XGBoost

#### Prompt 2.1 : Installer XGBoost et charger les données

**Ce qu'on a tapé dans ChatGPT :**
"Je dois entraîner un modèle XGBoost pour prédire l'obésité.
On a 7 classes différentes.
On a déjà préparé les données dans des fichiers CSV :

X_train.csv, X_test.csv

y_train.csv, y_test.csv

Peux-tu me donner le code pour :

Charger les données

Entraîner XGBoost avec de bons paramètres

Faire des prédictions

Afficher les métriques de performance (accuracy, précision, recall, F1)

Sauvegarder le modèle

Je suis débutant, mets des commentaires stp."

text

**Ce que ChatGPT nous a répondu :**
```python
import pandas as pd
import numpy as np
import joblib
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import os

print("=" * 60)
print("MODÈLE XGBOOST - ENTRAÎNEMENT")
print("=" * 60)

# 1. CHARGER LES DONNÉES
print("\n📂 Chargement des données...")
X_train = pd.read_csv("data/X_train.csv")
X_test = pd.read_csv("data/X_test.csv")
y_train = pd.read_csv("data/y_train.csv").squeeze()
y_test = pd.read_csv("data/y_test.csv").squeeze()

print(f"✅ X_train : {X_train.shape}")
print(f"✅ X_test  : {X_test.shape}")

# 2. CRÉER ET ENTRAÎNER LE MODÈLE
print("\n⚙️ Entraînement du modèle XGBoost...")
modele_xgb = XGBClassifier(
    n_estimators=200,        # Nombre d'arbres
    max_depth=6,              # Profondeur max des arbres
    learning_rate=0.1,        # Taux d'apprentissage
    random_state=42,          # Pour reproduire les résultats
    eval_metric='mlogloss',   # Métrique pour la classification multi-classes
    use_label_encoder=False   # Évite un warning
)

modele_xgb.fit(X_train, y_train)
print("✅ Modèle entraîné !")

# 3. FAIRE DES PRÉDICTIONS
print("\n🔮 Prédictions sur les données de test...")
y_pred = modele_xgb.predict(X_test)
y_prob = modele_xgb.predict_proba(X_test)

# 4. CALCULER LES MÉTRIQUES
print("\n📊 MÉTRIQUES DE PERFORMANCE :")
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

print(f"✅ Accuracy  : {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"✅ Precision : {precision:.4f}")
print(f"✅ Recall    : {recall:.4f}")
print(f"✅ F1-Score  : {f1:.4f}")

# Rapport détaillé par classe
print("\n📋 RAPPORT DÉTAILLÉ :")
print(classification_report(y_test, y_pred))

# 5. SAUVEGARDER LE MODÈLE
os.makedirs("models", exist_ok=True)
joblib.dump(modele_xgb, "models/xgboost_model.pkl")
print("\n💾 Modèle sauvegardé dans 'models/xgboost_model.pkl'")
Notre réaction : "Ça marche ! On a une accuracy de 95.74% sur XGBoost. C'est super bon !"

👤 Membre 2B - Modèle LightGBM
Prompt 2.2 : Entraîner LightGBM
Ce qu'on a tapé dans ChatGPT :

text
"Je dois entraîner LightGBM pour le même problème.
J'ai vu que c'est un modèle rapide et performant.
Peux-tu me donner le code avec :
- Les mêmes données
- Des paramètres adaptés
- Les métriques de performance
- La sauvegarde du modèle

Et explique-moi les paramètres importants."
Ce que ChatGPT nous a répondu :

python
import pandas as pd
import numpy as np
import joblib
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import os
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("MODÈLE LIGHTGBM - ENTRAÎNEMENT")
print("=" * 60)

# 1. CHARGER LES DONNÉES
print("\n📂 Chargement des données...")
X_train = pd.read_csv("data/X_train.csv")
X_test = pd.read_csv("data/X_test.csv")
y_train = pd.read_csv("data/y_train.csv").squeeze()
y_test = pd.read_csv("data/y_test.csv").squeeze()

print(f"✅ X_train : {X_train.shape}")
print(f"✅ X_test  : {X_test.shape}")

# 2. CRÉER ET ENTRAÎNER LE MODÈLE
print("\n⚙️ Entraînement du modèle LightGBM...")

modele_lgbm = LGBMClassifier(
    n_estimators=200,         # Nombre d'arbres
    learning_rate=0.05,        # Taux d'apprentissage (plus petit que XGBoost)
    max_depth=6,               # Profondeur max
    num_leaves=31,             # Nombre de feuilles (paramètre important pour LightGBM)
    random_state=42,
    verbose=-1                 # Pour éviter les messages trop verbaux
)

modele_lgbm.fit(X_train, y_train)
print("✅ Modèle entraîné !")

# 3. FAIRE DES PRÉDICTIONS
print("\n🔮 Prédictions sur les données de test...")
y_pred = modele_lgbm.predict(X_test)
y_prob = modele_lgbm.predict_proba(X_test)

# 4. CALCULER LES MÉTRIQUES
print("\n📊 MÉTRIQUES DE PERFORMANCE :")
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

print(f"✅ Accuracy  : {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"✅ Precision : {precision:.4f}")
print(f"✅ Recall    : {recall:.4f}")
print(f"✅ F1-Score  : {f1:.4f}")

# Rapport détaillé par classe
print("\n📋 RAPPORT DÉTAILLÉ :")
print(classification_report(y_test, y_pred))

# 5. SAUVEGARDER LE MODÈLE
os.makedirs("models", exist_ok=True)
joblib.dump(modele_lgbm, "models/lightgbm_model.pkl")
print("\n💾 Modèle sauvegardé dans 'models/lightgbm_model.pkl'")

# Explication des paramètres (donnée par l'IA)
"""
📝 EXPLICATION DES PARAMÈTRES LIGHTGBM :

- n_estimators : nombre d'arbres dans la forêt. Plus c'est élevé, mieux c'est (jusqu'à un certain point)
- learning_rate : vitesse d'apprentissage. Plus petit = plus précis mais plus lent
- max_depth : profondeur max des arbres. Évite le surapprentissage
- num_leaves : paramètre spécifique à LightGBM. 31 est une valeur standard pour 7 classes
- random_state : pour reproduire les mêmes résultats
"""
👤 Membre 2C - Modèle CatBoost
Prompt 2.3 : Entraîner CatBoost
Ce qu'on a tapé dans ChatGPT :

text
"Je dois entraîner CatBoost.
Paraît que c'est très bon pour les données catégorielles.
Mais nos données sont déjà encodées en nombres.
Peux-tu me donner le code d'entraînement avec les métriques ?"
Ce que ChatGPT nous a répondu :

python
import pandas as pd
import numpy as np
import joblib
from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import os

print("=" * 60)
print("MODÈLE CATBOOST - ENTRAÎNEMENT")
print("=" * 60)

# 1. CHARGER LES DONNÉES
print("\n📂 Chargement des données...")
X_train = pd.read_csv("data/X_train.csv")
X_test = pd.read_csv("data/X_test.csv")
y_train = pd.read_csv("data/y_train.csv").squeeze()
y_test = pd.read_csv("data/y_test.csv").squeeze()

print(f"✅ X_train : {X_train.shape}")
print(f"✅ X_test  : {X_test.shape}")

# 2. CRÉER ET ENTRAÎNER LE MODÈLE
print("\n⚙️ Entraînement du modèle CatBoost...")
print("⚠️ CatBoost peut être un peu long, patience...")

modele_cat = CatBoostClassifier(
    iterations=500,           # Nombre d'arbres
    learning_rate=0.1,         # Taux d'apprentissage
    depth=6,                   # Profondeur des arbres
    random_seed=42,
    verbose=100,               # Affiche la progression tous les 100 arbres
    early_stopping_rounds=50   # Arrête si pas d'amélioration après 50 itérations
)

modele_cat.fit(X_train, y_train, eval_set=(X_test, y_test))
print("✅ Modèle entraîné !")

# 3. FAIRE DES PRÉDICTIONS
print("\n🔮 Prédictions sur les données de test...")
y_pred = modele_cat.predict(X_test)
y_prob = modele_cat.predict_proba(X_test)

# 4. CALCULER LES MÉTRIQUES
print("\n📊 MÉTRIQUES DE PERFORMANCE :")
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

print(f"✅ Accuracy  : {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"✅ Precision : {precision:.4f}")
print(f"✅ Recall    : {recall:.4f}")
print(f"✅ F1-Score  : {f1:.4f}")

# Rapport détaillé par classe
print("\n📋 RAPPORT DÉTAILLÉ :")
print(classification_report(y_test, y_pred))

# 5. SAUVEGARDER LE MODÈLE
os.makedirs("models", exist_ok=True)
modele_cat.save_model("models/catboost_model.cbm")
joblib.dump(modele_cat, "models/catboost_model.pkl")
print("\n💾 Modèle sauvegardé dans 'models/catboost_model.pkl' et 'models/catboost_model.cbm'")
👤 Membre 2D - Modèle Random Forest
Prompt 2.4 : Entraîner Random Forest
Ce qu'on a tapé dans ChatGPT :

text
"Je dois entraîner Random Forest.
C'est le modèle le plus simple à comprendre.
Peux-tu me donner le code avec :
- Les hyperparamètres à ajuster
- Les métriques
- Et peut-être voir l'importance des features ?"
Ce que ChatGPT nous a répondu :

python
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import matplotlib.pyplot as plt
import os

print("=" * 60)
print("MODÈLE RANDOM FOREST - ENTRAÎNEMENT")
print("=" * 60)

# 1. CHARGER LES DONNÉES
print("\n📂 Chargement des données...")
X_train = pd.read_csv("data/X_train.csv")
X_test = pd.read_csv("data/X_test.csv")
y_train = pd.read_csv("data/y_train.csv").squeeze()
y_test = pd.read_csv("data/y_test.csv").squeeze()

print(f"✅ X_train : {X_train.shape}")
print(f"✅ X_test  : {X_test.shape}")

# 2. CRÉER ET ENTRAÎNER LE MODÈLE
print("\n⚙️ Entraînement du modèle Random Forest...")

modele_rf = RandomForestClassifier(
    n_estimators=200,         # Nombre d'arbres
    max_depth=10,              # Profondeur max (None = pas de limite)
    min_samples_split=5,       # Échantillons min pour diviser un noeud
    min_samples_leaf=2,        # Échantillons min dans une feuille
    random_state=42,
    n_jobs=-1                  # Utilise tous les processeurs
)

modele_rf.fit(X_train, y_train)
print("✅ Modèle entraîné !")

# 3. FAIRE DES PRÉDICTIONS
print("\n🔮 Prédictions sur les données de test...")
y_pred = modele_rf.predict(X_test)
y_prob = modele_rf.predict_proba(X_test)

# 4. CALCULER LES MÉTRIQUES
print("\n📊 MÉTRIQUES DE PERFORMANCE :")
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

print(f"✅ Accuracy  : {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"✅ Precision : {precision:.4f}")
print(f"✅ Recall    : {recall:.4f}")
print(f"✅ F1-Score  : {f1:.4f}")

# Rapport détaillé par classe
print("\n📋 RAPPORT DÉTAILLÉ :")
print(classification_report(y_test, y_pred))

# 5. IMPORTANCE DES FEATURES
print("\n🔍 Importance des features :")
importances = modele_rf.feature_importances_
features = X_train.columns

# Trier par importance
indices = np.argsort(importances)[::-1]
print("\nTop 10 features les plus importantes :")
for i in range(min(10, len(features))):
    print(f"{i+1}. {features[indices[i]]} : {importances[indices[i]]:.4f}")

# Graphique
plt.figure(figsize=(10, 6))
plt.title("Importance des features - Random Forest")
plt.barh(range(min(10, len(features))), importances[indices][:10])
plt.yticks(range(min(10, len(features))), [features[i] for i in indices[:10]])
plt.tight_layout()
plt.savefig("outputs/rf_feature_importance.png")
plt.show()

# 6. SAUVEGARDER LE MODÈLE
os.makedirs("models", exist_ok=True)
joblib.dump(modele_rf, "models/random_forest_model.pkl")
print("\n💾 Modèle sauvegardé dans 'models/random_forest_model.pkl'")
👤 Membre 2E - Comparaison des modèles et SHAP
Prompt 2.5 : Comparer tous les modèles
Ce qu'on a tapé dans ChatGPT :

text
"On a 4 modèles entraînés : XGBoost, LightGBM, CatBoost, Random Forest.
Maintenant, on veut les comparer objectivement pour choisir le meilleur.

Peux-tu nous créer un script qui :
1. Charge tous les modèles sauvegardés
2. Calcule les métriques pour chacun sur les mêmes données de test
3. Affiche un tableau comparatif
4. Identifie le meilleur modèle (accuracy et ROC-AUC)
5. Sauvegarde les résultats dans un fichier texte

On veut aussi des graphiques pour visualiser la comparaison."
Ce que ChatGPT nous a répondu :

python
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix
)
import os

print("=" * 70)
print("COMPARAISON DES MODÈLES")
print("=" * 70)

# 1. CHARGER LES DONNÉES DE TEST
print("\n📂 Chargement des données de test...")
X_test = pd.read_csv("data/X_test.csv")
y_test = pd.read_csv("data/y_test.csv").squeeze()
print(f"✅ Données chargées : {X_test.shape[0]} échantillons")

# 2. CHARGER LES MODÈLES
print("\n🤖 Chargement des modèles...")
modeles = {}

try:
    modeles['XGBoost'] = joblib.load("models/xgboost_model.pkl")
    print("✅ XGBoost chargé")
except:
    print("❌ XGBoost non trouvé")

try:
    modeles['LightGBM'] = joblib.load("models/lightgbm_model.pkl")
    print("✅ LightGBM chargé")
except:
    print("❌ LightGBM non trouvé")

try:
    modeles['CatBoost'] = joblib.load("models/catboost_model.pkl")
    print("✅ CatBoost chargé")
except:
    print("❌ CatBoost non trouvé")

try:
    modeles['Random Forest'] = joblib.load("models/random_forest_model.pkl")
    print("✅ Random Forest chargé")
except:
    print("❌ Random Forest non trouvé")

# 3. CALCULER LES MÉTRIQUES POUR CHAQUE MODÈLE
print("\n📊 Calcul des métriques...")
resultats = []

for nom, modele in modeles.items():
    print(f"\n🔍 Évaluation de {nom}...")
    
    # Prédictions
    y_pred = modele.predict(X_test)
    y_prob = modele.predict_proba(X_test)
    
    # Métriques
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    # ROC-AUC (multi-classe)
    n_classes = len(np.unique(y_test))
    if n_classes > 2:
        roc_auc = roc_auc_score(y_test, y_prob, multi_class='ovr')
    else:
        roc_auc = roc_auc_score(y_test, y_prob[:, 1])
    
    resultats.append({
        'Modèle': nom,
        'Accuracy': accuracy,
        'Precision': precision,
        'Recall': recall,
        'F1-Score': f1,
        'ROC-AUC': roc_auc
    })

# 4. AFFICHER LE TABLEAU COMPARATIF
print("\n" + "=" * 70)
print("TABLEAU COMPARATIF DES MODÈLES")
print("=" * 70)

df_resultats = pd.DataFrame(resultats)
df_resultats = df_resultats.sort_values('Accuracy', ascending=False)

# Format pourcentage
df_affichage = df_resultats.copy()
for col in ['Accuracy', 'Precision', 'Recall', 'F1-Score']:
    df_affichage[col] = (df_affichage[col] * 100).round(2).astype(str) + '%'
df_affichage['ROC-AUC'] = df_affichage['ROC-AUC'].round(4)

print("\n" + df_affichage.to_string(index=False))
print()

# 5. IDENTIFIER LE MEILLEUR MODÈLE
meilleur_accuracy = df_resultats.loc[df_resultats['Accuracy'].idxmax()]
meilleur_rocauc = df_resultats.loc[df_resultats['ROC-AUC'].idxmax()]

print("=" * 70)
print("🏆 RÉSULTATS - MEILLEUR MODÈLE")
print("=" * 70)
print(f"\n🎯 Meilleur Accuracy : {meilleur_accuracy['Modèle']} ({meilleur_accuracy['Accuracy']*100:.2f}%)")
print(f"🎯 Meilleur ROC-AUC  : {meilleur_rocauc['Modèle']} ({meilleur_rocauc['ROC-AUC']:.4f})")

# 6. GRAPHIQUES DE COMPARAISON
print("\n📈 Génération des graphiques...")
os.makedirs("outputs", exist_ok=True)

# Graphique à barres
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle("Comparaison des modèles", fontsize=16)

modeles_noms = df_resultats['Modèle'].values
metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
titles = ['Accuracy', 'Précision', 'Recall', 'F1-Score', 'ROC-AUC']

for i, (metric, title) in enumerate(zip(metrics, titles)):
    ax = axes[i // 3, i % 3]
    valeurs = df_resultats[metric].values * (100 if metric != 'ROC-AUC' else 1)
    couleurs = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    ax.bar(modeles_noms, valeurs, color=couleurs)
    ax.set_title(title)
    ax.set_ylabel('Score (%)' if metric != 'ROC-AUC' else 'Score')
    ax.set_ylim(0, 105)
    
    # Ajouter les valeurs sur les barres
    for j, v in enumerate(valeurs):
        ax.text(j, v + 1, f'{v:.1f}', ha='center', fontsize=9)

# Cacher le dernier subplot vide
axes[1, 2].axis('off')
plt.tight_layout()
plt.savefig("outputs/comparaison_modeles.png", dpi=150)
plt.show()

# 7. SAUVEGARDER LES RÉSULTATS DANS UN FICHIER
with open("outputs/resultats_comparaison.txt", "w") as f:
    f.write("=" * 60 + "\n")
    f.write("RÉSULTATS DE LA COMPARAISON DES MODÈLES\n")
    f.write("=" * 60 + "\n\n")
    f.write(df_affichage.to_string())
    f.write("\n\n")
    f.write("=" * 60 + "\n")
    f.write(f"🏆 Meilleur modèle (Accuracy) : {meilleur_accuracy['Modèle']} ({meilleur_accuracy['Accuracy']*100:.2f}%)\n")
    f.write(f"🏆 Meilleur modèle (ROC-AUC) : {meilleur_rocauc['Modèle']} ({meilleur_rocauc['ROC-AUC']:.4f})\n")
    f.write("=" * 60 + "\n")

print("\n✅ Résultats sauvegardés dans 'outputs/resultats_comparaison.txt'")
print("✅ Graphique sauvegardé dans 'outputs/comparaison_modeles.png'")
Prompt 2.6 : Intégration SHAP pour expliquer le meilleur modèle
Ce qu'on a tapé dans ChatGPT :

text
"On a choisi le meilleur modèle (probablement LightGBM ou XGBoost).
Maintenant, on doit ajouter SHAP pour expliquer les prédictions.
Le prof veut voir :
- Les features les plus importantes globalement
- L'impact de chaque feature sur la prédiction

Peux-tu nous aider à intégrer SHAP avec des graphiques ?
On veut que ce soit clair pour des médecins."
Ce que ChatGPT nous a répondu :

python
import pandas as pd
import numpy as np
import joblib
import shap
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("ANALYSE SHAP - EXPLICABILITÉ DU MODÈLE")
print("=" * 60)

# 1. CHARGER LE MEILLEUR MODÈLE (à adapter selon vos résultats)
print("\n📂 Chargement du meilleur modèle...")

# Essayez de charger LightGBM d'abord (souvent le meilleur)
try:
    modele = joblib.load("models/lightgbm_model.pkl")
    nom_modele = "LightGBM"
    print(f"✅ Modèle {nom_modele} chargé")
except:
    try:
        modele = joblib.load("models/xgboost_model.pkl")
        nom_modele = "XGBoost"
        print(f"✅ Modèle {nom_modele} chargé")
    except:
        modele = joblib.load("models/random_forest_model.pkl")
        nom_modele = "Random Forest"
        print(f"✅ Modèle {nom_modele} chargé")

# 2. CHARGER LES DONNÉES DE TEST
X_test = pd.read_csv("data/X_test.csv")
print(f"✅ Données de test chargées : {X_test.shape}")

# Prendre un échantillon pour SHAP (sinon c'est trop long)
X_sample = X_test.sample(min(100, len(X_test)), random_state=42)
print(f"✅ Échantillon de {len(X_sample)} lignes pour SHAP")

# 3. CRÉER L'EXPLAINER SHAP
print("\n🔧 Création de l'explainer SHAP...")
print("⚠️ Cette étape peut prendre quelques secondes...")

if nom_modele in ['LightGBM', 'XGBoost', 'Random Forest']:
    explainer = shap.TreeExplainer(modele)
else:
    # Fallback pour d'autres modèles
    explainer = shap.KernelExplainer(modele.predict_proba, X_sample[:50])

# 4. CALCULER LES VALEURS SHAP
print("\n📊 Calcul des valeurs SHAP...")
shap_values = explainer.shap_values(X_sample)

# 5. GRAPHIQUE 1 : IMPORTANCE GLOBALE DES FEATURES
print("\n📈 Génération du graphique d'importance globale...")

plt.figure(figsize=(10, 6))
if isinstance(shap_values, list):
    # Pour les modèles multi-classes, on prend la moyenne
    shap_values_mean = np.abs(np.array(shap_values)).mean(axis=(0, 1))
    shap.summary_plot(shap_values, X_sample, plot_type='bar', show=False)
else:
    shap.summary_plot(shap_values, X_sample, plot_type='bar', show=False)

plt.title(f"Importance des features - {nom_modele}", fontsize=14)
plt.tight_layout()
plt.savefig("outputs/shap_importance_globale.png", dpi=150, bbox_inches='tight')
plt.show()

# 6. GRAPHIQUE 2 : SUMMARY PLOT (impact détaillé)
print("\n📈 Génération du summary plot...")

plt.figure(figsize=(10, 8))
if isinstance(shap_values, list):
    # Pour les modèles multi-classes, on prend la classe 0 (mais on peut choisir)
    shap.summary_plot(shap_values, X_sample, show=False)
else:
    shap.summary_plot(shap_values, X_sample, show=False)

plt.title(f"Impact des features sur la prédiction - {nom_modele}", fontsize=14)
plt.tight_layout()
plt.savefig("outputs/shap_summary.png", dpi=150, bbox_inches='tight')
plt.show()

# 7. GRAPHIQUE 3 : WATERFALL POUR UN PATIENT EXEMPLE
print("\n📈 Génération du waterfall plot pour un patient exemple...")

# Prendre le premier patient
patient_idx = 0
patient_data = X_sample.iloc[patient_idx:patient_idx+1]

plt.figure(figsize=(10, 6))
if isinstance(shap_values, list):
    # Pour la classe prédite
    prediction = modele.predict(patient_data)[0]
    shap.waterfall_plot(
        shap.Explanation(
            values=shap_values[int(prediction)][patient_idx],
            base_values=explainer.expected_value[int(prediction)],
            data=patient_data.values[0],
            feature_names=X_sample.columns.tolist()
        ),
        show=False
    )
else:
    shap.waterfall_plot(
        shap.Explanation(
            values=shap_values[patient_idx],
            base_values=explainer.expected_value,
            data=patient_data.values[0],
            feature_names=X_sample.columns.tolist()
        ),
        show=False
    )

plt.title(f"Explication pour un patient - {nom_modele}", fontsize=14)
plt.tight_layout()
plt.savefig("outputs/shap_waterfall.png", dpi=150, bbox_inches='tight')
plt.show()

# 8. RÉSUMÉ DES FEATURES LES PLUS IMPORTANTES
print("\n" + "=" * 60)
print("📊 TOP 10 FEATURES LES PLUS IMPORTANTES")
print("=" * 60)

if isinstance(shap_values, list):
    # Moyenne sur toutes les classes
    importance = np.abs(np.array(shap_values)).mean(axis=(0, 1))
else:
    importance = np.abs(shap_values).mean(axis=0)

feature_importance = pd.DataFrame({
    'Feature': X_sample.columns,
    'Importance': importance
}).sort_values('Importance', ascending=False)

for i, row in feature_importance.head(10).iterrows():
    print(f"{i+1}. {row['Feature']} : {row['Importance']:.4f}")

# 9. SAUVEGARDER LES RÉSULTATS
feature_importance.to_csv("outputs/shap_feature_importance.csv", index=False)
print("\n✅ Résultats SHAP sauvegardés dans 'outputs/shap_feature_importance.csv'")
RÉSUMÉ PARTIE 2 (Modèles ML) :
Membre	Modèle	Prompts	Résultat obtenu
Membre 2A	XGBoost	1	Accuracy ~95.74%
Membre 2B	LightGBM	1	Accuracy ~96.22%
Membre 2C	CatBoost	1	Accuracy ~95.51%
Membre 2D	Random Forest	1	Accuracy ~94.33%
Membre 2E	Comparaison + SHAP	2	Tableau comparatif + graphiques SHAP
Conclusion : LightGBM a été choisi comme meilleur modèle avec 96.22% d'accuracy. SHAP nous a permis de comprendre que le poids, l'âge et les antécédents familiaux sont les facteurs les plus importants.


