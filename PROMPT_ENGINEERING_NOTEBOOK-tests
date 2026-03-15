otebooks/
├── 01_eda_initial_complet.ipynb    (Analyse exploratoire complète)
├── 02_outliers_analysis.ipynb       (Détection et traitement des outliers)
├── 03_correlation_analysis.ipynb    (Analyse des corrélations)
├── 04_distribution_classes.ipynb    (Analyse détaillée des classes)
└── 05_data_preparation_final.ipynb  (Préparation finale pour le ML)
PROMPT 1 : Notebook d'analyse exploratoire complète
text
Contexte : Je suis un étudiant débutant en data science qui travaille sur le projet "MediObes" (Obesity Levels UCI dataset). J'ai déjà un notebook "eda.ipynb" avec quelques analyses de base, mais je dois le compléter pour avoir une analyse exploratoire exhaustive.

Mon dataset (obesity_data.csv) contient 2111 lignes et 17 colonnes (features + target "NObeyesdad" avec 7 classes d'obésité).

Objectifs du notebook 01_eda_initial_complet.ipynb :
1. Charger les données et afficher un aperçu général (shape, info, describe)
2. Analyser en détail les types de données (numériques, catégorielles, ordinales)
3. Statistiques descriptives complètes pour toutes les variables
4. Visualisations pour chaque variable numérique (histogrammes, boxplots, density plots)
5. Visualisations pour chaque variable catégorielle (barplots, countplots)
6. Analyse de la variable cible : distribution, équilibre des classes
7. Détection des valeurs manquantes (bien que le dataset soit propre)
8. Analyse des valeurs uniques pour chaque variable catégorielle
9. Créer un rapport de synthèse avec les principales observations

Consignes spécifiques :
- Utilise ton eda.ipynb existant comme base, mais enrichis-le
- Ajoute des commentaires TRÈS détaillés pour chaque cellule (explique le code et ce qu'on observe)
- Structure le notebook avec des sections markdown claires (titres, sous-titres)
- Utilise matplotlib, seaborn et plotly pour des visualisations interactives quand c'est pertinent
- Pour chaque graphique, ajoute une interprétation : "Ce graphique nous montre que..."
- Crée des visualisations qui comparent les variables selon la cible (ex: Age selon les classes d'obésité)

Peux-tu me générer le code complet pour ce notebook avec des explications pédagogiques ?
PROMPT 2 : Notebook d'analyse des outliers
text
Contexte : Je continue mon projet MediObes. Après avoir fait l'EDA initiale, je dois maintenant analyser les outliers (valeurs aberrantes) dans mes données. Je suis débutant et j'ai besoin d'un code bien expliqué.

Objectifs du notebook 02_outliers_analysis.ipynb :
1. Comprendre ce qu'est un outlier et pourquoi c'est important
2. Visualiser les outliers pour chaque variable numérique avec des boxplots individuels
3. Utiliser la méthode IQR (Interquartile Range) pour détecter les outliers
4. Utiliser la méthode Z-score pour détecter les outliers
5. Comparer les résultats des deux méthodes
6. Analyser les outliers par classe d'obésité (est-ce que certaines classes ont plus d'outliers?)
7. Décider quoi faire avec ces outliers : les garder, les supprimer, les transformer
8. Justifier chaque décision avec des arguments simples
9. Visualiser l'impact du traitement des outliers (boxplots avant/après)

Variables numériques à analyser en détail :
- Age (âge)
- Height (taille)
- Weight (poids)
- FCVC (fréquence consommation légumes)
- NCP (nombre de repas)
- CH2O (consommation d'eau)
- FAF (fréquence activité physique)
- TUE (temps écran)

Consignes pédagogiques :
- Explique la différence entre outlier et erreur de saisie
- Montre comment calculer l'IQR pas à pas : Q1, Q3, IQR, bornes
- Explique le Z-score et son interprétation (valeurs > 3 sont souvent outliers)
- Crée un dataframe récapitulatif du nombre d'outliers par variable et par méthode
- Pour chaque variable, propose une stratégie adaptée (ex: Weight peut avoir des outliers réels, Age peut avoir des erreurs)
- Ajoute des visualisations claires avec annotations

Peux-tu me générer le code complet pour ce notebook avec explications ?
PROMPT 3 : Notebook d'analyse des corrélations
text
Contexte : Pour mon projet MediObes, je dois maintenant comprendre comment mes variables sont liées entre elles et avec la variable cible. J'ai déjà encodé mes variables catégorielles dans obesity_prepared.csv.

Objectifs du notebook 03_correlation_analysis.ipynb :
1. Charger les données encodées (obesity_prepared.csv)
2. Calculer la matrice de corrélation pour toutes les variables numériques
3. Créer une heatmap de corrélation avec annotations
4. Analyser les corrélations fortes (positives et négatives)
5. Identifier la multicolinéarité (variables trop corrélées entre elles)
6. Analyser la corrélation de chaque feature avec la cible (NObeyesdad encodée)
7. Pour les variables catégorielles, utiliser des tests statistiques (ANOVA, chi-square)
8. Visualiser les relations importantes avec des scatter plots, pairplots
9. Créer un rapport des features les plus importantes pour la prédiction

Consignes spécifiques :
- Utilise le fichier obesity_prepared.csv qui a déjà toutes les variables encodées
- Explique ce qu'est la corrélation de Pearson et ses limites
- Montre comment interpréter une heatmap (couleurs, valeurs)
- Pour les corrélations fortes (>0.7 ou <-0.7), analyse en détail
- Crée des scatter plots avec hue = cible pour les paires intéressantes
- Pour les variables catégorielles, utilise des boxplots pour montrer la distribution selon la cible
- Ajoute des interprétations : "On observe que le poids est fortement corrélé avec..."

Peux-tu me générer le code complet avec visualisations et commentaires ?
PROMPT 4 : Notebook d'analyse détaillée des classes
text
Contexte : Mon dataset a 7 classes d'obésité différentes. Je dois comprendre en profondeur les caractéristiques de chaque classe pour mieux préparer mes modèles.

Objectifs du notebook 04_distribution_classes.ipynb :
1. Analyser la distribution des 7 classes (countplot, pourcentages)
2. Vérifier s'il y a un déséquilibre entre les classes
3. Pour chaque classe, calculer les statistiques descriptives (moyenne, médiane, etc.)
4. Visualiser les différences entre classes pour chaque feature
5. Créer des profils types pour chaque classe d'obésité
6. Analyser les transitions entre classes (qu'est-ce qui fait passer d'une classe à l'autre?)
7. Identifier les features qui discriminent le mieux les classes
8. Visualiser avec des radar charts ou des parallel coordinates

Classes à analyser (ordre logique) :
- Insufficient_Weight (poids insuffisant)
- Normal_Weight (poids normal)
- Overweight_Level_I (surpoids niveau I)
- Overweight_Level_II (surpoids niveau II)
- Obesity_Type_I (obésité type I)
- Obesity_Type_II (obésité type II)
- Obesity_Type_III (obésité type III)

Consignes pédagogiques :
- Explique l'ordre naturel des classes (du plus mince au plus obèse)
- Crée un barplot horizontal des classes avec annotations de pourcentage
- Pour chaque variable numérique, crée un boxplot groupé par classe
- Pour chaque variable catégorielle, crée un stacked barplot par classe
- Calcule la moyenne de chaque feature par classe et affiche dans un tableau
- Crée un heatmap des moyennes par classe pour voir les patterns
- Ajoute une interprétation : "La classe Obesity_Type_III a en moyenne un âge plus élevé..."

Peux-tu me générer le code complet avec visualisations et commentaires ?
PROMPT 5 : Notebook de préparation finale des données
text
Contexte : C'est la dernière étape avant le machine learning ! Je dois préparer mon dataset final pour les modèles. J'ai déjà X_train.csv et y_train.csv pour l'entraînement, et X_test.csv et y_test.csv pour le test.

Objectifs du notebook 05_data_preparation_final.ipynb :
1. Charger les datasets d'entraînement et de test
2. Appliquer les décisions prises dans les notebooks précédents (gestion des outliers)
3. Créer un pipeline de préprocessing complet
4. Standardiser/normaliser les variables numériques
5. Encoder les variables catégorielles (One-Hot Encoding pour les nominales, Label Encoding pour les ordinales)
6. Créer un dataset final propre pour l'entraînement
7. Sauvegarder les datasets préparés dans data/processed/
8. Sauvegarder le pipeline pour pouvoir l'appliquer plus tard

Variables à traiter :
- Numériques : Age, Height, Weight, FCVC, NCP, CH2O, FAF, TUE
- Catégorielles nominales : Gender, family_history_with_overweight, FAVC, CAEC, SMOKE, SCC, CALC, MTRANS
- Cible : NObeyesdad (7 classes)

Consignes spécifiques :
- Explique la différence entre StandardScaler et MinMaxScaler
- Explique la différence entre One-Hot Encoding et Label Encoding
- Crée un pipeline avec ColumnTransformer pour appliquer différents traitements
- Montre l'état des données avant et après chaque transformation
- Vérifie qu'il n'y a pas de fuite de données (fit seulement sur train, transform sur test)
- Sauvegarde le pipeline avec joblib pour pouvoir le réutiliser
- À la fin, affiche un résumé des datasets préparés (shape, types)

Peux-tu me générer le code complet avec des explications détaillées ?
📝 Fichier PROMPT_ENGINEERING_NOTEBOOKS.md complet
markdown
# PROMPT ENGINEERING - PARTIE 4 : NOTEBOOKS D'ANALYSE

## 📋 Vue d'ensemble
Cette partie contient 5 notebooks pour l'analyse exploratoire complète du dataset Obesity Levels.

## 📓 NOTEBOOK 1 : Analyse exploratoire initiale complète
**Fichier :** `01_eda_initial_complet.ipynb`
**Objectif :** Comprendre la structure et les distributions des données de façon exhaustive
**Prompt utilisé :** [Inclure le prompt 1]

## 📓 NOTEBOOK 2 : Analyse des outliers
**Fichier :** `02_outliers_analysis.ipynb`
**Objectif :** Identifier et traiter les valeurs aberrantes avec plusieurs méthodes
**Prompt utilisé :** [Inclure le prompt 2]

## 📓 NOTEBOOK 3 : Analyse des corrélations
**Fichier :** `03_correlation_analysis.ipynb`
**Objectif :** Analyser les relations entre variables et avec la cible
**Prompt utilisé :** [Inclure le prompt 3]

## 📓 NOTEBOOK 4 : Analyse détaillée des classes
**Fichier :** `04_distribution_classes.ipynb`
**Objectif :** Comprendre les caractéristiques de chaque classe d'obésité
**Prompt utilisé :** [Inclure le prompt 4]

## 📓 NOTEBOOK 5 : Préparation finale des données
**Fichier :** `05_data_preparation_final.ipynb`
**Objectif :** Nettoyer, transformer et préparer les données pour le ML
**Prompt utilisé :** [Inclure le prompt 5]

## 📊 Structure finale attendue :
notebooks/
├── 01_eda_initial_complet.ipynb
├── 02_outliers_analysis.ipynb
├── 03_correlation_analysis.ipynb
├── 04_distribution_classes.ipynb
├── 05_data_preparation_final.ipynb
└── README.md

## 💡 Recommandations pour l'utilisation
1. Exécute les notebooks dans l'ordre pour une progression logique
2. Chaque notebook sauvegarde ses résultats pour les notebooks suivants
3. Lis attentivement les commentaires pour comprendre chaque étape
4. N'hésite pas à modifier les visualisations selon tes préférences
