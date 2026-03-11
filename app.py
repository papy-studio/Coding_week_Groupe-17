"""
╔══════════════════════════════════════════════════════════════╗
║         OBESITY LEVEL PREDICTOR — Streamlit App             ║
╠══════════════════════════════════════════════════════════════╣
║  Run: streamlit run app.py                                   ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import pickle
import os
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Obesity Level Predictor",
    page_icon="🏥",
    layout="wide"
)

# ── Class names ───────────────────────────────────────────────
CLASSES = [
    'Insufficient Weight', 'Normal Weight',
    'Obesity Type I',      'Obesity Type II',
    'Obesity Type III',    'Overweight Level I',
    'Overweight Level II'
]

CLASS_COLORS = {
    'Insufficient Weight':  '#3B82F6',
    'Normal Weight':        '#10B981',
    'Obesity Type I':       '#F59E0B',
    'Obesity Type II':      '#F97316',
    'Obesity Type III':     '#EF4444',
    'Overweight Level I':   '#8B5CF6',
    'Overweight Level II':  '#EC4899',
}

# ── Load model ────────────────────────────────────────────────
@st.cache_resource
def load_model():
    for path in ["outputs/xgboost.pkl", "outputs/model.pkl", "outputs/best_model_XGBoost.pkl"]:
        if os.path.exists(path):
            try:
                obj = joblib.load(path)
            except Exception:
                with open(path, "rb") as f:
                    obj = pickle.load(f)
            if isinstance(obj, dict) and "model" in obj:
                return obj["model"]
            return obj
    return None

@st.cache_data
def load_test_data():
    if os.path.exists("data/X_test.csv"):
        X_test = pd.read_csv("data/X_test.csv")
        y_test = pd.read_csv("data/y_test.csv").squeeze()
        return X_test, y_test
    return None, None

model        = load_model()
X_test, y_test = load_test_data()

# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
st.title("🏥 Obesity Level Predictor")
st.markdown("**XGBoost model** trained on UCI Obesity dataset (2111 patients)")
st.divider()

if model is None:
    st.error("❌ Model not found! Put xgboost.pkl in the outputs/ folder.")
    st.stop()

# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════
tab1, tab2 = st.tabs(["🔮 Predict", "📊 Model Performance"])

# ══════════════════════════════════════════════════════════════
# TAB 1 — PREDICT
# ══════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Enter Patient Data")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**👤 Personal Info**")
        gender  = st.selectbox("Gender", ["Male", "Female"])
        age     = st.slider("Age", 10, 80, 25)
        height  = st.slider("Height (m)", 1.40, 2.00, 1.75, step=0.01)
        weight  = st.slider("Weight (kg)", 30, 180, 85)

        bmi = weight / (height ** 2)
        st.metric("BMI", f"{bmi:.1f}")

    with col2:
        st.markdown("**🍔 Eating Habits**")
        history = st.selectbox("Family obesity history", ["Yes", "No"])
        favc    = st.selectbox("High calorie food frequently (FAVC)", ["Yes", "No"])
        fcvc    = st.slider("Vegetable freq. (FCVC)", 1, 3, 2)
        ncp     = st.slider("Meals per day (NCP)", 1, 4, 3)
        caec    = st.selectbox("Snacking (CAEC)", ["No", "Sometimes", "Frequently", "Always"])
        ch2o    = st.slider("Water liters/day (CH2O)", 1, 3, 2)
        calc    = st.selectbox("Alcohol (CALC)", ["No", "Sometimes", "Frequently", "Always"])

    with col3:
        st.markdown("**🏃 Lifestyle**")
        smoke   = st.selectbox("Smoker", ["No", "Yes"])
        scc     = st.selectbox("Monitors calories (SCC)", ["No", "Yes"])
        faf     = st.slider("Exercise days/week (FAF)", 0, 3, 1)
        tue     = st.slider("Screen hours/day (TUE)", 0, 2, 1)
        mtrans  = st.selectbox("Transport", ["Bike", "Motorbike", "Car", "Public Transport", "Walking"])

    st.divider()

    # ── Encode inputs ─────────────────────────────────────────
    def encode():
        caec_map  = {"No": 0, "Sometimes": 1, "Frequently": 2, "Always": 3}
        calc_map  = {"No": 0, "Sometimes": 1, "Frequently": 2, "Always": 3}
        trans_map = {"Bike": 0, "Motorbike": 1, "Car": 2, "Public Transport": 3, "Walking": 4}

        return pd.DataFrame([{
            "Gender":                          1 if gender == "Male" else 0,
            "Age":                             age,
            "Height":                          height,
            "Weight":                          weight,
            "family_history_with_overweight":  1 if history == "Yes" else 0,
            "FAVC":                            1 if favc == "Yes" else 0,
            "FCVC":                            fcvc,
            "NCP":                             ncp,
            "CAEC":                            caec_map[caec],
            "SMOKE":                           1 if smoke == "Yes" else 0,
            "CH2O":                            ch2o,
            "SCC":                             1 if scc == "Yes" else 0,
            "FAF":                             faf,
            "TUE":                             tue,
            "CALC":                            calc_map[calc],
            "MTRANS":                          trans_map[mtrans],
        }])

    # ── Predict button ────────────────────────────────────────
    if st.button("🔮 Predict Obesity Level", type="primary", use_container_width=True):
        df_input   = encode()
        pred       = model.predict(df_input)[0]
        proba      = model.predict_proba(df_input)[0]
        label      = CLASSES[pred]
        confidence = proba.max() * 100
        color      = CLASS_COLORS[label]

        st.divider()

        # Result
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"""
            <div style='background:{color}22; border:2px solid {color};
                        border-radius:16px; padding:24px; text-align:center;'>
                <div style='font-size:40px'>🏥</div>
                <div style='font-size:22px; font-weight:800; color:{color}; margin:8px 0'>{label}</div>
                <div style='font-size:16px; color:#666'>Confidence: <b>{confidence:.1f}%</b></div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown("**Probability per class:**")
            for i, (cls, prob) in enumerate(zip(CLASSES, proba)):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.progress(float(prob), text=cls)
                with col_b:
                    st.write(f"{prob*100:.1f}%")

