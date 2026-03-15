# MediObes — Application d'aide à la décision pour l'estimation du niveau d'obésité

## 1) Présentation du projet

**MediObes** est une application développée dans le cadre du projet **Coding Week**.
L'objectif est de concevoir une solution simple, pédagogique et exploitable combinant :

- une **analyse de données médicales**,
- plusieurs **modèles de machine learning**,
- une **interface Streamlit** pour les médecins et les patients,
- une première couche d'**explicabilité** des prédictions.

Le projet estime le **niveau d'obésité** d'un patient à partir de ses caractéristiques physiques, de ses habitudes alimentaires et de son mode de vie.

> **Important** : ce projet a une vocation **académique et pédagogique**. Il ne remplace pas un avis médical et ne doit pas être utilisé comme outil de diagnostic clinique réel.

---

## 2) Problématique

L'obésité est un enjeu de santé publique majeur. Ce projet répond à la question suivante :

**Comment concevoir une application capable d'estimer automatiquement le niveau d'obésité d'un patient?**

---

## 3) Objectifs pédagogiques et techniques

### Objectifs pédagogiques

- Découvrir un **workflow complet de projet data/IA**.
- Manipuler un **jeu de données réel**.
- Comprendre la différence entre **prétraitement, entraînement et test**.
- Produire un projet **présentable devant un encadrant ou un jury**.

### Objectifs techniques

- Prédire une classe de la variable **NObeyesdad**.
- Comparer plusieurs algorithmes de classification.
- Construire une interface interactive avec **Streamlit**.
- Sauvegarder des dossiers patients au format **JSON**.
- Ajouter une première interprétation du modèle via **SHAP**.

---

## 4) Fonctionnalités principales

### Côté médecin

- connexion à un espace dédié,
- saisie des données cliniques du patient,
- estimation du niveau d'obésité,
- affichage des probabilités de classes,
- visualisation d'éléments d'explication,
- ajout de recommandations,
- sauvegarde du dossier patient.

### Côté patient

- connexion à un espace personnel,
- consultation du profil,
- visualisation du dernier résultat médical,
- suivi de poids,
- lecture des recommandations enregistrées.

### Côté data science

- préparation et encodage des données,
- comparaison de plusieurs modèles,
- sauvegarde des résultats,
- tests automatiques sur les prédictions et les fichiers.

---

## 5) Jeu de données utilisé

Le projet s'appuie sur le dataset public :

**Estimation of Obesity Levels Based on Eating Habits and Physical Condition**

Source indiquée dans le projet :
- UCI Machine Learning Repository
- https://archive.ics.uci.edu/dataset/544/estimation+of+obesity+levels+based+on+eating+habits+and+physical+condition

### Variable cible

La variable à prédire est :

- **NObeyesdad** : niveau d'obésité du patient.

### Exemples de variables d'entrée

- Gender
- Age
- Height
- Weight
- family_history_with_overweight
- FAVC
- FCVC
- NCP
- CAEC
- SMOKE
- CH2O
- SCC
- FAF
- TUE
- CALC
- MTRANS

---

## 6) Approche de machine learning

Le dépôt montre une approche basée sur la **classification supervisée multiclasses**.

### Étapes suivies

1. Chargement du dataset.
2. Encodage des variables catégorielles.
3. Encodage de la variable cible.
4. Optimisation mémoire des colonnes numériques.
5. Séparation en jeu d'entraînement et jeu de test.
6. Entraînement et comparaison de plusieurs modèles.
7. Intégration du meilleur modèle dans l'application(LightGBM Classifier).

### Modèles considérés dans le projet

- Random Forest Classifier
- XGBoost Classifier
- LightGBM Classifier
- CatBoost Classifier

### Explainable AI

Le projet prévoit l'usage de **SHAP** afin de mieux expliquer les facteurs ayant influencé la prédiction.

---

## 7) Technologies utilisées

- **Python**
- **Streamlit** pour l'interface web
- **Pandas / NumPy** pour le traitement de données
- **Scikit-learn** pour la préparation et l'évaluation
- **LightGBM / XGBoost / CatBoost / Random Forest** pour la classification
- **Matplotlib / Seaborn / Plotly** pour la visualisation
- **Joblib** pour la sauvegarde des modèles
- **Pytest** pour les tests

---

## 8) Structure réelle du dépôt

