import streamlit as st
import pandas as pd
import numpy as np
import joblib
import shap
import matplotlib
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime

matplotlib.use("Agg")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediObes · Résultat",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auth guard ─────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in") or st.session_state.get("role") != "doctor":
    st.markdown("""<style>
        [data-testid="stSidebar"],[data-testid="collapsedControl"],
        header[data-testid="stHeader"]{ display:none !important; }
    </style>""", unsafe_allow_html=True)
    st.switch_page("pages/doctor/login.py")

if "patient_data" not in st.session_state or "patient_info" not in st.session_state:
    st.warning("Aucune donnée patient. Veuillez remplir le formulaire.")
    st.switch_page("pages/doctor/data_entry.py")

# ── Constants ──────────────────────────────────────────────────────────────────
MODEL_PATH   = "models/model.pkl"
RECORDS_DIR  = "data/records"

OBESITY_LABELS = {
    0: "Insufficient_Weight", 1: "Normal_Weight",
    2: "Obesity_Type_I",      3: "Obesity_Type_II",
    4: "Obesity_Type_III",    5: "Overweight_Level_I",
    6: "Overweight_Level_II",
}
LABEL_FR = {
    "Insufficient_Weight":  "Poids Insuffisant",
    "Normal_Weight":        "Poids Normal",
    "Overweight_Level_I":   "Surpoids — Niveau I",
    "Overweight_Level_II":  "Surpoids — Niveau II",
    "Obesity_Type_I":       "Obésité — Type I",
    "Obesity_Type_II":      "Obésité — Type II",
    "Obesity_Type_III":     "Obésité — Type III (Morbide)",
}
LABEL_COLOR = {
    "Insufficient_Weight":  ("#2196F3", "rgba(33,150,243,0.12)"),
    "Normal_Weight":        ("#52B788", "rgba(82,183,136,0.12)"),
    "Overweight_Level_I":   ("#F4A261", "rgba(244,162,97,0.12)"),
    "Overweight_Level_II":  ("#E76F51", "rgba(231,111,81,0.12)"),
    "Obesity_Type_I":       ("#E05252", "rgba(224,82,82,0.12)"),
    "Obesity_Type_II":      ("#C62828", "rgba(198,40,40,0.12)"),
    "Obesity_Type_III":     ("#B71C1C", "rgba(183,28,28,0.12)"),
}
LABEL_ADVICE = {
    "Insufficient_Weight":  "Ce patient présente un poids insuffisant. Un suivi nutritionnel est recommandé.",
    "Normal_Weight":        "Le patient présente un poids normal. Maintenir les habitudes actuelles.",
    "Overweight_Level_I":   "Surpoids modéré. Une amélioration de l'activité physique est conseillée.",
    "Overweight_Level_II":  "Surpoids important. Un plan nutritionnel personnalisé est recommandé.",
    "Obesity_Type_I":       "Obésité de type I. Prise en charge médicale et diététique nécessaire.",
    "Obesity_Type_II":      "Obésité de type II. Consultation spécialisée urgente recommandée.",
    "Obesity_Type_III":     "Obésité morbide. Prise en charge pluridisciplinaire immédiate requise.",
}
FEATURE_LABELS_FR = {
    "Gender": "Sexe", "Age": "Âge", "Height": "Taille (m)", "Weight": "Poids (kg)",
    "family_history_with_overweight": "Antécédents familiaux", "FAVC": "Aliments caloriques",
    "FCVC": "Légumes/repas", "NCP": "Repas/jour", "CAEC": "Grignotage",
    "SMOKE": "Tabagisme", "CH2O": "Eau/jour", "SCC": "Surveillance calories",
    "FAF": "Activité physique", "TUE": "Temps écran", "CALC": "Alcool", "MTRANS": "Transport",
}

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'DM Sans', sans-serif; background: #0B1628;
}
[data-testid="stAppViewContainer"]::before {
    content: ''; position: fixed; inset: 0;
    background:
        radial-gradient(ellipse at 10% 30%, rgba(29,105,150,0.15) 0%, transparent 55%),
        radial-gradient(ellipse at 90% 70%, rgba(29,105,150,0.08) 0%, transparent 50%);
    pointer-events: none; z-index: 0;
}
[data-testid="stMain"] { position: relative; z-index: 1; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: #0D1E30 !important; border-right: 1px solid rgba(29,105,150,0.15) !important; }
[data-testid="stSidebar"] * { color: #4A7A9A !important; }
[data-testid="stSidebar"] hr { border-color: rgba(29,105,150,0.15) !important; margin: 14px 0; }
.sb-logo { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 600; color: #FFFFFF !important; letter-spacing: -0.3px; margin-bottom: 2px; }
.sb-logo span { color: transparent; background: linear-gradient(135deg,#52B788,#7EC8E3); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.sb-tagline { font-size: 11px; color: #1D3A50 !important; margin-bottom: 20px; }
.sb-user { background: rgba(29,105,150,0.12); border: 1px solid rgba(29,105,150,0.20); border-radius: 12px; padding: 12px 14px; margin-bottom: 4px; }
.sb-user-name { font-size: 13.5px; font-weight: 500; color: #FFFFFF !important; }
.sb-user-role { font-size: 11px; color: #52B788 !important; margin-top: 2px; }
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: rgba(29,105,150,0.12) !important; color: #4A7A9A !important;
    border: 1px solid rgba(29,105,150,0.20) !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 13px !important;
    box-shadow: none !important; transition: background 0.2s !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: rgba(29,105,150,0.22) !important; color: #7EC8E3 !important; transform: none !important;
}

/* ── Page header ── */
.page-header { margin-bottom: 28px; }
.page-eyebrow { font-size: 11px; font-weight: 500; letter-spacing: 1.5px; text-transform: uppercase; color: #1D4A6A; margin-bottom: 6px; }
.page-title { font-family: 'Playfair Display', serif; font-size: 34px; font-weight: 600; color: #FFFFFF; letter-spacing: -0.8px; margin-bottom: 4px; }
.page-sub { font-size: 14px; color: #1D3A50; font-weight: 300; }

/* ── Result card ── */
.result-card {
    border-radius: 18px; padding: 32px 36px; margin-bottom: 20px;
    position: relative; overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08);
}
.result-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: var(--accent-color);
}
.result-label-small {
    font-size: 10.5px; font-weight: 500; text-transform: uppercase;
    letter-spacing: 1.2px; margin-bottom: 8px; opacity: 0.6;
}
.result-label-main {
    font-family: 'Playfair Display', serif;
    font-size: 30px; font-weight: 600; line-height: 1.2; margin-bottom: 10px;
}
.result-advice { font-size: 13.5px; line-height: 1.7; max-width: 520px; opacity: 0.8; }

/* ── Proba bars ── */
.proba-row { display: flex; align-items: center; gap: 10px; margin-bottom: 9px; font-size: 12.5px; }
.proba-label { width: 190px; color: #4A7A9A; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.proba-bar-bg { flex: 1; background: rgba(255,255,255,0.06); border-radius: 6px; height: 8px; }
.proba-bar-fill { height: 8px; border-radius: 6px; transition: width 0.6s ease; }
.proba-value { width: 42px; text-align: right; font-weight: 500; color: #7EC8E3; font-size: 11.5px; }

/* ── Section card ── */
.section-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 28px 32px; margin-bottom: 20px;
    position: relative; overflow: hidden;
}
.section-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(to right, #1D6996, #7EC8E3);
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 17px; color: #7EC8E3; margin-bottom: 20px;
    display: flex; align-items: center; gap: 8px;
}
.section-title::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(to right, rgba(29,105,150,0.3), transparent); margin-left: 8px;
}

/* ── Patient chips ── */
.patient-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(29,105,150,0.12); border: 1px solid rgba(29,105,150,0.25);
    border-radius: 20px; padding: 5px 14px;
    font-size: 12.5px; color: #7EC8E3; margin-right: 8px; margin-bottom: 8px;
}

/* ── Save button ── */
.save-btn [data-testid="stButton"] > button {
    background: linear-gradient(135deg, #52B788, #3d9e70) !important;
    color: #FFFFFF !important; border: none !important;
    border-radius: 10px !important; padding: 13px 0 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 14.5px !important;
    font-weight: 500 !important; box-shadow: 0 4px 16px rgba(82,183,136,0.30) !important;
    transition: transform 0.15s, box-shadow 0.15s;
}
.save-btn [data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important; box-shadow: 0 8px 24px rgba(82,183,136,0.40) !important;
}

/* ── Reco button ── */
.reco-btn [data-testid="stButton"] > button {
    background: linear-gradient(135deg, #1D6996, #155a7a) !important;
    color: #FFFFFF !important; border: none !important;
    border-radius: 10px !important; padding: 13px 0 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 14.5px !important;
    font-weight: 500 !important; box-shadow: 0 4px 16px rgba(29,105,150,0.30) !important;
}
.reco-btn [data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important; box-shadow: 0 8px 24px rgba(29,105,150,0.40) !important;
}

/* ── New patient button ── */
.new-btn [data-testid="stButton"] > button {
    background: transparent !important; color: #4A7A9A !important;
    border: 1px solid rgba(29,105,150,0.30) !important;
    border-radius: 10px !important; padding: 12px 0 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 14px !important;
    box-shadow: none !important;
}
.new-btn [data-testid="stButton"] > button:hover {
    background: rgba(29,105,150,0.10) !important; color: #7EC8E3 !important; transform: none !important;
}

/* ── SHAP plot background ── */
[data-testid="stImage"] { border-radius: 12px; overflow: hidden; }
[data-testid="stCaptionContainer"] p { color: #1D3A50 !important; font-size: 11.5px !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">Medi<span>Obes</span></div>
    <div class="sb-tagline">Espace Médecin</div>
    <hr>
    """, unsafe_allow_html=True)
    name = st.session_state.get("display_name", "Médecin")
    st.markdown(f"""
    <div class="sb-user">
        <div class="sb-user-name">🩺 {name}</div>
        <div class="sb-user-role">● Médecin connecté</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.page_link("pages/doctor/dashboard.py",  label="🏠  Tableau de bord")
    st.page_link("pages/doctor/data_entry.py", label="➕  Nouveau patient")
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("🚪  Se déconnecter", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/home.py")

# ── Load model ─────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)

model = load_model()

# ── Patient data ───────────────────────────────────────────────────────────────
patient_info = st.session_state["patient_info"]
patient_data = st.session_state["patient_data"]
patient_id   = st.session_state.get("selected_patient_id", "unknown")
df_input     = pd.DataFrame([patient_data])
prenom       = patient_info["prenom"]
nom          = patient_info["nom"]
bmi_val      = patient_data["Weight"] / (patient_data["Height"] ** 2)

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
    <div class="page-eyebrow">Espace Médecin · Analyse</div>
    <div class="page-title">Résultat de l'estimation</div>
    <div class="page-sub">
        Patient : <strong style="color:#7EC8E3">{prenom} {nom}</strong>
        &nbsp;·&nbsp; {datetime.now().strftime("%d/%m/%Y à %H:%M")}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Model check ────────────────────────────────────────────────────────────────
if model is None:
    st.error("⚠️ Modèle introuvable — vérifiez que `models/model.pkl` existe.")
    st.info("Lancez `python src/train_model.py` pour générer le modèle.")
    st.stop()

# ── Prediction ─────────────────────────────────────────────────────────────────
prediction_enc = model.predict(df_input)[0]
probas         = model.predict_proba(df_input)[0]
classes        = model.classes_

pred_label = OBESITY_LABELS.get(int(prediction_enc), str(prediction_enc)) \
             if isinstance(prediction_enc, (int, np.integer)) else str(prediction_enc)

pred_label_fr = LABEL_FR.get(pred_label, pred_label)
accent, bg    = LABEL_COLOR.get(pred_label, ("#1D6996", "rgba(29,105,150,0.12)"))
advice        = LABEL_ADVICE.get(pred_label, "")

st.session_state["prediction"] = pred_label

# ══════════════════════════════════════════════════════════════════════════════
# BLOC 1 — Résultat + Probabilités
# ══════════════════════════════════════════════════════════════════════════════
col_res, col_proba = st.columns([1.1, 1])

with col_res:
    st.markdown(f"""
    <div class="result-card" style="background:{bg}; --accent-color:{accent};">
        <div class="result-label-small" style="color:{accent};">Niveau d'obésité estimé</div>
        <div class="result-label-main" style="color:{accent};">{pred_label_fr}</div>
        <div class="result-advice" style="color:#8AAABB;">{advice}</div>
        <div style="margin-top:20px; display:flex; gap:20px;">
            <div style="text-align:center;">
                <div style="font-family:'Playfair Display',serif; font-size:26px; color:#FFFFFF; font-weight:600;">{bmi_val:.1f}</div>
                <div style="font-size:11px; color:#2A5A7A; text-transform:uppercase; letter-spacing:0.8px;">IMC</div>
            </div>
            <div style="text-align:center;">
                <div style="font-family:'Playfair Display',serif; font-size:26px; color:#FFFFFF; font-weight:600;">{patient_data['Weight']:.0f}</div>
                <div style="font-size:11px; color:#2A5A7A; text-transform:uppercase; letter-spacing:0.8px;">kg</div>
            </div>
            <div style="text-align:center;">
                <div style="font-family:'Playfair Display',serif; font-size:26px; color:#FFFFFF; font-weight:600;">{int(patient_data['Age'])}</div>
                <div style="font-size:11px; color:#2A5A7A; text-transform:uppercase; letter-spacing:0.8px;">ans</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_proba:
    st.markdown('<div class="section-card" style="padding:24px 28px;">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 &nbsp;Probabilités</div>', unsafe_allow_html=True)
    sorted_idx = np.argsort(probas)[::-1]
    for i in sorted_idx:
        cls_raw    = classes[i]
        cls_str    = OBESITY_LABELS.get(int(cls_raw), str(cls_raw)) \
                     if isinstance(cls_raw, (int, np.integer)) else str(cls_raw)
        cls_fr     = LABEL_FR.get(cls_str, cls_str)
        pct        = probas[i] * 100
        c, _       = LABEL_COLOR.get(cls_str, ("#1D6996", ""))
        is_pred    = cls_str == pred_label
        fw         = "600" if is_pred else "400"
        label_color = "#FFFFFF" if is_pred else "#4A7A9A"
        st.markdown(f"""
        <div class="proba-row">
            <div class="proba-label" style="font-weight:{fw}; color:{label_color};">{cls_fr}</div>
            <div class="proba-bar-bg">
                <div class="proba-bar-fill" style="width:{pct:.1f}%; background:{c};"></div>
            </div>
            <div class="proba-value">{pct:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# BLOC 2 — SHAP
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🔍 &nbsp;Explication SHAP — Facteurs influençant la prédiction</div>', unsafe_allow_html=True)

try:
    explainer   = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(df_input)

    if isinstance(shap_values, list):
        class_list = list(classes)
        try:    pred_idx = class_list.index(prediction_enc)
        except: pred_idx = 0
        shap_vals_pred = shap_values[pred_idx][0]
    else:
        shap_vals_pred = shap_values[0]

    feature_names_fr = [FEATURE_LABELS_FR.get(f, f) for f in df_input.columns]
    sorted_shap_idx  = np.argsort(np.abs(shap_vals_pred))[::-1][:10]
    vals   = shap_vals_pred[sorted_shap_idx]
    labels = [feature_names_fr[i] for i in sorted_shap_idx]
    colors = [accent if v > 0 else "#2A4A5A" for v in vals]

    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor("#0D1E30")
    ax.set_facecolor("#0D1E30")

    ax.barh(labels[::-1], vals[::-1], color=colors[::-1], height=0.55, edgecolor="none")

    for idx, (bar, val) in enumerate(zip(ax.patches, vals[::-1])):
        max_abs = max(abs(vals)) if max(abs(vals)) > 0 else 1
        x_pos = val + max_abs * 0.02 if val >= 0 else val - max_abs * 0.02
        ha    = "left" if val >= 0 else "right"
        ax.text(x_pos, bar.get_y() + bar.get_height() / 2,
                f"{val:+.3f}", va="center", ha=ha, fontsize=9, color="#7EC8E3")

    ax.axvline(0, color="rgba(29,105,150,0.4)", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Valeur SHAP", fontsize=10, color="#4A7A9A")
    ax.set_title(f"Top 10 features · {pred_label_fr}", fontsize=11,
                 color="#FFFFFF", pad=14, fontweight="600")
    ax.tick_params(axis="y", labelsize=9,  colors="#7EC8E3")
    ax.tick_params(axis="x", labelsize=8,  colors="#2A5A7A")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("rgba(29,105,150,0.3)")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    with st.expander("📈 Summary plot global"):
        fig2, _ = plt.subplots(figsize=(9, 5))
        fig2.patch.set_facecolor("#0D1E30")
        shap.summary_plot(
            shap_values if isinstance(shap_values, np.ndarray) else shap_values[pred_idx],
            df_input, feature_names=feature_names_fr, show=False, plot_size=None,
        )
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

except Exception as e:
    st.warning(f"Impossible de générer les explications SHAP : {e}")

st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# BLOC 3 — Sauvegarde
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">💾 &nbsp;Enregistrer le dossier</div>', unsafe_allow_html=True)

st.markdown(f"""
<div style="margin-bottom:20px;">
    <span class="patient-chip">👤 {prenom} {nom}</span>
    <span class="patient-chip">🆔 {patient_id}</span>
    <span class="patient-chip">📏 IMC {bmi_val:.1f}</span>
    <span class="patient-chip" style="color:{accent}; border-color:{accent};">🎯 {pred_label_fr}</span>
</div>
""", unsafe_allow_html=True)

col_save, col_reco, col_new, _ = st.columns([1.5, 1.8, 1.5, 2])

with col_save:
    st.markdown('<div class="save-btn">', unsafe_allow_html=True)
    save_btn = st.button("💾  Enregistrer", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_reco:
    st.markdown('<div class="reco-btn">', unsafe_allow_html=True)
    reco_btn = st.button("✍️  Rédiger les recommandations", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_new:
    st.markdown('<div class="new-btn">', unsafe_allow_html=True)
    new_btn = st.button("➕  Nouveau patient", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Save logic ─────────────────────────────────────────────────────────────────
def save_record():
    os.makedirs(RECORDS_DIR, exist_ok=True)
    path = os.path.join(RECORDS_DIR, f"{patient_id}.json")

    # Charger l'existant pour ne pas écraser les recommandations
    existing = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            existing = json.load(f)

    record = {
        **existing,
        "patient_id":   patient_id,
        "patient_name": f"{prenom} {nom}",
        "date_analyse": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "doctor":       st.session_state.get("display_name", "Inconnu"),
        "prediction":   pred_label,
        "BMI":          round(bmi_val, 2),
        "clinical_data": patient_data,
    }

    with open(path, "w") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

if save_btn:
    if st.session_state.get("patient_saved"):
        st.info("Ce dossier a déjà été enregistré dans cette session.")
    else:
        try:
            save_record()
            st.session_state["patient_saved"] = True
            st.success(f"✅ Dossier de {prenom} {nom} enregistré avec succès.")
        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde : {e}")

if reco_btn:
    if not st.session_state.get("patient_saved"):
        try:
            save_record()
            st.session_state["patient_saved"] = True
        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde : {e}")
            st.stop()
    st.switch_page("pages/doctor/recommendations.py")

if new_btn:
    for key in ["patient_data", "patient_info", "prediction", "patient_saved", "selected_patient_id"]:
        st.session_state.pop(key, None)
    st.switch_page("pages/doctor/data_entry.py")