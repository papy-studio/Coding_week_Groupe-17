"""
MEDIOBES - Membre 5 (Modèle + SHAP)
Fichier unique et prêt à l'emploi
"""

import joblib
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt
import io
import base64
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.preprocessing import LabelEncoder

# ============================================================
# PARTIE 1: ENTRAÎNEMENT DU MODÈLE
# ============================================================

def train_and_save_models(df_path='../data/processed/obesity_processed.csv'):
    """Entraîne tous les modèles et sauvegarde le meilleur"""
    
    # Charger données
    df = pd.read_csv(df_path)
    X = df.drop('NObeyesdad', axis=1)
    y = df['NObeyesdad']
    
    # Encoder
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    # Modèles
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
        'XGBoost': XGBClassifier(n_estimators=100, random_state=42),
        'LightGBM': LGBMClassifier(n_estimators=100, random_state=42, verbose=-1),
        'CatBoost': CatBoostClassifier(n_estimators=100, random_state=42, verbose=0)
    }
    
    # Entraînement et évaluation
    results = {}
    best_f1 = 0
    best_model = None
    best_name = ""
    
    print("Entraînement des modèles...")
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        f1 = f1_score(y_test, y_pred, average='macro')
        results[name] = f1
        
        if f1 > best_f1:
            best_f1 = f1
            best_model = model
            best_name = name
        
        # Sauvegarder
        os.makedirs('../models', exist_ok=True)
        joblib.dump(model, f'../models/{name}.pkl')
        print(f"  {name}: F1 = {f1:.4f}")
    
    # Sauvegarder meilleur modèle
    joblib.dump(best_model, '../models/best_model.pkl')
    joblib.dump(le, '../models/label_encoder.pkl')
    joblib.dump(X.columns.tolist(), '../models/feature_names.pkl')
    
    print(f"\n✅ Meilleur modèle: {best_name} (F1 = {best_f1:.4f})")
    return best_model, le, X.columns.tolist()

# ============================================================
# PARTIE 2: CHARGEUR DE MODÈLE
# ============================================================