# ══════════════════════════════════════════════════════════════
# TAB 2 — MODEL PERFORMANCE
# ══════════════════════════════════════════════════════════════
with tab2:
    st.subheader("XGBoost — Model Performance on Test Set")

    if X_test is None:
        st.warning("⚠️ data/X_test.csv not found. Run train_model.py first.")
    else:
        y_pred = model.predict(X_test)
        acc    = accuracy_score(y_test, y_pred)

        # ── Metrics ───────────────────────────────────────────
        m1, m2, m3 = st.columns(3)
        report = classification_report(y_test, y_pred, output_dict=True)
        m1.metric("✅ Accuracy",   f"{acc*100:.2f}%")
        m2.metric("📊 F1 Macro",   f"{report['macro avg']['f1-score']*100:.2f}%")
        m3.metric("🎯 Precision",  f"{report['macro avg']['precision']*100:.2f}%")

        st.divider()

        # ── Confusion matrix ──────────────────────────────────
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Confusion Matrix**")
            fig, ax = plt.subplots(figsize=(7, 5))
            cm = confusion_matrix(y_test, y_pred)
            sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                        xticklabels=['Ins','Nor','Ob1','Ob2','Ob3','Ow1','Ow2'],
                        yticklabels=['Ins','Nor','Ob1','Ob2','Ob3','Ow1','Ow2'],
                        linewidths=0.5)
            ax.set_xlabel("Predicted")
            ax.set_ylabel("True")
            st.pyplot(fig)

        with col2:
            st.markdown("**F1 Score per Class**")
            f1_scores = {cls: report[str(i)]["f1-score"]
                         for i, cls in enumerate(CLASSES) if str(i) in report}
            fig2, ax2 = plt.subplots(figsize=(7, 5))
            classes_short = ['Insuf.', 'Normal', 'Ob.I', 'Ob.II', 'Ob.III', 'Ow.I', 'Ow.II']
            ax2.bar(classes_short, f1_scores.values(), color="#4C72B0", edgecolor="white")
            ax2.set_ylim(0, 1.1)
            ax2.set_ylabel("F1 Score")
            ax2.tick_params(axis="x", rotation=15)
            for i, v in enumerate(f1_scores.values()):
                ax2.text(i, v + 0.01, f"{v:.2f}", ha="center", fontsize=10, fontweight="bold")
            st.pyplot(fig2)

        # ── Full report ───────────────────────────────────────
        with st.expander("📋 Full Classification Report"):
            report_df = pd.DataFrame(report).transpose().round(2)
            st.dataframe(report_df, use_container_width=True)
