# MediObes — Outil Clinique d'Aide à la Décision pour l'Estimation du Risque d'Obésité

> **Coding Week — Centrale Casablanca — Groupe 17 — Mars 2026**  
> Application web basée sur le machine learning pour la prédiction du risque d'obésité avec explicabilité SHAP, conçue pour les professionnels de santé et les patients.

---

## Table des matières

1. [Vue d'ensemble du projet](#1-vue-densemble-du-projet)
2. [Dataset](#2-dataset)
3. [Modèle de Machine Learning](#3-modèle-de-machine-learning)
4. [Explicabilité SHAP](#4-explicabilité-shap)
5. [Prompt Engineering](#5-prompt-engineering)
6. [Architecture de l'application](#6-architecture-de-lapplication)
7. [Installation et lancement](#7-installation-et-lancement)
8. [Tests automatisés](#8-tests-automatisés)
9. [Pipeline CI/CD](#9-pipeline-cicd)
10. [Structure du projet](#10-structure-du-projet)
11. [Équipe](#11-équipe)

---

## 1. Vue d'ensemble du projet

MediObes est un outil clinique d'aide à la décision qui estime le niveau de risque d'obésité d'un patient à partir de données cliniques et comportementales, en utilisant le machine learning et l'explicabilité SHAP. L'application propose deux espaces dédiés :

- **Espace Médecin** — Saisie des données cliniques du patient, exécution de la prédiction, visualisation des explications SHAP, rédaction de recommandations personnalisées.
- **Espace Patient** — Consultation du niveau de risque personnel, lecture des recommandations du médecin, suivi hebdomadaire de l'évolution du poids.

**Stack technique :** Python 3.13 · Streamlit · LightGBM · SHAP · pandas · joblib · pytest · Docker · GitHub Actions

---

## 2. Dataset

**Source :** UCI Machine Learning Repository — Obesity Levels Dataset (ID : 544)  
**URL :** https://archive.ics.uci.edu/dataset/544/estimation+of+obesity+levels+based+on+eating+habits+and+physical+condition

| Propriété | Valeur |
|---|---|
| Nombre d'échantillons | 2 111 |
| Features | 16 features cliniques et comportementales |
| Classes cibles | 7 niveaux d'obésité |
| Valeurs manquantes | Aucune |

### 2.1 Classes cibles

| Classe | Description |
|---|---|
| `Insufficient_Weight` | IMC < 18,5 |
| `Normal_Weight` | IMC 18,5–24,9 |
| `Overweight_Level_I` | IMC 25–27,4 |
| `Overweight_Level_II` | IMC 27,5–29,9 |
| `Obesity_Type_I` | IMC 30–34,9 |
| `Obesity_Type_II` | IMC 35–39,9 |
| `Obesity_Type_III` | IMC ≥ 40 |

### 2.2 Équilibre du dataset

Le dataset est **modérément équilibré** entre les 7 classes, avec entre 272 et 351 échantillons par classe. Cette distribution quasi-uniforme est intentionnelle — le dataset UCI a été synthétiquement augmenté via SMOTE pour garantir une représentation équitable de chaque niveau d'obésité.

**Impact :** Grâce à cet équilibre naturel, aucune technique de rééchantillonnage supplémentaire (SMOTE, pondération des classes, sous-échantillonnage) n'a été nécessaire. Le modèle a été entraîné directement sur les données encodées sans correction du déséquilibre, et obtient malgré tout d'excellents scores F1 macro sur toutes les classes. Cela confirme que l'équilibre du dataset a directement contribué à la robustesse et à la généralisation du modèle.

### 2.3 Encodage des features

| Feature | Type | Encodage |
|---|---|---|
| Gender | Binaire | Female=0, Male=1 |
| family_history, FAVC, SMOKE, SCC | Binaires | no=0, yes=1 |
| CAEC (grignotage) | Ordinal | Always=0, Frequently=1, no=2, Sometimes=3 |
| CALC (alcool) | Ordinal | Always=0, Frequently=1, no=2, Sometimes=3 |
| MTRANS (transport) | Nominal | Automobile=0, Bike=1, Motorbike=2, Public_Transportation=3, Walking=4 |
| NObeyesdad (cible) | Multiclasse | LabelEncoder (ordre alphabétique, 0–6) |

---

## 3. Modèle de Machine Learning

### 3.1 Sélection du modèle

Plusieurs modèles ont été évalués sur le dataset :

| Modèle | Accuracy | F1 Macro | Remarques |
|---|---|---|---|
| **LightGBM** | **~97%** | **~97%** | ✅ Meilleur modèle — sélectionné |
| XGBoost | ~95% | ~95% | Performant mais plus lent |
| Random Forest | ~96% | ~95% | Bonne baseline |
| CatBoost | ~94% | ~94% | Entraînement plus lent |

**LightGBM a été sélectionné** pour sa précision supérieure, sa rapidité d'entraînement et son support natif de l'explicabilité SHAP via TreeExplainer.

### 3.2 Configuration LightGBM

```python
LGBMClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=6,
    verbose=-1
)
```

### 3.3 Métriques de performance

| Métrique | Valeur |
|---|---|
| Accuracy | ~97% |
| ROC-AUC (One-vs-Rest) | ~99,9% |
| F1 Macro | ~97% |
| Découpage Train/Test | 80% / 20% (random_state=42) |

Le modèle identifie correctement les 7 classes d'obésité sur le jeu de test, avec une confiance particulièrement élevée sur les classes extrêmes (`Insufficient_Weight` et `Obesity_Type_III`), qui sont les plus critiques cliniquement.

### 3.4 Pourquoi LightGBM est le plus performant

LightGBM utilise une stratégie de croissance d'arbres **feuille par feuille** (leaf-wise) plutôt que niveau par niveau. Cette approche lui permet de modéliser des frontières de décision plus complexes, particulièrement efficaces sur des données tabulaires cliniques où les interactions entre features (par exemple Poids × Activité physique, ou FAVC × Antécédents familiaux) portent un signal prédictif fort.

---

## 4. Explicabilité SHAP

### 4.1 Pourquoi SHAP ?

SHAP (SHapley Additive exPlanations) fournit une **importance des features par prédiction individuelle** — il explique non seulement ce que le modèle prédit, mais **pourquoi**. Dans un contexte médical, c'est essentiel : un médecin doit comprendre quels facteurs ont conduit à une classification de risque donnée avant d'agir sur cette information.

### 4.2 Features les plus influentes

D'après l'analyse SHAP sur le jeu de test, les features qui influencent le plus les prédictions sont :

| Rang | Feature | Signification clinique | Direction d'impact |
|---|---|---|---|
| 1 | **Weight (Poids)** | Poids corporel du patient (kg) | ↑ Poids élevé → classe obésité supérieure |
| 2 | **Height (Taille)** | Taille du patient (m) | ↑ Patient plus grand → classe obésité inférieure |
| 3 | **Age** | Âge du patient (années) | Corrélation positive modérée avec le risque |
| 4 | **family_history_with_overweight** | Prédisposition génétique à l'obésité | Fort effet positif vers les classes obésité |
| 5 | **FAVC** | Consommation fréquente d'aliments très caloriques | Pousse vers les classes supérieures |
| 6 | **FAF** | Fréquence d'activité physique hebdomadaire | ↑ Plus d'activité → classe obésité inférieure |
| 7 | **NCP** | Nombre de repas principaux par jour | Influence modérée |
| 8 | **CH2O** | Consommation d'eau quotidienne | Corrélation inverse avec l'obésité |
| 9 | **CAEC** | Grignotage entre les repas | Pousse vers les classes surpoids |
| 10 | **MTRANS** | Mode de transport principal | Marche/vélo → risque obésité plus faible |

### 4.3 Insights cliniques issus de SHAP

**Le poids et la taille dominent** car ils encodent directement l'IMC, l'indicateur clinique primaire. Cependant, le modèle apporte une nuance au-delà de l'IMC : deux patients avec un IMC identique peuvent recevoir des prédictions différentes en fonction de leurs comportements.

**Les antécédents familiaux** constituent la feature non-biométrique la plus forte — les patients avec des antécédents familiaux d'obésité sont systématiquement orientés vers des classes supérieures, même lorsque leur IMC est borderline.

**L'activité physique (FAF)** présente constamment des valeurs SHAP négatives importantes pour les classes obésité — le modèle a appris que les patients actifs sont significativement moins susceptibles d'être classés obèses, indépendamment de leur poids actuel.

**Le mode de transport** est un proxy de l'activité physique quotidienne. Les patients qui marchent ou utilisent le vélo comme transport principal ont des contributions SHAP nettement plus faibles aux classes obésité par rapport aux conducteurs automobiles.

Ces insights sont présentés dans l'interface MediObes via des graphiques SHAP individuels pour chaque consultation, permettant aux médecins d'expliquer les prédictions aux patients en termes concrets et actionnables.

---

## 5. Prompt Engineering

Le prompt engineering a été appliqué dans MediObes pour la **génération automatique de recommandations cliniques** dans `doctor_recommendations.py`.

### 5.1 Le problème

Lorsqu'un médecin ouvre la page des recommandations, il fait face à une zone de texte vide. Rédiger des recommandations personnalisées et médicalement appropriées pour chacun des 7 niveaux d'obésité à partir de zéro est chronophage et source d'incohérences entre praticiens.

### 5.2 L'approche — Conception de templates structurés

Plutôt que d'appeler une API LLM externe, le prompt engineering dans MediObes prend la forme de **templates cliniques structurés** déclenchés conditionnellement selon la classe d'obésité prédite. Ces templates ont été conçus en appliquant les principes du prompt engineering : spécificité, actionnabilité et ancrage médical.

**Exemple concret — pour `Obesity_Type_I` :**

Le défi était de générer une recommandation à la fois médicalement précise pour ce niveau de risque, suffisamment détaillée pour être utile, et structurée pour que le médecin puisse la personnaliser rapidement. La réflexion de prompt engineering a consisté à décomposer le problème en sous-tâches cliniques distinctes — suivi, nutrition, activité physique, bilan biologique, objectif chiffré :

```
- Prise en charge multidisciplinaire : médecin, diététicien, psychologue si nécessaire.
- Programme de rééducation alimentaire complet sur 6 mois minimum.
- Activité physique adaptée supervisée : kinésithérapeute recommandé.
- Bilan cardiologique et métabolique complet obligatoire.
- Suivi hebdomadaire du poids les 2 premiers mois, puis mensuel.
- Objectif : perte de 5 à 10% du poids initial sur 6 mois.
```

L'insight clé du prompt engineering ici est la **spécificité conditionnée par la classe** : plutôt que des conseils génériques, chaque template est calibré sur la gravité clinique et l'urgence de la classe prédite. Les templates `Obesity_Type_III` incluent un langage d'orientation urgente et des recommandations d'hospitalisation, tandis que les templates `Normal_Weight` se concentrent sur la maintenance et la prévention.

**Impact :** Les médecins peuvent charger un template médicalement approprié en un clic, puis le personnaliser pour le patient individuel — réduisant significativement le temps de rédaction tout en maintenant la qualité clinique et la cohérence entre praticiens.

---

## 6. Architecture de l'application

```
app/
├── app.py                          # Point d'entrée — init données, redirection vers home
└── pages/                          # Structure plate — pas de sous-dossiers
    ├── home.py                     # Page d'accueil — choix espace médecin ou patient
    ├── doctor_login.py             # Authentification médecin
    ├── doctor-register.py          # Création de compte médecin
    ├── doctor_dashboard.py         # Liste patients avec KPIs et recherche
    ├── doctor_data_entry.py        # Formulaire saisie données cliniques (16 features)
    ├── doctor_result.py            # Prédiction ML + visualisation SHAP
    ├── doctor_recommendations.py   # Rédaction recommandations personnalisées
    ├── patient_login.py            # Authentification patient
    ├── patient_profile.py          # Affichage niveau de risque + recommandations
    └── patient_tracking.py         # Suivi poids hebdomadaire avec graphiques
```

### Flux de données

```
Le médecin saisit les données du patient (16 features)
                    ↓
LightGBM prédit la classe d'obésité (0–6)
                    ↓
SHAP explique quelles features ont conduit à la prédiction
                    ↓
Le médecin sauvegarde le dossier + rédige les recommandations
                    ↓
Le patient se connecte → voit son niveau de risque + recommandations + suivi de poids
```

### Stockage des données

```
data/
├── doctors.json              # Comptes médecins {username: {password, name}}
├── patients.json             # Comptes patients {patient_id: {password, name, doctor_id}}
├── records/{patient_id}.json # Dossier médical complet par patient
└── tracking/{patient_id}.csv # Historique de poids (date, poids)
```

---

## 7. Installation et lancement

### Prérequis

- Python 3.13
- pip

### Installation classique

```bash
# 1. Cloner le dépôt
git clone https://github.com/papy-studio/Coding_week_Groupe-17.git
cd Coding_week_Groupe-17

# 2. Créer et activer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Mac/Linux

# 3. Installer les dépendances
pip install -r requirements.txt
```

### Générer le modèle

Les fichiers `.pkl` ne sont pas inclus dans le dépôt. Pour les générer sur Google Colab :

1. Ouvrir `notebooks/LightGBM.ipynb` dans Google Colab
2. Exécuter toutes les cellules
3. Télécharger `model.pkl` et `label_encoder.pkl`
4. Les placer dans `src/models/`

### Lancer avec Streamlit

```bash
streamlit run app/app.py
```

L'application s'ouvre à `http://localhost:8501`.

### Lancer avec Docker

Docker permet de lancer MediObes sans installer Python, pip ou les dépendances système — tout est encapsulé dans le container.

```bash
# 1. Créer le .dockerignore à la racine (évite de copier .venv et notebooks)
cat > .dockerignore << 'EOF'
.venv/
__pycache__/
*.pyc
.git/
.DS_Store
notebooks/
tests/
*.ipynb
data/records/
data/tracking/
EOF

# 2. Builder l'image (5-10 min la première fois — LightGBM + SHAP sont lourds)
docker build -t mediobes .

# 3. Lancer le container
docker run -p 8501:8501 mediobes
```

L'application est ensuite accessible à `http://localhost:8501`.

> **Note :** Le premier build prend du temps (~5-10 min) car Docker installe toutes les dépendances depuis zéro. Les builds suivants seront instantanés grâce au cache — Docker ne réinstalle les packages que si `requirements.txt` change.

### Comptes médecin par défaut

| Identifiant | Mot de passe |
|---|---|
| dr.martin | medic123 |
| dr.hassan | medic456 |

---

## 8. Tests automatisés

```bash
# Tous les tests
pytest tests/ -v

# Tests du modèle uniquement
pytest tests/test_models.py -v

# Tests du flux patient uniquement
pytest tests/test_patient_flow.py -v

# Avec rapport HTML
pytest tests/ -v --html=tests/rapport_tests.html --self-contained-html
```

### Couverture des tests

**`test_models.py`** — 20 tests couvrant :
- Existence des fichiers modèle et données
- Validation des données (shape, colonnes, plages de valeurs, ratio split)
- Chargement et interface du modèle (predict, predict_proba)
- Validité des prédictions (plage des classes, somme des probabilités = 1)
- Cohérence clinique (IMC normal → classe normale, patient obèse → classe obésité)
- Accuracy ≥ 90% et ≥ 95% · F1 macro ≥ 90% · Déterminisme

**`test_patient_flow.py`** — 15 tests couvrant :
- Simulation complète du pipeline ML (saisie → prédiction → sauvegarde → vérification)
- Création et intégrité du dossier JSON
- Persistance des recommandations (pas d'écrasement lors d'une mise à jour)
- Flux d'intégration : data_entry → result → recommendations

---

## 9. Pipeline CI/CD

GitHub Actions exécute automatiquement tous les tests à chaque push sur `main` ou `develop`, et à chaque pull request vers `main`.

```yaml
# .github/workflows/ci.yml
on:
  push:          { branches: [main, develop] }
  pull_request:  { branches: [main] }
```

**Étapes du pipeline :**
1. Checkout du code
2. Configuration de Python 3.13
3. Installation des dépendances depuis `requirements.txt`
4. Exécution de `test_models.py`
5. Exécution de `test_patient_flow.py`
6. Génération du rapport HTML des tests
7. Upload du rapport comme artefact

Un test en échec bloque le merge — garantissant que le modèle et le flux patient sont toujours fonctionnels sur la branche principale.

---

## 10. Structure du projet

```
Coding_week_Groupe-17/
├── .github/
│   └── workflows/
│       └── ci.yml                  # Pipeline CI GitHub Actions
├── app/
│   ├── app.py                      # Point d'entrée Streamlit
│   └── pages/                      # Toutes les pages (structure plate)
├── src/
│   ├── models/
│   │   └── model.pkl               # Modèle LightGBM entraîné
│   └── data/
│       ├── X_train.csv
│       ├── X_test.csv
│       ├── y_train.csv
│       └── y_test.csv
├── data/
│   ├── doctors.json
│   ├── patients.json
│   ├── records/
│   └── tracking/
├── notebooks/
│   ├── LightGBM.ipynb              # Notebook d'entraînement du modèle
│   ├── eda.ipynb                   # Analyse exploratoire des données
│   └── shap_analysis.ipynb         # Analyse SHAP
├── tests/
│   ├── test_models.py              # Tests unitaires du modèle
│   └── test_patient_flow.py        # Tests d'intégration
├── .streamlit/
│   └── config.toml                 # Configuration du thème Streamlit
├── .dockerignore                   # Fichiers exclus du build Docker
├── Dockerfile                      # Configuration Docker
├── requirements.txt
└── README.md
```

---

## 11. Équipe

**Centrale Casablanca — Coding Week Mars 2026 — Groupe 17**
Projet réalisé par le **Groupe 17** dans le cadre de la **Coding Week 2026**.

Wiaam BOUGUEZOUR(cattcookies70-sudo)                      
Meryem AZGARD(meryem000a-cmyk)                         
Tawba BENZAYED(tawbabenzayed-droid)   
Papy NANA(papy-studio)  
Moubarak TIEMTORE(mbk7-dev)      

Organisation GitHub : [papy-studio](https://github.com/papy-studio)  
Dépôt : [Coding_week_Groupe-17](https://github.com/papy-studio/Coding_week_Groupe-17)

---

*MediObes — Centrale Casablanca · Coding Week 2026 · Toutes les données sont confidentielles et à des fins de démonstration uniquement.*