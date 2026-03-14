"""
tests/test_patient_flow.py
==========================
Tests automatiques — Flux complet patient :
  1. Chargement du modèle
  2. Prédiction ML sur données patient
  3. Sauvegarde du dossier JSON
  4. UI Streamlit (AppTest) — saisie + résultat + recommandations

Lancer : pytest tests/test_patient_flow.py -v
"""

import pytest
import json
import os
import shutil
import numpy as np
import pandas as pd
import joblib
from datetime import datetime

# ── Données d'un patient test ──────────────────────────────────────────────────
PATIENT_TEST = {
    "Gender":                         1,
    "Age":                            28.0,
    "Height":                         1.75,
    "Weight":                         95.0,
    "family_history_with_overweight": 1,
    "FAVC":                           1,
    "FCVC":                           2,
    "NCP":                            3,
    "CAEC":                           1,
    "SMOKE":                          0,
    "CH2O":                           2,
    "SCC":                            0,
    "FAF":                            1,
    "TUE":                            1,
    "CALC":                           1,
    "MTRANS":                         2,
}

PATIENT_INFO = {"prenom": "Test", "nom": "Patient"}
PATIENT_ID   = "test_patient_001"
RECORDS_DIR  = "data/records"
MODEL_PATH   = "models/model.pkl"

CLASSES = [
    "Insufficient_Weight", "Normal_Weight",
    "Obesity_Type_I",      "Obesity_Type_II",
    "Obesity_Type_III",    "Overweight_Level_I",
    "Overweight_Level_II",
]

# ══════════════════════════════════════════════════════════════════════════════
# PARTIE 1 — Tests pytest purs (sans UI)
# ══════════════════════════════════════════════════════════════════════════════

class TestModeleML:
    """Tests du modèle ML"""

    def test_modele_existe(self):
        """Le fichier model.pkl doit exister"""
        paths = [
            "models/model.pkl",
            "outputs/lightgbm.pkl",
            "outputs/xgboost.pkl",
            "outputs/catboost.pkl",
            "outputs/random_forest.pkl",
        ]
        found = any(os.path.exists(p) for p in paths)
        assert found, "Aucun modèle trouvé dans models/ ou outputs/"

    def test_modele_chargeable(self):
        """Le modèle doit se charger sans erreur"""
        model = self._load_model()
        assert model is not None, "Impossible de charger le modèle"

    def test_modele_type_correct(self):
        """Le modèle doit avoir predict et predict_proba"""
        model = self._load_model()
        assert hasattr(model, "predict"),       "Le modèle n'a pas de méthode predict"
        assert hasattr(model, "predict_proba"), "Le modèle n'a pas de méthode predict_proba"

    def _load_model(self):
        for path in ["models/model.pkl", "outputs/lightgbm.pkl",
                     "outputs/xgboost.pkl", "outputs/catboost.pkl",
                     "outputs/random_forest.pkl"]:
            if os.path.exists(path):
                obj = joblib.load(path)
                if isinstance(obj, dict) and "model" in obj:
                    obj = obj["model"]
                return obj
        return None


