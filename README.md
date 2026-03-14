# coding_week_Groupe-17

# Application d'Aide à la Décision Médicale

## Estimation du Niveau d’Obésité avec Machine Learning Explicable

Ce projet a été réalisé dans le cadre de la **Coding Week (9–15 mars 2026)**.

L’objectif est de développer une **application d’aide à la décision médicale** permettant aux médecins d’estimer le **niveau d’obésité d’un patient** à partir de ses habitudes alimentaires, de son mode de vie et de certaines caractéristiques physiques.

La solution combine :

* **Machine Learning**
* **Explainable AI (SHAP)**
* **Interface interactive pour les médecins et les patients**

---

# Objectifs du projet

Les principaux objectifs sont :

* Développer un **modèle de machine learning robuste** pour prédire le niveau d’obésité.
* Assurer la **transparence des prédictions** grâce à l’utilisation de **SHAP**.
* Concevoir une **interface simple et intuitive** pour les professionnels de santé.
* Appliquer des **bonnes pratiques de développement logiciel** (GitHub, organisation du projet, tests).

---

# Jeu de données

Nous utilisons le dataset public du **UCI Machine Learning Repository** :

**Estimation of Obesity Levels Based on Eating Habits and Physical Condition**

Lien du dataset :

[https://archive.ics.uci.edu/dataset/544/estimation+of+obesity+levels+based+on+eating+habits+and+physical+condition](https://archive.ics.uci.edu/dataset/544/estimation+of+obesity+levels+based+on+eating+habits+and+physical+condition)

Ce dataset contient des informations sur :

* le **genre**
* l’**âge**
* la **taille**
* le **poids**
* les **habitudes alimentaires**
* l’**activité physique**
* le **tabagisme**
* le **mode de transport**

La variable cible est :

**NObeyesdad** : niveau d’obésité (7 classes).

---

# Analyse et Prétraitement des données

Plusieurs étapes de préparation des données ont été réalisées.

## Encodage des variables catégorielles

Les variables catégorielles ont été transformées en variables numériques :

* variables binaires

  * `yes / no → 1 / 0`
* variables catégorielles

  * encodage avec **LabelEncoder**

---

## Optimisation de la mémoire

Une fonction a été développée pour réduire l’utilisation mémoire :

```
optimize_memory(df)
```

Cette fonction convertit automatiquement :

* `float64 → float32`
* `int64 → int32`

Cela permet :

* de réduire l’utilisation mémoire
* d’améliorer les performances du traitement.

---

## Séparation des données

Les données sont divisées en :

* **80 % pour l'entraînement**
* **20 % pour les tests**

Cette séparation permet d’évaluer la performance du modèle sur des données non vues.

---

# Modèles de Machine Learning

Plusieurs modèles ont été testés et comparés :

* **Random Forest Classifier**
* **XGBoost Classifier**
* **LightGBM Classifier**
* **CatBoost Classifier**

Les modèles ont été évalués selon plusieurs métriques :

* Accuracy
* Precision
* Recall
* F1-score
* ROC-AUC

---

# Modèle sélectionné

Après comparaison des performances, **LightGBM Classifier** s’est révélé être le modèle le plus performant.

Il offre :

* la **meilleure accuracy**
* une **bonne capacité de généralisation**
* une **exécution rapide**

Ce modèle a donc été choisi pour être intégré dans l’application.

---

# Explainable AI avec SHAP

Afin de garantir la **transparence des prédictions**, nous avons intégré **SHAP (SHapley Additive exPlanations)**.

SHAP permet :

* d’identifier les **variables les plus influentes**
* d’expliquer les décisions du modèle
* de rendre le modèle **compréhensible pour les médecins**

Les visualisations SHAP incluent :

* **SHAP Summary Plot**
* **importance des variables**
* **interprétation des prédictions individuelles**

---

# Interface de l’application

L’interface a été développée avec **Streamlit**.

L’application comporte plusieurs pages destinées aux **médecins** et aux **patients**.

---

## Interface médecin

Le médecin peut :

* saisir les données du patient
* prédire le **niveau d’obésité**
* visualiser les **explications du modèle**
* fournir des **recommandations personnalisées**

---

## Interface patient

Le patient peut :

* suivre son **évolution de santé**
* effectuer un **suivi hebdomadaire**
* consulter ses **résultats**
* recevoir des **conseils adaptés**

L’objectif est de permettre un **suivi continu et personnalisé**.

---

# Architecture du projet

Le projet suit une architecture professionnelle :

```
project/

app/
    app.py
    pages/
        doctor/
        patient/

data/

notebooks/
    eda.ipynb
    Analyse.ipynb

src/
    data_processing.py
    run_comparison.py

tests/

outputs/

requirements.txt
README.md
```

Description :

* **notebooks/** : analyse exploratoire des données
* **src/** : pipeline de machine learning
* **app/** : interface web
* **tests/** : tests automatisés
* **outputs/** : résultats des modèles

---

# Installation

Cloner le repository :

```
git clone <repository_url>
cd project
```

Installer les dépendances :

```
pip install -r requirements.txt
```

---

# Entraînement du modèle

Pour entraîner le modèle :

```
python src/train_model.py
```

---

# Lancer l’application

Pour démarrer l’interface :

```
streamlit run app/app.py
```

L’application s’ouvrira automatiquement dans votre navigateur.

---

# Reproductibilité

Le projet est entièrement reproductible.

Les étapes pour reproduire les résultats :

1. Installer les dépendances
2. Entraîner le modèle
3. Lancer l’application

---

# Enseignements du projet

Ce projet met en évidence :

* l’importance des **habitudes de vie dans la prédiction de l’obésité**
* la performance des **modèles de type gradient boosting**
* l’utilité de **l’IA explicable** dans le domaine médical

---

# Conclusion

Ce projet démontre comment le **machine learning explicable** peut être utilisé pour soutenir les professionnels de santé dans la prise de décision.

En combinant **prédiction automatique, transparence des modèles et interface interactive**, cette application constitue un outil utile pour le **suivi et la prévention de l’obésité**.

