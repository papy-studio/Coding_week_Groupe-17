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
