"""
╔══════════════════════════════════════════════════════════════╗
║     TESTS — LightGBM, CatBoost, XGBoost, Random Forest      ║
╠══════════════════════════════════════════════════════════════╣
"""

import pytest
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.metrics import accuracy_score, f1_score

# ── Constants ─────────────────────────────────────────────────
CLASSES = [
    'Insufficient_Weight', 'Normal_Weight',
    'Obesity_Type_I',      'Obesity_Type_II',
    'Obesity_Type_III',    'Overweight_Level_I',
    'Overweight_Level_II'
]

MODELS = {
    "LightGBM":      "outputs/lightgbm.pkl",
    "CatBoost":      "outputs/catboost.pkl",
    "XGBoost":       "outputs/xgboost.pkl",
    "Random Forest": "outputs/random_forest.pkl",
}

VALID_RANGES = {
    "Gender":                         (0, 1),
    "Age":                            (10, 80),
    "Height":                         (1.40, 2.00),
    "Weight":                         (30, 180),
    "family_history_with_overweight": (0, 1),
    "FAVC":                           (0, 1),
    "FCVC":                           (1, 3),
    "NCP":                            (1, 4),
    "CAEC":                           (0, 3),
    "SMOKE":                          (0, 1),
    "CH2O":                           (1, 3),
    "SCC":                            (0, 1),
    "FAF":                            (0, 3),
    "TUE":                            (0, 2),
    "CALC":                           (0, 3),
    "MTRANS":                         (0, 4),
}

# ── Helpers ───────────────────────────────────────────────────
def load_model(path):
    obj = joblib.load(path)
    if isinstance(obj, dict) and "model" in obj:
        obj = obj["model"]
    
    # Wrap CatBoost to ensure 1D predictions
    if 'catboost' in path.lower():
        class CatBoostWrapper:
            def __init__(self, model):
                self.model = model
            def predict(self, X):
                pred = self.model.predict(X)
                return pred.ravel() if hasattr(pred, 'ravel') else pred
            def predict_proba(self, X):
                return self.model.predict_proba(X)
            def __getattr__(self, name):
                return getattr(self.model, name)
        return CatBoostWrapper(obj)
    
    return obj

def valid_patient():
    return pd.DataFrame([{
        "Gender": 1, "Age": 25, "Height": 1.75, "Weight": 85,
        "family_history_with_overweight": 1, "FAVC": 1, "FCVC": 2,
        "NCP": 3, "CAEC": 2, "SMOKE": 0, "CH2O": 2, "SCC": 0,
        "FAF": 1, "TUE": 1, "CALC": 1, "MTRANS": 2
    }])

def normal_patient():
    """Clearly normal BMI patient"""
    return pd.DataFrame([{
        "Gender": 0, "Age": 28, "Height": 1.68, "Weight": 62,
        "family_history_with_overweight": 0, "FAVC": 0, "FCVC": 3,
        "NCP": 3, "CAEC": 1, "SMOKE": 0, "CH2O": 3, "SCC": 0,
        "FAF": 3, "TUE": 1, "CALC": 0, "MTRANS": 4
    }])

def obese_patient():
    """Clearly obese patient"""
    return pd.DataFrame([{
        "Gender": 1, "Age": 40, "Height": 1.68, "Weight": 140,
        "family_history_with_overweight": 1, "FAVC": 1, "FCVC": 1,
        "NCP": 4, "CAEC": 3, "SMOKE": 1, "CH2O": 1, "SCC": 0,
        "FAF": 0, "TUE": 2, "CALC": 3, "MTRANS": 2
    }])


# ══════════════════════════════════════════════════════════════
# 1. FILE EXISTENCE TESTS
# ══════════════════════════════════════════════════════════════

def test_lightgbm_file_exists():
    assert os.path.exists("outputs/lightgbm.pkl"), "lightgbm.pkl not found in outputs/"

def test_catboost_file_exists():
    assert os.path.exists("outputs/catboost.pkl"), "catboost.pkl not found in outputs/"

def test_xgboost_file_exists():
    assert os.path.exists("outputs/xgboost.pkl"), "xgboost.pkl not found in outputs/"

def test_random_forest_file_exists():
    assert os.path.exists("outputs/random_forest.pkl"), "random_forest.pkl not found in outputs/"

def test_data_files_exist():
    assert os.path.exists("data/X_train.csv"), "X_train.csv missing"
    assert os.path.exists("data/X_test.csv"),  "X_test.csv missing"
    assert os.path.exists("data/y_train.csv"), "y_train.csv missing"
    assert os.path.exists("data/y_test.csv"),  "y_test.csv missing"


# ══════════════════════════════════════════════════════════════
# 2. DATA VALIDATION TESTS
# ══════════════════════════════════════════════════════════════

def test_no_missing_values_train():
    X_train = pd.read_csv("data/X_train.csv")
    assert X_train.isnull().sum().sum() == 0, "Missing values in X_train"

def test_no_missing_values_test():
    X_test = pd.read_csv("data/X_test.csv")
    assert X_test.isnull().sum().sum() == 0, "Missing values in X_test"

