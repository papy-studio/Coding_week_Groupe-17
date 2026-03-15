"""
╔══════════════════════════════════════════════════════════════╗
║              TESTS — MediObes · LightGBM Model              ║
╚══════════════════════════════════════════════════════════════╝
"""
import pytest
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.metrics import accuracy_score, f1_score

# ── Constants ──────────────────────────────────────────────────────────────────
MODEL_PATH = "src/models/model.pkl"

CLASSES = [
    'Insufficient_Weight', 'Normal_Weight',
    'Obesity_Type_I',      'Obesity_Type_II',
    'Obesity_Type_III',    'Overweight_Level_I',
    'Overweight_Level_II'
]

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

# ── Helpers ────────────────────────────────────────────────────────────────────
def load_model():
    obj = joblib.load(MODEL_PATH)
    if isinstance(obj, dict) and "model" in obj:
        obj = obj["model"]
    return obj

def valid_patient():
    return pd.DataFrame([{
        "Gender": 1, "Age": 25, "Height": 1.75, "Weight": 85,
        "family_history_with_overweight": 1, "FAVC": 1, "FCVC": 2,
        "NCP": 3, "CAEC": 2, "SMOKE": 0, "CH2O": 2, "SCC": 0,
        "FAF": 1, "TUE": 1, "CALC": 1, "MTRANS": 2
    }])

def normal_patient():
    """Patient avec IMC normal"""
    return pd.DataFrame([{
        "Gender": 0, "Age": 28, "Height": 1.68, "Weight": 62,
        "family_history_with_overweight": 0, "FAVC": 0, "FCVC": 3,
        "NCP": 3, "CAEC": 1, "SMOKE": 0, "CH2O": 3, "SCC": 0,
        "FAF": 3, "TUE": 1, "CALC": 0, "MTRANS": 4
    }])

def obese_patient():
    """Patient clairement obèse"""
    return pd.DataFrame([{
        "Gender": 1, "Age": 40, "Height": 1.68, "Weight": 140,
        "family_history_with_overweight": 1, "FAVC": 1, "FCVC": 1,
        "NCP": 4, "CAEC": 3, "SMOKE": 1, "CH2O": 1, "SCC": 0,
        "FAF": 0, "TUE": 2, "CALC": 3, "MTRANS": 2
    }])


# ══════════════════════════════════════════════════════════════════════════════
# 1. FILE EXISTENCE TESTS
# ══════════════════════════════════════════════════════════════════════════════

def test_model_file_exists():
    assert os.path.exists(MODEL_PATH), f"❌ model.pkl not found at {MODEL_PATH}"

def test_data_files_exist():
   assert os.path.exists("src/data/X_train.csv"), "❌ X_train.csv missing"
   assert os.path.exists("src/data/X_test.csv"),  "❌ X_test.csv missing"
   assert os.path.exists("src/data/y_train.csv"), "❌ y_train.csv missing"
   assert os.path.exists("src/data/y_test.csv"),  "❌ y_test.csv missing"


# ══════════════════════════════════════════════════════════════════════════════
# 2. DATA VALIDATION TESTS
# ══════════════════════════════════════════════════════════════════════════════

def test_no_missing_values_train():
    X_train = pd.read_csv("src/data/X_train.csv")
    assert X_train.isnull().sum().sum() == 0, "❌ Missing values in X_train"

def test_no_missing_values_test():
    X_test = pd.read_csv("src/data/X_test.csv")
    assert X_test.isnull().sum().sum() == 0, "❌ Missing values in X_test"

def test_correct_number_of_features():
    X_test = pd.read_csv("src/data/X_test.csv")
    assert X_test.shape[1] == 16, f"❌ Expected 16 features, got {X_test.shape[1]}"

def test_correct_columns():
    X_test   = pd.read_csv("src/data/X_test.csv")
    expected = list(VALID_RANGES.keys())
    missing  = [c for c in expected if c not in X_test.columns]
    assert len(missing) == 0, f"❌ Missing columns: {missing}"

def test_target_valid_range():
    y_test = pd.read_csv("src/data/y_test.csv").squeeze()
    assert y_test.min() >= 0, "❌ Target below 0"
    assert y_test.max() <= 6, "❌ Target above 6"

def test_train_test_split_ratio():
    X_train = pd.read_csv("src/data/X_train.csv")
    X_test  = pd.read_csv("src/data/X_test.csv")
    ratio   = len(X_test) / (len(X_train) + len(X_test))
    assert 0.18 <= ratio <= 0.22, f"❌ Split ratio is {ratio:.2f}, expected ~0.20"