class ModelLoader:
    """Charge le modèle et fait des prédictions"""
    
    def __init__(self, model_path='models/best_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.label_encoder = None
        self.feature_names = None
    
    def load(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Modèle introuvable: {self.model_path}")
        
        self.model = joblib.load(self.model_path)
        self.label_encoder = joblib.load('models/label_encoder.pkl')
        self.feature_names = joblib.load('models/feature_names.pkl')
        return self
    
    def predict(self, features_df):
        if self.model is None:
            self.load()
        
        # Réordonner les features
        features_df = features_df[self.feature_names]
        
        # Prédire
        pred_encoded = self.model.predict(features_df)[0]
        pred_proba = self.model.predict_proba(features_df)[0]
        pred_label = self.label_encoder.inverse_transform([pred_encoded])[0]
        
        # Distribution
        probabilities = {}
        for label, prob in zip(self.label_encoder.classes_, pred_proba):
            probabilities[label] = float(prob)
        
        return {
            'prediction': pred_label,
            'probability': float(max(pred_proba)),
            'probabilities': probabilities
        }

# ============================================================
# PARTIE 3: EXPLICABILITÉ SHAP
# ============================================================

class ShapExplainer:
    """Gère les explications SHAP"""
    
    def __init__(self, model, feature_names):
        self.model = model
        self.feature_names = feature_names
        self.explainer = shap.TreeExplainer(model)
    
    def get_waterfall_base64(self, patient_data):
        """Retourne le waterfall plot en base64"""
        shap_values = self.explainer.shap_values(patient_data)
        
        # Gérer multi-classes
        if isinstance(shap_values, list):
            pred_class = self.model.predict(patient_data)[0]
            if hasattr(self.model, 'classes_'):
                class_idx = list(self.model.classes_).index(pred_class)
            else:
                class_idx = 0
            shap_vals = shap_values[class_idx][0]
            expected = self.explainer.expected_value[class_idx]
        else:
            shap_vals = shap_values[0]
            expected = self.explainer.expected_value
        
        # Créer plot
        plt.figure(figsize=(10, 5))
        shap.waterfall_plot(
            shap.Explanation(
                values=shap_vals,
                base_values=expected,
                data=patient_data.iloc[0].values,
                feature_names=self.feature_names
            ),
            show=False
        )
        
        # Convertir en base64
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        return img_base64
    
    def get_top_features(self, patient_data, n=5):
        """Retourne les n features les plus importantes"""
        shap_values = self.explainer.shap_values(patient_data)
        
        if isinstance(shap_values, list):
            pred_class = self.model.predict(patient_data)[0]
            if hasattr(self.model, 'classes_'):
                class_idx = list(self.model.classes_).index(pred_class)
            else:
                class_idx = 0
            shap_vals = shap_values[class_idx][0]
        else:
            shap_vals = shap_values[0]
        
        df = pd.DataFrame({
            'feature': self.feature_names,
            'impact': shap_vals,
            'abs_impact': np.abs(shap_vals)
        }).sort_values('abs_impact', ascending=False).head(n)
        
        return df[['feature', 'impact']].to_dict('records')

# ============================================================
# PARTIE 4: UTILITAIRES (IMC, etc.)
# ============================================================

def calculate_bmi(height, weight):
    """Calcule l'IMC"""
    if height <= 0 or weight <= 0:
        return None
    return round(weight / (height ** 2), 1)

def get_bmi_category(bmi):
    """Catégorie IMC"""
    if bmi is None:
        return "Non calculable"
    if bmi < 18.5:
        return "Insuffisance pondérale"
    elif bmi < 25:
        return "Poids normal"
    elif bmi < 30:
        return "Surpoids"
    elif bmi < 35:
        return "Obésité modérée"
    elif bmi < 40:
        return "Obésité sévère"
    else:
        return "Obésité morbide"

def get_risk_level(prediction):
    """Niveau de risque"""
    high_risk = ['Obesity_Type_I', 'Obesity_Type_II', 'Obesity_Type_III']
    medium_risk = ['Overweight_Level_I', 'Overweight_Level_II']
    
    if prediction in high_risk:
        return "Élevé", "🔴"
    elif prediction in medium_risk:
        return "Modéré", "🟠"
    else:
        return "Faible", "🟢"

def prepare_features(form_data, feature_names):
    """Convertit formulaire en DataFrame"""
    
    # Mapping de base (adapte selon tes features)
    mapping = {
        'Age': float(form_data.get('age', 30)),
        'Height': float(form_data.get('height', 1.75)),
        'Weight': float(form_data.get('weight', 70)),
        'FCVC': float(form_data.get('fcvc', 2.0)),
        'NCP': float(form_data.get('ncp', 3.0)),
        'CH2O': float(form_data.get('ch2o', 2.0)),
        'FAF': float(form_data.get('faf', 1.0)),
        'TUE': float(form_data.get('tue', 1.0)),
    }
    
    # Créer DataFrame avec toutes les features
    features = {}
    for name in feature_names:
        features[name] = mapping.get(name, 0.0)
    
    return pd.DataFrame([features])

# ============================================================
# PARTIE 5: TESTS RAPIDES
# ============================================================

def test_all():
    """Teste toutes les fonctions"""
    print("Test des fonctions...")
    
    # Test IMC
    bmi = calculate_bmi(1.75, 70)
    assert bmi == 22.9
    assert get_bmi_category(bmi) == "Poids normal"
    
    # Test risque
    risk, icon = get_risk_level("Obesity_Type_I")
    assert risk == "Élevé"
    
    print("✅ Tous les tests passent!")

# ============================================================
# MAIN: Exemple d'utilisation
# ============================================================

if __name__ == "__main__":
    print("="*50)
    print("MEDIOBES - Module Modèle + SHAP (Membre 5)")
    print("="*50)
    
    # 1. Tester les utilitaires
    test_all()
    
    # 2. Exemple d'utilisation avec le modèle
    try:
        # Charger modèle
        loader = ModelLoader('models/best_model.pkl')
        loader.load()
        print(f"\n✅ Modèle chargé avec {len(loader.feature_names)} features")
        
        # Créer données test
        test_data = pd.DataFrame([np.zeros(len(loader.feature_names))], 
                                columns=loader.feature_names)
        
        # Prédire
        result = loader.predict(test_data)
        print(f"Prédiction: {result['prediction']}")
        print(f"Confiance: {result['probability']*100:.1f}%")
        
        # SHAP
        explainer = ShapExplainer(loader.model, loader.feature_names)
        print("✅ Explainers SHAP prêt")
        
    except Exception as e:
        print(f"\n⚠️ Modèle non trouvé: {e}")
        print("Entraîne d'abord le modèle avec train_and_save_models()")

        from membre5_model_shap import ModelLoader, prepare_features, calculate_bmi

loader = ModelLoader('models/best_model.pkl')
loader.load()

# Données d'un patient
patient = {'age': 35, 'height': 1.80, 'weight': 85, 'fcvc': 2.5}
features = prepare_features(patient, loader.feature_names)

result = loader.predict(features)
bmi = calculate_bmi(1.80, 85)

print(f"Risque: {result['prediction']}, IMC: {bmi}")



import streamlit as st
from membre5_model_shap import ModelLoader, ShapExplainer, calculate_bmi, prepare_features

loader = ModelLoader()
loader.load()
explainer = ShapExplainer(loader.model, loader.feature_names)

# ... ton code Streamlit ...