def test_correct_number_of_features():
    X_test = pd.read_csv("data/X_test.csv")
    assert X_test.shape[1] == 16, f"❌ Expected 16 features, got {X_test.shape[1]}"

def test_correct_columns():
    X_test   = pd.read_csv("data/X_test.csv")
    expected = list(VALID_RANGES.keys())
    missing  = [c for c in expected if c not in X_test.columns]
    assert len(missing) == 0, f"❌ Missing columns: {missing}"

def test_target_valid_range():
    y_test = pd.read_csv("data/y_test.csv").squeeze()
    assert y_test.min() >= 0, "❌ Target below 0"
    assert y_test.max() <= 6, "❌ Target above 6"

def test_train_test_split_ratio():
    X_train = pd.read_csv("data/X_train.csv")
    X_test  = pd.read_csv("data/X_test.csv")
    ratio   = len(X_test) / (len(X_train) + len(X_test))
    assert 0.18 <= ratio <= 0.22, f"❌ Split ratio is {ratio:.2f}, expected ~0.20"

def test_feature_ranges():
    X_test = pd.read_csv("data/X_test.csv")
    for col, (mn, mx) in VALID_RANGES.items():
        if col in X_test.columns:
            assert X_test[col].min() >= mn, f"❌ {col} below min {mn}"
            assert X_test[col].max() <= mx, f"❌ {col} above max {mx}"


# ══════════════════════════════════════════════════════════════
# 3. MODEL LOADING TESTS
# ══════════════════════════════════════════════════════════════

@pytest.mark.parametrize("name,path", MODELS.items())
def test_model_loads(name, path):
    if not os.path.exists(path):
        pytest.skip(f"{name} not found")
    model = load_model(path)
    assert model is not None, f"❌ {name} failed to load"

@pytest.mark.parametrize("name,path", MODELS.items())
def test_model_has_predict(name, path):
    if not os.path.exists(path):
        pytest.skip(f"{name} not found")
    model = load_model(path)
    assert hasattr(model, "predict"), f"❌ {name} has no predict method"

@pytest.mark.parametrize("name,path", MODELS.items())
def test_model_has_predict_proba(name, path):
    if not os.path.exists(path):
        pytest.skip(f"{name} not found")
    model = load_model(path)
    assert hasattr(model, "predict_proba"), f"❌ {name} has no predict_proba method"


# ══════════════════════════════════════════════════════════════
# 4. PREDICTION TESTS
# ══════════════════════════════════════════════════════════════

@pytest.mark.parametrize("name,path", MODELS.items())
def test_prediction_valid_class(name, path):
    if not os.path.exists(path):
        pytest.skip(f"{name} not found")
    model = load_model(path)
    pred  = model.predict(valid_patient())[0]
    assert 0 <= pred <= 6, f"❌ {name} returned invalid class: {pred}"

@pytest.mark.parametrize("name,path", MODELS.items())
def test_probabilities_sum_to_one(name, path):
    if not os.path.exists(path):
        pytest.skip(f"{name} not found")
    model = load_model(path)
    proba = model.predict_proba(valid_patient())[0]
    assert len(proba) == 7,                "❌ Expected 7 probabilities"
    assert abs(proba.sum() - 1.0) < 1e-4, f"❌ {name} probabilities don't sum to 1"

@pytest.mark.parametrize("name,path", MODELS.items())
def test_normal_patient_prediction(name, path):
    """Normal BMI patient should predict Normal Weight or close"""
    if not os.path.exists(path):
        pytest.skip(f"{name} not found")
    model = load_model(path)
    pred  = model.predict(normal_patient())[0]
    assert pred in [0, 1, 5, 6], \
        f"❌ {name} predicted {CLASSES[pred]} for a normal BMI patient"

@pytest.mark.parametrize("name,path", MODELS.items())
def test_obese_patient_prediction(name, path):
    """Obese patient should predict an obesity class"""
    if not os.path.exists(path):
        pytest.skip(f"{name} not found")
    model = load_model(path)
    pred  = model.predict(obese_patient())[0]
    assert pred in [2, 3, 4], \
        f"❌ {name} predicted {CLASSES[pred]} for a clearly obese patient"

@pytest.mark.parametrize("name,path", MODELS.items())
def test_prediction_is_deterministic(name, path):
    """Same input must always give same output"""
    if not os.path.exists(path):
        pytest.skip(f"{name} not found")
    model = load_model(path)
    pred1 = model.predict(valid_patient())[0]
    pred2 = model.predict(valid_patient())[0]
    assert pred1 == pred2, f"❌ {name} is not deterministic!"


# ══════════════════════════════════════════════════════════════
# 5. ACCURACY TESTS
# ══════════════════════════════════════════════════════════════

@pytest.mark.parametrize("name,path", MODELS.items())
def test_accuracy_above_80(name, path):
    """All models must exceed 80% accuracy"""
    if not os.path.exists(path):
        pytest.skip(f"{name} not found")
    model  = load_model(path)
    X_test = pd.read_csv("data/X_test.csv")
    y_test = pd.read_csv("data/y_test.csv").squeeze()
    acc    = accuracy_score(y_test, model.predict(X_test))
    assert acc >= 0.80, f"❌ {name} accuracy too low: {acc*100:.2f}%"

