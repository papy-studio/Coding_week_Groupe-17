import streamlit as st
import json
from pathlib import Path
from datetime import datetime
 
st.set_page_config(
    page_title="MediObes · Recommandations",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
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
 
# ── Chemins absolus ────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent.parent.parent
RECORDS_DIR = BASE_DIR / "data" / "records"
RECORDS_DIR.mkdir(parents=True, exist_ok=True)
 
# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');
 
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
[data-testid="stSidebar"] { background: #0D1E30 !important; border-right: 1px solid rgba(29,105,150,0.15) !important; }
[data-testid="stSidebar"] * { color: #4A7A9A !important; }
[data-testid="stSidebar"] hr { border-color: rgba(29,105,150,0.15) !important; }
.sb-logo { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 600; color: #FFFFFF !important; margin-bottom: 2px; }
.sb-logo span { color: transparent; background: linear-gradient(135deg,#52B788,#7EC8E3); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.sb-tagline { font-size: 11px; color: #1D3A50 !important; margin-bottom: 20px; }
.sb-user { background: rgba(29,105,150,0.12); border: 1px solid rgba(29,105,150,0.20); border-radius: 12px; padding: 12px 14px; margin-bottom: 4px; }
.sb-user-name { font-size: 13.5px; font-weight: 500; color: #FFFFFF !important; }
.sb-user-role { font-size: 11px; color: #52B788 !important; margin-top: 2px; }
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: rgba(29,105,150,0.12) !important; color: #4A7A9A !important;
    border: 1px solid rgba(29,105,150,0.20) !important; border-radius: 8px !important;
    font-size: 13px !important; box-shadow: none !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: rgba(29,105,150,0.22) !important; color: #7EC8E3 !important;
}
.page-eyebrow { font-size: 11px; font-weight: 500; letter-spacing: 1.5px; text-transform: uppercase; color: #1D4A6A; margin-bottom: 6px; }
.page-title { font-family: 'Playfair Display', serif; font-size: 34px; font-weight: 600; color: #FFFFFF; letter-spacing: -0.8px; margin-bottom: 4px; }
.page-sub { font-size: 14px; color: #1D3A50; font-weight: 300; margin-bottom: 28px; }
.section-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 16px; padding: 28px 32px; margin-bottom: 20px; position: relative; overflow: hidden; }
.section-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(to right, #52B788, #7EC8E3); }
.section-title { font-family: 'Playfair Display', serif; font-size: 17px; color: #7EC8E3; margin-bottom: 20px; }
.prediction-badge { border-radius: 12px; padding: 18px 24px; margin-bottom: 24px; display: flex; align-items: center; gap: 16px; }
.template-label { font-size: 11.5px; font-weight: 500; color: #2A5A7A; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 12px; }
[data-testid="stTextArea"] label { display: none; }
[data-testid="stTextArea"] textarea { background: rgba(255,255,255,0.05) !important; border: 1.5px solid rgba(29,105,150,0.22) !important; border-radius: 10px !important; color: #FFFFFF !important; font-family: 'DM Sans', sans-serif !important; font-size: 14px !important; }
[data-testid="stTextArea"] textarea:focus { border-color: #1D6996 !important; box-shadow: 0 0 0 3px rgba(29,105,150,0.15) !important; }
[data-testid="stCheckbox"] label { color: #AACCE0 !important; font-size: 13.5px !important; }
[data-testid="stButton"] > button { background: linear-gradient(135deg, #52B788, #3d8c6a) !important; color: #FFFFFF !important; border: none !important; border-radius: 10px !important; padding: 13px 0 !important; font-family: 'DM Sans', sans-serif !important; font-size: 15px !important; font-weight: 500 !important; box-shadow: 0 4px 20px rgba(82,183,136,0.3) !important; }
[data-testid="stButton"] > button:hover { transform: translateY(-1px) !important; box-shadow: 0 8px 28px rgba(82,183,136,0.45) !important; }
</style>
""", unsafe_allow_html=True)
 
# ── Sidebar ────────────────────────────────────────────────────────────────────
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
    st.page_link("pages/doctor_dashboard.py",       label="🏠  Tableau de bord")
    st.page_link("pages/doctor_data_entry.py",      label="➕  Nouveau patient")
    st.page_link("pages/doctor_recommendations.py", label="📝  Recommandations")
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("🚪  Se déconnecter", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/home.py")
 
# ── Récupérer les données de session ──────────────────────────────────────────
patient_id   = st.session_state.get("selected_patient_id")
patient_info = st.session_state.get("patient_info", {})
patient_data = st.session_state.get("patient_data", {})
prediction   = st.session_state.get("prediction_label", "")
confidence   = st.session_state.get("prediction_confidence", 0.0)
bmi          = st.session_state.get("prediction_bmi", 0.0)
 
if not patient_id or not prediction:
    st.warning("Aucune prédiction disponible. Veuillez d'abord saisir les données du patient.")
    if st.button("← Retour à la saisie"):
        st.switch_page("pages/doctor_data_entry.py")
    st.stop()
 
prenom = patient_info.get("prenom", "")
nom    = patient_info.get("nom", "")
 
# ── Page header ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div>
    <div class="page-eyebrow">Espace Médecin · Recommandations</div>
    <div class="page-title">Recommandations</div>
    <div class="page-sub">Rédiger les recommandations pour {prenom} {nom}</div>
</div>
""", unsafe_allow_html=True)
 
# ── Mapping classes ────────────────────────────────────────────────────────────
CLASS_MAPPING = {
    "Insufficient_Weight":  {"label": "Poids Insuffisant",           "color": "#2196F3"},
    "Normal_Weight":        {"label": "Poids Normal",                "color": "#52B788"},
    "Overweight_Level_I":   {"label": "Surpoids — Niveau I",         "color": "#F4A261"},
    "Overweight_Level_II":  {"label": "Surpoids — Niveau II",        "color": "#E76F51"},
    "Obesity_Type_I":       {"label": "Obésité — Type I",            "color": "#E05252"},
    "Obesity_Type_II":      {"label": "Obésité — Type II",           "color": "#C62828"},
    "Obesity_Type_III":     {"label": "Obésité — Type III (Morbide)","color": "#7B0000"},
}
 
info  = CLASS_MAPPING.get(prediction, {"label": prediction, "color": "#888"})
color = info["color"]
label = info["label"]
 
# ── Résumé prédiction ──────────────────────────────────────────────────────────
st.markdown(f"""
<div class="prediction-badge" style="background:{color}18; border:2px solid {color}40;">
    <div style="font-size:36px;">🎯</div>
    <div>
        <div style="font-size:11px; color:{color}; text-transform:uppercase; letter-spacing:1px; font-weight:500;">Prédiction</div>
        <div style="font-size:22px; font-weight:600; color:{color};">{label}</div>
        <div style="font-size:13px; color:#4A7A9A; margin-top:4px;">
            Confiance : <b style="color:#AACCE0;">{confidence:.1f}%</b> &nbsp;·&nbsp;
            IMC : <b style="color:#AACCE0;">{bmi:.1f}</b> &nbsp;·&nbsp;
            Patient : <b style="color:#AACCE0;">{patient_id}</b>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
 
# ── Templates (extraits du notebook Cell 14) ──────────────────────────────────
TEMPLATES = {
    "Activité physique": [
        "Augmenter l'activité physique à 30 min/jour minimum.",
        "Pratiquer une activité d'endurance (marche rapide, vélo, natation) 3×/semaine.",
        "Réduire le temps sédentaire : se lever toutes les heures.",
    ],
    "Alimentation": [
        "Réduire la consommation d'aliments ultra-transformés.",
        "Favoriser les légumes et fibres à chaque repas.",
        "Éviter les grignotages entre les repas.",
        "Augmenter la consommation d'eau à 2L/jour.",
        "Consulter un nutritionniste pour un plan alimentaire adapté.",
    ],
    "Suivi médical": [
        "Surveiller l'IMC chaque mois.",
        "Bilan sanguin (cholestérol, glycémie) dans 3 mois.",
        "Consultation de suivi dans 1 mois.",
    ],
    "Mode de vie": [
        "Réduire la consommation d'alcool.",
        "Arrêter le tabac — orientation vers sevrage tabagique recommandée.",
        "Améliorer la qualité du sommeil (7–9h/nuit).",
    ],
}
 
# ── Section templates ──────────────────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">✅ &nbsp;Modèles rapides</div>', unsafe_allow_html=True)
st.markdown('<div class="template-label">Cochez les recommandations à inclure</div>', unsafe_allow_html=True)
 
selected_templates = []
for category, items in TEMPLATES.items():
    st.markdown(f"**{category}**")
    for item in items:
        if st.checkbox(item, key=f"cb_{item[:40]}"):
            selected_templates.append(item)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
 
st.markdown('</div>', unsafe_allow_html=True)
 
# ── Section texte libre ────────────────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">✏️ &nbsp;Recommandations personnalisées</div>', unsafe_allow_html=True)
st.markdown('<div class="template-label">Texte libre — complément ou remplacement</div>', unsafe_allow_html=True)
 
custom_reco = st.text_area(
    "custom_reco",
    placeholder="Saisir les recommandations personnalisées pour ce patient...",
    height=150,
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)
 
# ── Aperçu ─────────────────────────────────────────────────────────────────────
all_recos = selected_templates + ([custom_reco.strip()] if custom_reco.strip() else [])
 
if all_recos:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👁️ &nbsp;Aperçu — ce qui sera sauvegardé</div>', unsafe_allow_html=True)
    for r in all_recos:
        st.markdown(f"- {r}")
    st.markdown('</div>', unsafe_allow_html=True)
 
# ── Sauvegarde ─────────────────────────────────────────────────────────────────
col_btn, _ = st.columns([2, 5])
with col_btn:
    save_btn = st.button("💾  Sauvegarder la consultation", use_container_width=True)
 
if save_btn:
    if not all_recos:
        st.error("⚠️ Aucune recommandation saisie. Cochez au moins un template ou rédigez un texte.")
    else:
        record_path = RECORDS_DIR / f"{patient_id}.json"
 
        # Charger l'existant pour ne pas écraser la prédiction
        existing = {}
        if record_path.exists():
            with open(record_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
 
        record = {
            **existing,
            "patient_id":      patient_id,
            "nom":             nom,
            "prenom":          prenom,
            "date_analyse":    existing.get("date_analyse", datetime.now().strftime("%Y-%m-%d %H:%M")),
            "date_reco":       datetime.now().strftime("%Y-%m-%d %H:%M"),
            "medecin":         st.session_state.get("username", ""),
            "prediction":      prediction,
            "confidence":      round(confidence, 1),
            "BMI":             round(bmi, 1),
            "recommendations": "\n".join(f"• {r}" for r in all_recos),
        }
 
        with open(record_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
 
        st.success(f"✅ Consultation sauvegardée pour {prenom} {nom} ({patient_id})")
        st.balloons()
 
        # Nettoyer session
        for key in ["selected_patient_id", "patient_info", "patient_data",
                    "prediction_label", "prediction_confidence", "prediction_bmi",
                    "prediction", "patient_saved"]:
            st.session_state.pop(key, None)
 
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("🏠 Retour au tableau de bord", key="back_dashboard"):
            st.switch_page("pages/doctor_dashboard.py")
 