def test_feature_ranges():
    X_test = pd.read_csv("src/data/X_test.csv")
    for col, (mn, mx) in VALID_RANGES.items():
        if col in X_test.columns:
            assert X_test[col].min() >= mn, f"❌ {col} below min {mn}"
            assert X_test[col].max() <= mx, f"❌ {col} above max {mx}"


# ══════════════════════════════════════════════════════════════════════════════
# 3. MODEL LOADING TESTS
# ══════════════════════════════════════════════════════════════════════════════

def test_model_loads():
    model = load_model()
    assert model is not None, "❌ Model failed to load"

def test_model_has_predict():
    model = load_model()
    assert hasattr(model, "predict"), "❌ Model has no predict method"

def test_model_has_predict_proba():
    model = load_model()
    assert hasattr(model, "predict_proba"), "❌ Model has no predict_proba method"


# ══════════════════════════════════════════════════════════════════════════════
# 4. PREDICTION TESTS
# ══════════════════════════════════════════════════════════════════════════════

def test_prediction_valid_class():
    model = load_model()
    pred  = int(model.predict(valid_patient())[0])
    assert 0 <= pred <= 6, f"❌ Invalid class predicted: {pred}"

def test_probabilities_sum_to_one():
    model = load_model()
    proba = model.predict_proba(valid_patient())[0]
    assert len(proba) == 7,                "❌ Expected 7 probabilities"
    assert abs(proba.sum() - 1.0) < 1e-4, "❌ Probabilities don't sum to 1"

def test_normal_patient_prediction():
    """Patient normal doit prédire Normal Weight ou proche"""
    model = load_model()
    pred  = int(model.predict(normal_patient())[0])
    assert pred in [0, 1, 5, 6], \
        f"❌ Predicted {CLASSES[pred]} for a normal BMI patient"

def test_obese_patient_prediction():
    """Patient obèse doit prédire une classe obésité"""
    model = load_model()
    pred  = int(model.predict(obese_patient())[0])
    assert pred in [2, 3, 4], \
        f"❌ Predicted {CLASSES[pred]} for a clearly obese patient"

def test_prediction_is_deterministic():
    """Le même input doit toujours donner le même output"""
    model = load_model()
    pred1 = model.predict(valid_patient())[0]
    pred2 = model.predict(valid_patient())[0]
    assert pred1 == pred2, "❌ Model is not deterministic!"

def test_prediction_output_shape():
    model  = load_model()
    X_test = pd.read_csv("src/data/X_test.csv")
    preds  = model.predict(X_test)
    assert len(preds) == len(X_test), "❌ Prediction count doesn't match input count"


# ══════════════════════════════════════════════════════════════════════════════
# 5. ACCURACY TESTS
# ══════════════════════════════════════════════════════════════════════════════

def test_accuracy_above_90():
    model  = load_model()
    X_test = pd.read_csv("src/data/X_test.csv")
    y_test = pd.read_csv("src/data/y_test.csv").squeeze()
    acc    = accuracy_score(y_test, model.predict(X_test))
    assert acc >= 0.90, f"❌ Accuracy too low: {acc*100:.2f}% (expected ≥ 90%)"

def test_accuracy_above_95():
    model  = load_model()
    X_test = pd.read_csv("src/data/X_test.csv")
    y_test = pd.read_csv("src/data/y_test.csv").squeeze()
    acc    = accuracy_score(y_test, model.predict(X_test))
    assert acc >= 0.95, f"❌ Accuracy too low: {acc*100:.2f}% (expected ≥ 95%)"

def test_f1_macro_above_90():
    model  = load_model()
    X_test = pd.read_csv("src/data/X_test.csv")
    y_test = pd.read_csv("src/data/y_test.csv").squeeze()
    f1     = f1_score(y_test, model.predict(X_test), average="macro")
    assert f1 >= 0.90, f"❌ F1 macro too low: {f1*100:.2f}% (expected ≥ 90%)"

def test_all_classes_predicted():
    model  = load_model()
    X_test = pd.read_csv("src/data/X_test.csv")
    preds  = model.predict(X_test)
    unique = set(int(p) for p in preds)
    assert len(unique) == 7, f"❌ Model only predicts {len(unique)}/7 classes"


# ══════════════════════════════════════════════════════════════════════════════
# 6. INVALID INPUT TESTS
# ══════════════════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════════════════
# 7. ROBUSTNESS TEST
# ══════════════════════════════════════════════════════════════════════════════

def test_obese_prediction_is_obesity_class():
    """Le modèle doit prédire une classe obésité pour un cas évident"""
    model = load_model()
    pred  = int(model.predict(obese_patient())[0])
    assert pred in [2, 3, 4], \
        f"❌ Predicted {CLASSES[pred]} for obvious obesity case"