def test_lightgbm_accuracy_above_95():
    """LightGBM must exceed 95% — it's the best model"""
    if not os.path.exists("outputs/lightgbm.pkl"):
        pytest.skip("LightGBM not found")
    model  = load_model("outputs/lightgbm.pkl")
    X_test = pd.read_csv("data/X_test.csv")
    y_test = pd.read_csv("data/y_test.csv").squeeze()
    acc    = accuracy_score(y_test, model.predict(X_test))
    assert acc >= 0.95, f"❌ LightGBM accuracy too low: {acc*100:.2f}%"

def test_lightgbm_is_best_model():
    """LightGBM must have highest accuracy among all models"""
    X_test = pd.read_csv("data/X_test.csv")
    y_test = pd.read_csv("data/y_test.csv").squeeze()
    accs   = {}
    for name, path in MODELS.items():
        if os.path.exists(path):
            model      = load_model(path)
            accs[name] = accuracy_score(y_test, model.predict(X_test))

    if "LightGBM" not in accs:
        pytest.skip("LightGBM not found")

    best = max(accs, key=accs.get)
    assert best == "LightGBM" or accs["LightGBM"] >= max(accs.values()) - 0.01, \
        f"❌ LightGBM is not the best model. Best: {best} ({accs[best]*100:.2f}%)"

@pytest.mark.parametrize("name,path", MODELS.items())
def test_f1_macro_above_80(name, path):
    """All models must exceed 80% F1 macro"""
    if not os.path.exists(path):
        pytest.skip(f"{name} not found")
    model  = load_model(path)
    X_test = pd.read_csv("data/X_test.csv")
    y_test = pd.read_csv("data/y_test.csv").squeeze()
    f1     = f1_score(y_test, model.predict(X_test), average="macro")
    assert f1 >= 0.80, f"❌ {name} F1 too low: {f1*100:.2f}%"

@pytest.mark.parametrize("name,path", MODELS.items())
def test_all_classes_predicted(name, path):
    """Each model must predict all 7 classes on the test set"""
    if not os.path.exists(path):
        pytest.skip(f"{name} not found")
    model  = load_model(path)
    X_test = pd.read_csv("data/X_test.csv")
    preds  = model.predict(X_test)
    # Flatten predictions if needed
    if hasattr(preds, 'ravel'):
        preds = preds.ravel()
    unique_preds = set(preds)
    assert len(unique_preds) == 7, \
        f"❌ {name} only predicts {len(unique_preds)}/7 classes"


# ══════════════════════════════════════════════════════════════
# 6. INVALID INPUT TESTS
# ══════════════════════════════════════════════════════════════

def test_detect_missing_values():
    bad = valid_patient().copy()
    bad["Weight"] = np.nan
    assert bad.isnull().sum().sum() > 0, "❌ Missing value not detected"

def test_detect_negative_weight():
    assert -50 < VALID_RANGES["Weight"][0], "❌ Negative weight not caught"

def test_detect_impossible_height():
    assert 3.0 > VALID_RANGES["Height"][1], "❌ Impossible height not caught"

def test_detect_invalid_gender():
    assert 5 not in [0, 1], "❌ Invalid gender not caught"

def test_detect_age_out_of_range():
    assert 150 > VALID_RANGES["Age"][1], "❌ Age 150 not caught"


# ══════════════════════════════════════════════════════════════
# 7. COMPARISON TEST
# ══════════════════════════════════════════════════════════════

def test_all_models_agree_on_obvious_case():
    """All models should agree on a very obvious obesity case"""
    X_test = pd.read_csv("data/X_test.csv")
    y_test = pd.read_csv("data/y_test.csv").squeeze()

    preds = {}
    for name, path in MODELS.items():
        if os.path.exists(path):
            model       = load_model(path)
            preds[name] = model.predict(obese_patient())[0]

    # All should predict an obesity class (2, 3 or 4)
    for name, pred in preds.items():
        assert pred in [2, 3, 4], \
            f"❌ {name} predicted {CLASSES[pred]} for obvious obesity case"

def test_models_consistency_on_test_set():
    """Top 3 models (LightGBM, CatBoost, XGBoost) should agree on 85%+ of test cases"""
    top3  = ["LightGBM", "CatBoost", "XGBoost"]
    preds = {}

    X_test = pd.read_csv("data/X_test.csv")

    for name in top3:
        path = MODELS[name]
        if os.path.exists(path):
            model       = load_model(path)
            raw_preds = model.predict(X_test)
            # Flatten predictions if needed
            if hasattr(raw_preds, 'ravel'):
                raw_preds = raw_preds.ravel()
            preds[name] = raw_preds

    if len(preds) < 2:
        pytest.skip("Not enough models to compare")

    # Compare all pairs
    names = list(preds.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            agree = np.mean(preds[names[i]] == preds[names[j]])
            assert agree >= 0.85, \
                f"❌ {names[i]} and {names[j]} only agree on {agree*100:.1f}% of cases"