```text
Coding_week_Groupe-17-main/
├── app/
│   ├── app.py
│   ├── espace_medecin.ipynb
│   └── pages/
│       ├── home.py
│       ├── doctor_login.py
│       ├── doctor_dashboard.py
│       ├── doctor_data_entry.py
│       ├── doctor_result.py
│       ├── doctor_recommendations.py
│       ├── doctor-register.py
│       ├── patient_login.py
│       ├── patient_profile.py
│       ├── patient_tracking.py
│       └── doctor/
│           └── recommendations.py
├── data/
├── notebooks/
│   ├── Analyse.ipynb
│   ├── eda.ipynb
│   └── data/
├── outputs/
│   ├── results.txt
│   └── test_output.txt
├── src/
│   ├── data_processing.py
│   ├── run_comparison.py
│   ├── test_imports.py
│   ├── train_model.ipynb
│   ├── LightGBM.ipynb
│   ├── comparaison.ipynb
│   └── data/
├── tests/
│   ├── test_models.py
│   ├── test_patient_flow.py
│   ├── rapport_tests.html
│   └── assets/
├── requirements.txt
└── README.md
```

### Rôle des principaux dossiers

- **app/** : interface Streamlit.
- **src/** : scripts et notebooks orientés entraînement / comparaison.
- **notebooks/** : analyse exploratoire et préparation des données.
- **data/** : fichiers JSON et données utilisées par l'application.
- **outputs/** : résultats, logs et modèles exportés lorsqu'ils sont générés.
- **tests/** : tests automatiques fonctionnels et ML.

---

## 9) Installation du projet

### Prérequis

Il est conseillé d'utiliser :

- **Python 3.10 ou plus**
- **pip**
- un **environnement virtuel**

### Étapes d'installation

Depuis la racine du projet :

```bash
python -m venv .venv
```

#### Sous Windows

```bash
.venv\Scripts\activate
```

#### Sous macOS / Linux

```bash
source .venv/bin/activate
```

Puis installer les dépendances :

```bash
pip install -r requirements.txt
```

---

## 10) Lancer l'application

Depuis la racine du projet, exécuter :

```bash
streamlit run app/app.py
```

### Remarque importante

Au premier lancement, l'application crée automatiquement certains fichiers si besoin, par exemple :

- `data/doctors.json`
- `data/patients.json`
- `data/records/`
- `data/tracking/`

---

## 11) Comptes de démonstration présents dans le code

Le code initialise deux comptes médecins de test :

- **dr.martin** / **medic123**
- **dr.hassan** / **medic456**



---

## 12) Exécuter les tests

Lancer tous les tests :

```bash
pytest tests -v
```

Lancer séparément :

```bash
pytest tests/test_models.py -v
pytest tests/test_patient_flow.py -v
```

### Ce que vérifient les tests

- l'existence des fichiers nécessaires,
- la validité des plages de données,
- le chargement des modèles,
- la cohérence des prédictions,
- la sauvegarde correcte des dossiers patients,
- la stabilité générale du flux patient.



---

## 13) Compétences d'ingénierie mobilisées

Ce projet est intéressant pour une 1re année d'ingéniorat car il fait intervenir plusieurs dimensions :

- **algorithmique**,
- **programmation Python**,
- **gestion de données**,
- **intelligence artificielle**,
- **tests logiciels**,
- **interface homme-machine**,
- **organisation d'un projet en équipe**,
- **communication technique**.

---

## 14) Limites du projet

- Le dataset reste un dataset public académique, pas une base hospitalière réelle.
- Les performances annoncées doivent être **revalidées** sur les modèles effectivement exportés.
- La sécurité des comptes est volontairement simplifiée.
- Le dépôt gagnerait à mieux séparer les scripts de production, les notebooks et les artefacts générés.

---

## 15) Auteurs

Projet réalisé par le **Groupe 17** dans le cadre de la **Coding Week 2026**.

Wiaam BOUGUEZOUR(cattcookies70-sudo)                      
Meryem AZGARD(meryem000a-cmyk)                         
Tawba BENZAYED(tawbabenzayed-droid)   
Papy NANA(papy-studio)  
Moubarak TIEMTORE(mbk7-dev)               

**JIRA**   Pour organiser notre travail nous avons fait la répartition des tâches.



---

## 16) Conclusion


Ce projet, **MediObes**, démontre comment le machine learning explicable peut être utilisé pour soutenir les professionnels de santé dans la prise de décision.

En combinant prédiction automatique, transparence des modèles et interface interactive, cette application constitue un outil utile pour le suivi et la prévention de l’obésité.
