import streamlit as st
import pandas as pd
import numpy as np
import joblib
import shap
import matplotlib
import matplotlib.pyplot as plt
import json
from pathlib import Path
from datetime import datetime

matplotlib.use("Agg")

st.set_page_config(
    page_title="MediObes · Résultat",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR    = Path(__file__).resolve().parent.parent.parent
RECORDS_DIR = BASE_DIR / "data" / "records"
MODEL_PRIORITY = [
    ("LightGBM", BASE_DIR / "outputs" / "lightgbm.pkl"),
    ("LightGBM", BASE_DIR / "src" / "models" / "model.pkl"),
    ("Model",    BASE_DIR / "models" / "model.pkl"),
]

# ── Auth guard ─────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in") or st.session_state.get("role") != "doctor":
    st.markdown("""<style>
        [data-testid="stSidebar"],[data-testid="collapsedControl"],
        header[data-testid="stHeader"]{ display:none !important; }
    </style>""", unsafe_allow_html=True)
    st.warning("Accès réservé aux médecins connectés.")
    if st.button("🔐 Se connecter"):
        st.switch_page("pages/doctor_login.py")
    st.stop()

if "patient_data" not in st.session_state or "patient_info" not in st.session_state:
    st.warning("Aucune donnée patient. Veuillez remplir le formulaire.")
    if st.button("← Retour à la saisie", key="guard_back"):
        st.switch_page("pages/doctor_data_entry.py")
    st.stop()

_pd = st.session_state.get("patient_data", {})
if "Weight" not in _pd or "Height" not in _pd:
    st.warning("Données patient incomplètes.")
    if st.button("← Retour à la saisie", key="guard_back2"):
        st.switch_page("pages/doctor_data_entry.py")
    st.stop()

CLASSES_ORDER = [
    "Insufficient_Weight", "Normal_Weight",
    "Obesity_Type_I",      "Obesity_Type_II",
    "Obesity_Type_III",    "Overweight_Level_I",
    "Overweight_Level_II",
]
LABEL_FR = {
    "Insufficient_Weight":  "Poids Insuffisant",
    "Normal_Weight":        "Poids Normal",
    "Overweight_Level_I":   "Surpoids - Niveau I",
    "Overweight_Level_II":  "Surpoids - Niveau II",
    "Obesity_Type_I":       "Obésité - Type I",
    "Obesity_Type_II":      "Obésité - Type II",
    "Obesity_Type_III":     "Obésité - Type III (Morbide)",
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
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

section[data-testid="stSidebar"] { display: block !important; background-color: #0d1f35 !important; }
[data-testid="stSidebarNav"], div[data-testid="stSidebarNav"],
.css-1d391kg, .css-1lcbmhc, .css-1wrcr25,
.eczjsme11, .eczjsme12, .eczjsme13 { display: none !important; }

.stApp { background-color: #0B1628; }
h1, h2, h3 { font-family: 'Playfair Display', serif; color: white; }
.sidebar-logo { font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700; color: white; margin-bottom: 4px; }
.sidebar-logo span { color: #52B788; }
.sidebar-role { font-size: 0.72rem; color: rgba(255,255,255,0.35); letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 2rem; font-family: 'DM Sans', sans-serif; }
.user-card { background: rgba(82,183,136,0.08); border: 1px solid rgba(82,183,136,0.2); border-radius: 12px; padding: 12px 16px; margin-bottom: 2rem; }
.user-name { color: white; font-size: 0.92rem; font-weight: 500; font-family: 'DM Sans', sans-serif; }
.user-sub  { color: rgba(255,255,255,0.4); font-size: 0.75rem; margin-top: 2px; font-family: 'DM Sans', sans-serif; }
.nav-section { font-size: 0.68rem; color: rgba(255,255,255,0.25); letter-spacing: 0.12em; text-transform: uppercase; margin: 1.2rem 0 0.5rem 0; font-family: 'DM Sans', sans-serif; }
div[data-testid="stSidebar"] .stButton > button { background: transparent; color: rgba(255,255,255,0.65); border: none; border-radius: 8px; text-align: left; width: 100%; padding: 0.5rem 0.75rem; font-size: 0.88rem; font-family: 'DM Sans', sans-serif; }
div[data-testid="stSidebar"] .stButton > button:hover { background: rgba(255,255,255,0.06); color: white; }
div[data-testid="stSidebar"] [data-testid="stButton"]:last-child > button { color: #E05252 !important; }
div[data-testid="stSidebar"] [data-testid="stButton"]:last-child > button:hover { background: rgba(224,82,82,0.1) !important; }

.page-header { margin-bottom: 28px; }
.page-eyebrow { font-size: 0.72rem; color: #52B788; text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 6px; font-family: 'DM Sans', sans-serif; }
.page-title { font-family: 'Playfair Display', serif; font-size: 2.2rem; font-weight: 600; color: white; margin-bottom: 4px; }
.page-sub { font-family: 'DM Sans', sans-serif; font-size: 0.88rem; color: rgba(255,255,255,0.35); }
.result-card { border-radius: 18px; padding: 32px 36px; margin-bottom: 20px; position: relative; overflow: hidden; border: 1px solid rgba(255,255,255,0.08); }
.result-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--accent-color); }
.result-label-small { font-size: 10.5px; font-weight: 500; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 8px; opacity: 0.6; }
.result-label-main { font-family: 'Playfair Display', serif; font-size: 30px; font-weight: 600; line-height: 1.2; margin-bottom: 10px; }
.result-advice { font-size: 13.5px; line-height: 1.7; max-width: 520px; opacity: 0.8; }
.proba-row { display: flex; align-items: center; gap: 10px; margin-bottom: 9px; font-size: 12.5px; }
.proba-label { width: 190px; color: #4A7A9A; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.proba-bar-bg { flex: 1; background: rgba(255,255,255,0.06); border-radius: 6px; height: 8px; }
.proba-bar-fill { height: 8px; border-radius: 6px; }
.proba-value { width: 42px; text-align: right; font-weight: 500; color: #7EC8E3; font-size: 11.5px; }
.section-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 16px; padding: 28px 32px; margin-bottom: 20px; position: relative; overflow: hidden; }
.section-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(to right, #52B788, #A8E6CF); }
.section-title { font-family: 'Playfair Display', serif; font-size: 1.1rem; color: #52B788; margin-bottom: 18px; display: flex; align-items: center; gap: 8px; }
.section-title::after { content: ''; flex: 1; height: 1px; background: linear-gradient(to right, #52B788, transparent); margin-left: 8px; }
.patient-chip { display: inline-flex; align-items: center; gap: 6px; background: rgba(82,183,136,0.08); border: 1px solid rgba(82,183,136,0.2); border-radius: 20px; padding: 5px 14px; font-size: 12.5px; color: #52B788; margin-right: 8px; margin-bottom: 8px; font-family: 'DM Sans', sans-serif; }
.model-badge { display: inline-flex; align-items: center; gap: 6px; background: rgba(82,183,136,0.10); border: 1px solid rgba(82,183,136,0.25); border-radius: 20px; padding: 5px 14px; font-size: 12px; color: #52B788; margin-bottom: 16px; font-family: 'DM Sans', sans-serif; }
.save-btn [data-testid="stButton"] > button { background: linear-gradient(135deg, #52B788, #3d9e70) !important; color: #FFFFFF !important; border: none !important; border-radius: 10px !important; padding: 13px 0 !important; font-size: 14.5px !important; font-weight: 500 !important; box-shadow: 0 4px 16px rgba(82,183,136,0.30) !important; }
.reco-btn [data-testid="stButton"] > button { background: linear-gradient(135deg, #1D6996, #155a7a) !important; color: #FFFFFF !important; border: none !important; border-radius: 10px !important; padding: 13px 0 !important; font-size: 14.5px !important; font-weight: 500 !important; }
.new-btn [data-testid="stButton"] > button { background: transparent !important; color: rgba(255,255,255,0.65) !important; border: 1px solid rgba(255,255,255,0.15) !important; border-radius: 10px !important; padding: 12px 0 !important; font-size: 14px !important; box-shadow: none !important; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { display: flex !important; visibility: visible !important; background-color: #0B1628; }
header [data-testid="stLogo"], header [data-testid="stStatusWidget"] { display: none !important; }
.block-container { padding-top: 2rem !important; max-width: 1200px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">Medi<span>Obes</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-role">Espace Médecin</div>', unsafe_allow_html=True)
    doctor_name = st.session_state.get("display_name", "Médecin")
    st.markdown(f'<div class="user-card"><div class="user-name">🩺 {doctor_name}</div><div class="user-sub">Médecin traitant</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-section">Navigation</div>', unsafe_allow_html=True)
    if st.button("📋  Tableau de bord",  use_container_width=True, key="nav_dashboard"):       st.switch_page("pages/doctor_dashboard.py")
    if st.button("➕  Nouveau patient",  use_container_width=True, key="nav_new_patient"):     st.switch_page("pages/doctor_data_entry.py")
    if st.button("📊  Résultat",         use_container_width=True, key="nav_result"):          st.switch_page("pages/doctor_result.py")
    if st.button("📝  Recommandations",  use_container_width=True, key="nav_recommendations"): st.switch_page("pages/doctor_recommendations.py")
    st.markdown("---")
    if st.button("🚪  Se déconnecter",   use_container_width=True, key="logout"):
        st.session_state.clear()
        st.switch_page("pages/home.py")

# ── Modèle ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_best_model():
    for model_name, path in MODEL_PRIORITY:
        if path.exists():
            try:
                obj = joblib.load(path)
                if isinstance(obj, dict) and "model" in obj:
                    obj = obj["model"]
                return obj, model_name
            except Exception:
                continue
    return None, None

model, model_name = load_best_model()

patient_info = st.session_state.get("patient_info", {})
patient_data = st.session_state.get("patient_data", {})
patient_id   = st.session_state.get("selected_patient_id", "unknown")
df_input     = pd.DataFrame([patient_data])
prenom       = patient_info.get("prenom", "")
nom          = patient_info.get("nom", "")
bmi_val      = patient_data.get("Weight", 70) / (patient_data.get("Height", 1.70) ** 2)

st.markdown(f"""
<div class="page-header">
    <div class="page-eyebrow">Espace Médecin · Analyse</div>
    <div class="page-title">Résultat de l'estimation</div>
    <div class="page-sub">Patient : <strong style="color:#7EC8E3">{prenom} {nom}</strong>
        &nbsp;·&nbsp; {datetime.now().strftime("%d/%m/%Y à %H:%M")}</div>
</div>
""", unsafe_allow_html=True)

if model is None:
    st.error("Aucun modèle trouvé dans models/ ou outputs/.")
    st.stop()

# ── Prédiction + SHAP avec spinner ────────────────────────────────────────────
shap_cache_key = f"shap_done_{patient_id}"

if not st.session_state.get(shap_cache_key):
    with st.spinner("⏳ Analyse en cours — calcul de la prédiction et des explications SHAP…"):

        raw_pred = model.predict(df_input)
        probas   = model.predict_proba(df_input)[0]
        raw_val  = np.array(raw_pred).flatten()[0]
        try:    pred_int = int(raw_val)
        except: pred_int = 0

        pred_label    = CLASSES_ORDER[pred_int] if pred_int < len(CLASSES_ORDER) else "Normal_Weight"
        pred_label_fr = LABEL_FR.get(pred_label, pred_label)
        accent, bg    = LABEL_COLOR.get(pred_label, ("#1D6996", "rgba(29,105,150,0.12)"))
        confidence    = float(probas.max()) * 100

        shap_fig = None
        try:
            explainer   = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(df_input)
            class_idx   = int(pred_int)
            if isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
                sv = shap_values[0, :, class_idx]
            elif isinstance(shap_values, list):
                sv = shap_values[class_idx][0]
            else:
                sv = shap_values[0]

            feature_names_fr = [FEATURE_LABELS_FR.get(f, f) for f in df_input.columns]
            sorted_shap_idx  = np.argsort(np.abs(sv))[::-1][:10]
            vals   = sv[sorted_shap_idx]
            labels = [feature_names_fr[i] for i in sorted_shap_idx]
            colors = [accent if v > 0 else "#2A4A5A" for v in vals]

            fig, ax = plt.subplots(figsize=(9, 5))
            fig.patch.set_facecolor("#0D1E30")
            ax.set_facecolor("#0D1E30")
            ax.barh(labels[::-1], vals[::-1], color=colors[::-1], height=0.55, edgecolor="none")
            max_abs = max(abs(vals)) if max(abs(vals)) > 0 else 1
            for bar, val in zip(ax.patches, vals[::-1]):
                x_pos = val + max_abs * 0.02 if val >= 0 else val - max_abs * 0.02
                ha    = "left" if val >= 0 else "right"
                ax.text(x_pos, bar.get_y() + bar.get_height() / 2,
                        f"{val:+.3f}", va="center", ha=ha, fontsize=9, color="#7EC8E3")
            ax.axvline(0, color="#1D6996", linewidth=0.8, linestyle="--", alpha=0.4)
            ax.set_xlabel("Valeur SHAP", fontsize=10, color="#4A7A9A")
            ax.set_title(f"Top 10 features - {pred_label_fr}", fontsize=11, color="#FFFFFF", pad=14, fontweight="600")
            ax.tick_params(axis="y", labelsize=9, colors="#7EC8E3")
            ax.tick_params(axis="x", labelsize=8, colors="#2A5A7A")
            ax.spines[["top", "right", "left"]].set_visible(False)
            ax.spines["bottom"].set_color("#1D6996")
            plt.tight_layout()
            shap_fig = fig
        except Exception:
            shap_fig = None

        st.session_state[shap_cache_key]          = True
        st.session_state["pred_label"]            = pred_label
        st.session_state["pred_label_fr"]         = pred_label_fr
        st.session_state["accent"]                = accent
        st.session_state["bg"]                    = bg
        st.session_state["confidence"]            = confidence
        st.session_state["probas"]                = probas
        st.session_state["shap_fig"]              = shap_fig
        st.session_state["prediction"]            = pred_label
        st.session_state["prediction_label"]      = pred_label
        st.session_state["prediction_confidence"] = confidence
        st.session_state["prediction_bmi"]        = round(bmi_val, 2)

# ── Lecture depuis le cache ────────────────────────────────────────────────────
pred_label    = st.session_state["pred_label"]
pred_label_fr = st.session_state["pred_label_fr"]
accent        = st.session_state["accent"]
bg            = st.session_state["bg"]
confidence    = st.session_state["confidence"]
probas        = st.session_state["probas"]
shap_fig      = st.session_state["shap_fig"]
pred_int      = CLASSES_ORDER.index(pred_label) if pred_label in CLASSES_ORDER else 0
advice        = LABEL_ADVICE.get(pred_label, "")

# ── Résultat ──────────────────────────────────────────────────────────────────
st.markdown(f'<div class="model-badge">🤖 Modèle : {model_name}</div>', unsafe_allow_html=True)

col_res, col_proba = st.columns([1.1, 1])
with col_res:
    st.markdown(f"""
    <div class="result-card" style="background:{bg}; --accent-color:{accent};">
        <div class="result-label-small" style="color:{accent};">Niveau d'obésité estimé</div>
        <div class="result-label-main" style="color:{accent};">{pred_label_fr}</div>
        <div style="margin-bottom:12px;">
            <span style="background:{accent}22; border:1px solid {accent}55; border-radius:20px; padding:4px 14px; font-size:12px; color:{accent};">
                Confiance : {confidence:.1f}%
            </span>
        </div>
        <div class="result-advice" style="color:#8AAABB;">{advice}</div>
        <div style="margin-top:20px; display:flex; gap:20px;">
            <div style="text-align:center;">
                <div style="font-family:'Playfair Display',serif; font-size:26px; color:#FFFFFF; font-weight:600;">{bmi_val:.1f}</div>
                <div style="font-size:11px; color:#2A5A7A; text-transform:uppercase;">IMC</div>
            </div>
            <div style="text-align:center;">
                <div style="font-family:'Playfair Display',serif; font-size:26px; color:#FFFFFF; font-weight:600;">{patient_data.get('Weight', 0):.0f}</div>
                <div style="font-size:11px; color:#2A5A7A; text-transform:uppercase;">kg</div>
            </div>
            <div style="text-align:center;">
                <div style="font-family:'Playfair Display',serif; font-size:26px; color:#FFFFFF; font-weight:600;">{int(patient_data.get('Age', 0))}</div>
                <div style="font-size:11px; color:#2A5A7A; text-transform:uppercase;">ans</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_proba:
    st.markdown('<div class="section-card" style="padding:24px 28px;">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 &nbsp;Probabilités</div>', unsafe_allow_html=True)
    for i in np.argsort(probas)[::-1]:
        cls_str = CLASSES_ORDER[i] if i < len(CLASSES_ORDER) else f"Classe {i}"
        cls_fr  = LABEL_FR.get(cls_str, cls_str)
        pct     = probas[i] * 100
        c, _    = LABEL_COLOR.get(cls_str, ("#1D6996", ""))
        fw      = "600" if i == pred_int else "400"
        lc      = "#FFFFFF" if i == pred_int else "#4A7A9A"
        st.markdown(f"""
        <div class="proba-row">
            <div class="proba-label" style="font-weight:{fw}; color:{lc};">{cls_fr}</div>
            <div class="proba-bar-bg"><div class="proba-bar-fill" style="width:{pct:.1f}%; background:{c};"></div></div>
            <div class="proba-value">{pct:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── SHAP ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🔍 &nbsp;Explication SHAP</div>', unsafe_allow_html=True)
if shap_fig is not None:
    st.pyplot(shap_fig)
    plt.close(shap_fig)
else:
    st.warning("Impossible de générer les explications SHAP.")
st.markdown('</div>', unsafe_allow_html=True)

# ── Sauvegarde ─────────────────────────────────────────────────────────────────
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
    save_btn = st.button("💾  Enregistrer", use_container_width=True, key="save_btn")
    st.markdown('</div>', unsafe_allow_html=True)
with col_reco:
    st.markdown('<div class="reco-btn">', unsafe_allow_html=True)
    reco_btn = st.button("✍️  Rédiger les recommandations", use_container_width=True, key="reco_btn")
    st.markdown('</div>', unsafe_allow_html=True)
with col_new:
    st.markdown('<div class="new-btn">', unsafe_allow_html=True)
    new_btn = st.button("➕  Nouveau patient", use_container_width=True, key="new_btn")
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

def load_existing_record(record_path):
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            with open(record_path, "r", encoding=enc) as f:
                return json.load(f)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return {}

def save_record():
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    record_path = RECORDS_DIR / f"{patient_id}.json"
    existing = load_existing_record(record_path) if record_path.exists() else {}
    record = {
        **existing,
        "patient_id":    patient_id,
        "patient_name":  f"{prenom} {nom}",
        "prenom":        prenom,
        "nom":           nom,
        "date_analyse":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "doctor":        st.session_state.get("display_name", "Inconnu"),
        "model_used":    model_name,
        "prediction":    pred_label,
        "confidence":    round(confidence, 1),
        "BMI":           round(bmi_val, 2),
        "clinical_data": patient_data,
    }
    with open(record_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

if save_btn:
    if st.session_state.get("patient_saved"):
        st.info("Ce dossier a déjà été enregistré dans cette session.")
    else:
        try:
            save_record()
            st.session_state["patient_saved"] = True
            st.success(f"Dossier de {prenom} {nom} enregistré avec succès.")
        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde : {e}")

if reco_btn:
    if not st.session_state.get("patient_saved"):
        try:
            save_record()
            st.session_state["patient_saved"] = True
        except Exception as e:
            st.error(f"Erreur : {e}")
            st.stop()
    st.session_state.pop("reco_text", None)
    st.session_state.pop("diet_text", None)
    st.session_state.pop("current_record", None)
    st.switch_page("pages/doctor_recommendations.py")

if new_btn:
    st.session_state.pop(shap_cache_key, None)
    st.session_state["new_patient_mode"] = True
    st.switch_page("pages/doctor_data_entry.py")