class TestPrediction:
    """Tests de la prédiction ML sur le patient test"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.model = self._load_model()
        self.df    = pd.DataFrame([PATIENT_TEST])

    def _load_model(self):
        for path in ["models/model.pkl", "outputs/lightgbm.pkl",
                     "outputs/xgboost.pkl", "outputs/catboost.pkl",
                     "outputs/random_forest.pkl"]:
            if os.path.exists(path):
                obj = joblib.load(path)
                return obj["model"] if isinstance(obj, dict) else obj
        pytest.skip("Aucun modèle disponible")

    def test_prediction_retourne_un_resultat(self):
        """predict() doit retourner exactement 1 valeur"""
        result = self.model.predict(self.df)
        assert len(result) == 1, f"predict() a retourné {len(result)} résultats au lieu de 1"

    def test_prediction_classe_valide(self):
        """La classe prédite doit être un entier entre 0 et 6"""
        raw  = self.model.predict(self.df)
        pred = int(np.array(raw).flatten()[0])
        assert 0 <= pred <= 6, f"Classe prédite invalide : {pred}"

    def test_prediction_obese_pour_patient_test(self):
        """Un patient de 95kg/1.75m (IMC=31) doit être Obésité ou Surpoids"""
        raw  = self.model.predict(self.df)
        pred = int(np.array(raw).flatten()[0])
        label = CLASSES[pred]
        obese_or_overweight = [
            "Obesity_Type_I", "Obesity_Type_II", "Obesity_Type_III",
            "Overweight_Level_I", "Overweight_Level_II"
        ]
        assert label in obese_or_overweight, \
            f"Résultat inattendu pour IMC=31 : {label}"

    def test_probabilites_somme_100(self):
        """Les probabilités doivent sommer à ~1.0"""
        probas = self.model.predict_proba(self.df)[0]
        assert abs(sum(probas) - 1.0) < 1e-3, \
            f"Somme des probabilités = {sum(probas):.4f} (attendu ~1.0)"

    def test_probabilites_7_classes(self):
        """predict_proba doit retourner 7 probabilités (une par classe)"""
        probas = self.model.predict_proba(self.df)[0]
        assert len(probas) == 7, f"Nombre de classes : {len(probas)} (attendu 7)"

    def test_probabilites_entre_0_et_1(self):
        """Chaque probabilité doit être entre 0 et 1"""
        probas = self.model.predict_proba(self.df)[0]
        for i, p in enumerate(probas):
            assert 0 <= p <= 1, f"Probabilité invalide pour classe {i} : {p}"

    def test_imc_calcul_correct(self):
        """IMC = poids / taille² = 95 / 1.75² ≈ 31.0"""
        imc = PATIENT_TEST["Weight"] / (PATIENT_TEST["Height"] ** 2)
        assert 30.5 < imc < 31.5, f"IMC calculé : {imc:.2f} (attendu ~31.0)"


class TestSauvegarde:
    """Tests de lecture/écriture des dossiers JSON"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.makedirs(RECORDS_DIR, exist_ok=True)
        yield
        # Nettoyage après chaque test
        path = os.path.join(RECORDS_DIR, f"{PATIENT_ID}.json")
        if os.path.exists(path):
            os.remove(path)

    def _save_record(self, prediction="Obesity_Type_I", reco=""):
        record = {
            "patient_id":    PATIENT_ID,
            "patient_name":  "Test Patient",
            "date_analyse":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "doctor":        "Dr. Test",
            "prediction":    prediction,
            "confidence":    "96.0%",
            "BMI":           round(PATIENT_TEST["Weight"] / PATIENT_TEST["Height"] ** 2, 2),
            "clinical_data": PATIENT_TEST,
            "recommendations": reco,
        }
        path = os.path.join(RECORDS_DIR, f"{PATIENT_ID}.json")
        with open(path, "w") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
        return record

    def test_sauvegarde_cree_fichier(self):
        """La sauvegarde doit créer un fichier JSON"""
        self._save_record()
        path = os.path.join(RECORDS_DIR, f"{PATIENT_ID}.json")
        assert os.path.exists(path), "Le fichier JSON n'a pas été créé"

    def test_sauvegarde_contenu_correct(self):
        """Le JSON doit contenir les bonnes clés"""
        self._save_record(prediction="Obesity_Type_I", reco="Faire du sport")
        path = os.path.join(RECORDS_DIR, f"{PATIENT_ID}.json")
        with open(path) as f:
            data = json.load(f)
        assert data["patient_id"]  == PATIENT_ID,       "patient_id incorrect"
        assert data["prediction"]  == "Obesity_Type_I", "prediction incorrecte"
        assert data["BMI"]         > 0,                 "IMC invalide"
        assert "clinical_data"     in data,             "clinical_data manquant"

    def test_sauvegarde_recommandations(self):
        """Les recommandations doivent être sauvegardées correctement"""
        reco = "Réduire les sucres. Faire 30 min de sport/jour."
        self._save_record(reco=reco)
        path = os.path.join(RECORDS_DIR, f"{PATIENT_ID}.json")
        with open(path) as f:
            data = json.load(f)
        assert data["recommendations"] == reco, "Recommandations non sauvegardées"

    def test_mise_a_jour_sans_ecraser_reco(self):
        """Mettre à jour un dossier ne doit pas effacer les recommandations existantes"""
        self._save_record(reco="Recommandation originale")
        path = os.path.join(RECORDS_DIR, f"{PATIENT_ID}.json")

        # Simuler une mise à jour (comme dans doctor_result.py)
        with open(path) as f:
            existing = json.load(f)
        existing["date_analyse"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(path, "w") as f:
            json.dump(existing, f, indent=2)

        with open(path) as f:
            updated = json.load(f)
        assert updated["recommendations"] == "Recommandation originale", \
            "Les recommandations ont été écrasées lors de la mise à jour"

    def test_json_valide(self):
        """Le fichier JSON doit être valide (parseable)"""
        self._save_record()
        path = os.path.join(RECORDS_DIR, f"{PATIENT_ID}.json")
        try:
            with open(path) as f:
                json.load(f)
        except json.JSONDecodeError:
            pytest.fail("Le fichier JSON généré est invalide")


# ══════════════════════════════════════════════════════════════════════════════
# PARTIE 2 — Tests AppTest (UI Streamlit)
# ══════════════════════════════════════════════════════════════════════════════

try:
    from streamlit.testing.v1 import AppTest
    APPTEST_AVAILABLE = True
except ImportError:
    APPTEST_AVAILABLE = False


# ── NOTE : st.page_link() ne fonctionne pas dans AppTest (besoin du contexte
#           multi-pages complet). On utilise des tests d'intégration à la place.

class TestIntegrationFluxUI:
    """
    Tests d'intégration simulant le flux UI complet
    sans AppTest (contourne la limitation st.page_link)
    """

    def _load_model(self):
        for path in ["models/model.pkl", "outputs/lightgbm.pkl",
                     "outputs/xgboost.pkl", "outputs/catboost.pkl",
                     "outputs/random_forest.pkl"]:
            if os.path.exists(path):
                obj = joblib.load(path)
                return obj["model"] if isinstance(obj, dict) else obj
        return None

    def test_simulation_saisie_patient(self):
        """Simule la saisie d'un nouveau patient (doctor_data_entry)"""
        # Vérifie que les données du formulaire sont bien structurées
        assert len(PATIENT_TEST) == 16, "Le patient doit avoir 16 features"
        assert "Weight" in PATIENT_TEST
        assert "Height" in PATIENT_TEST
        assert "Age"    in PATIENT_TEST
        bmi = PATIENT_TEST["Weight"] / (PATIENT_TEST["Height"] ** 2)
        assert bmi > 0, "IMC doit être positif"

    def test_simulation_prediction_et_affichage(self):
        """Simule doctor_result : prédiction + sauvegarde"""
        model = self._load_model()
        if model is None:
            pytest.skip("Aucun modèle disponible")

        df     = pd.DataFrame([PATIENT_TEST])
        raw    = model.predict(df)
        pred   = int(np.array(raw).flatten()[0])
        probas = model.predict_proba(df)[0]

        assert 0 <= pred <= 6,              "Classe invalide"
        assert len(probas) == 7,            "7 classes attendues"
        assert abs(sum(probas) - 1.0) < 1e-3, "Probas doivent sommer à 1"

        # Simule la sauvegarde du dossier
        os.makedirs(RECORDS_DIR, exist_ok=True)
        record = {
            "patient_id":    PATIENT_ID,
            "patient_name":  "Test Patient",
            "date_analyse":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "doctor":        "Dr. Test",
            "prediction":    CLASSES[pred],
            "confidence":    f"{probas.max()*100:.1f}%",
            "BMI":           round(PATIENT_TEST["Weight"] / PATIENT_TEST["Height"]**2, 2),
            "clinical_data": PATIENT_TEST,
        }
        path = os.path.join(RECORDS_DIR, f"{PATIENT_ID}.json")
        with open(path, "w") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

        assert os.path.exists(path), "Fichier JSON non créé"
        os.remove(path)

    def test_simulation_recommandations(self):
        """Simule doctor_recommendations : écriture des recommandations"""
        os.makedirs(RECORDS_DIR, exist_ok=True)
        path = os.path.join(RECORDS_DIR, f"{PATIENT_ID}.json")

        # Dossier initial (après doctor_result)
        record = {
            "patient_id": PATIENT_ID,
            "prediction": "Obesity_Type_I",
            "BMI":        31.0,
        }
        with open(path, "w") as f:
            json.dump(record, f)

        # Simule l'ajout des recommandations
        reco = "Faire 30 min de sport par jour. Réduire les sucres."
        diet = "Déjeuner : salade + poulet. Dîner : légumes vapeur."

        with open(path) as f:
            existing = json.load(f)
        existing.update({
            "recommendations": reco,
            "diet_plan":       diet,
            "reco_date":       datetime.now().strftime("%d/%m/%Y à %H:%M"),
            "reco_author":     "Dr. Test",
        })
        with open(path, "w") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

        # Vérification
        with open(path) as f:
            saved = json.load(f)

        assert saved["recommendations"] == reco, "Recommandations non sauvegardées"
        assert saved["diet_plan"]       == diet, "Plan alimentaire non sauvegardé"
        assert "reco_date"   in saved,           "Date de reco manquante"
        assert "reco_author" in saved,           "Auteur de reco manquant"

        os.remove(path)

    def test_simulation_flux_complet_enchaine(self):
        """
        Simule les 3 étapes enchaînées :
        data_entry → result → recommendations
        """
        model = self._load_model()
        if model is None:
            pytest.skip("Aucun modèle disponible")

        os.makedirs(RECORDS_DIR, exist_ok=True)
        path = os.path.join(RECORDS_DIR, f"{PATIENT_ID}.json")

        # ── ÉTAPE 1 : Saisie (data_entry) ─────────────────────
        assert len(PATIENT_TEST) == 16

        # ── ÉTAPE 2 : Prédiction (result) ─────────────────────
        df     = pd.DataFrame([PATIENT_TEST])
        raw    = model.predict(df)
        pred   = int(np.array(raw).flatten()[0])
        probas = model.predict_proba(df)[0]
        bmi    = PATIENT_TEST["Weight"] / PATIENT_TEST["Height"]**2

        record = {
            "patient_id":    PATIENT_ID,
            "patient_name":  "Test Patient",
            "date_analyse":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "doctor":        "Dr. Test",
            "prediction":    CLASSES[pred],
            "confidence":    f"{probas.max()*100:.1f}%",
            "BMI":           round(bmi, 2),
            "clinical_data": PATIENT_TEST,
        }
        with open(path, "w") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

        # ── ÉTAPE 3 : Recommandations ──────────────────────────
        with open(path) as f:
            existing = json.load(f)
        existing.update({
            "recommendations": "Réduire les sucres raffinés.",
            "diet_plan":       "3 repas/jour, pas de grignotage.",
            "reco_date":       datetime.now().strftime("%d/%m/%Y à %H:%M"),
        })
        with open(path, "w") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

        # ── Vérification finale ────────────────────────────────
        with open(path) as f:
            final = json.load(f)

        assert final["patient_id"]      == PATIENT_ID
        assert final["prediction"]      in CLASSES
        assert final["BMI"]             > 0
        assert final["recommendations"] != ""
        assert final["diet_plan"]       != ""

        print(f"\n✅ Flux complet OK — {final['prediction']} | IMC {final['BMI']} | {final['confidence']}")
        os.remove(path)


# ══════════════════════════════════════════════════════════════════════════════
# RAPPORT FINAL
# ══════════════════════════════════════════════════════════════════════════════

def test_flux_complet_sans_ui():
    """
    TEST D'INTÉGRATION — Simule le flux complet :
    saisie → prédiction → sauvegarde → vérification
    """
    # 1. Charger le modèle
    model = None
    for path in ["models/model.pkl", "outputs/lightgbm.pkl",
                 "outputs/xgboost.pkl", "outputs/catboost.pkl",
                 "outputs/random_forest.pkl"]:
        if os.path.exists(path):
            obj = joblib.load(path)
            model = obj["model"] if isinstance(obj, dict) else obj
            break

    if model is None:
        pytest.skip("Aucun modèle disponible")

    # 2. Prédiction
    df   = pd.DataFrame([PATIENT_TEST])
    raw  = model.predict(df)
    pred = int(np.array(raw).flatten()[0])
    assert 0 <= pred <= 6

    probas = model.predict_proba(df)[0]
    assert abs(sum(probas) - 1.0) < 1e-3
    assert len(probas) == 7

    bmi = PATIENT_TEST["Weight"] / (PATIENT_TEST["Height"] ** 2)

    # 3. Sauvegarde
    os.makedirs(RECORDS_DIR, exist_ok=True)
    record = {
        "patient_id":      PATIENT_ID,
        "patient_name":    "Test Patient",
        "date_analyse":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "doctor":          "Dr. Test",
        "prediction":      ["Insufficient_Weight","Normal_Weight","Obesity_Type_I",
                            "Obesity_Type_II","Obesity_Type_III","Overweight_Level_I",
                            "Overweight_Level_II"][pred],
        "confidence":      f"{probas.max()*100:.1f}%",
        "BMI":             round(bmi, 2),
        "clinical_data":   PATIENT_TEST,
        "recommendations": "Test automatique — recommandations simulées.",
    }
    path = os.path.join(RECORDS_DIR, f"{PATIENT_ID}.json")
    with open(path, "w") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    # 4. Vérification
    assert os.path.exists(path)
    with open(path) as f:
        saved = json.load(f)
    assert saved["patient_id"]  == PATIENT_ID
    assert saved["BMI"]         > 0
    assert saved["prediction"]  in ["Insufficient_Weight","Normal_Weight","Obesity_Type_I",
                                    "Obesity_Type_II","Obesity_Type_III","Overweight_Level_I",
                                    "Overweight_Level_II"]
    assert saved["recommendations"] != ""

    print(f"\n✅ Flux complet OK — Prédiction : {saved['prediction']} | IMC : {saved['BMI']} | Confiance : {saved['confidence']}")

    # Nettoyage
    os.remove(path)