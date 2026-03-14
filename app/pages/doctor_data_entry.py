import streamlit as st
import json
import os
from pathlib import Path
 
# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediObes · Nouveau Patient",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ── Auth guard ─────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in") or st.session_state.get("role") != "doctor":
    st.markdown("""
    <style>
        [data-testid="stSidebar"],[data-testid="collapsedControl"],
        header[data-testid="stHeader"]{ display:none !important; }
    </style>""", unsafe_allow_html=True)
    st.warning("Accès réservé aux médecins connectés.")
    if st.button("🔐 Se connecter"):
        st.switch_page("pages/doctor_login.py")
    st.stop()

# ── Vider la session si on arrive en mode "Nouveau patient" ───────────────────
# Déclenché par le bouton "➕ Nouveau patient" depuis le dashboard ou doctor_result
if st.session_state.get("new_patient_mode"):
    for key in [
        "selected_patient_id", "patient_info", "patient_data",
        "patient_saved", "current_record", "current_patient_id",
        "reco_text", "diet_text", "prediction",
        "prediction_label", "prediction_confidence", "prediction_bmi",
    ]:
        st.session_state.pop(key, None)
    st.session_state.pop("new_patient_mode", None)

# ── Chemins absolus ────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent.parent.parent
PATIENTS_PATH = BASE_DIR / "data" / "patients.json"
PATIENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
 
def load_patients():
    if not PATIENTS_PATH.exists():
        return {}
    try:
        with open(PATIENTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}
 
def save_patient(patient_id, name, doctor_id, password="change_me"):
    patients = load_patients()
    patients[patient_id] = {
        "password":  password,
        "name":      name,
        "doctor_id": doctor_id,
    }
    with open(PATIENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(patients, f, indent=2, ensure_ascii=False)
 
# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');
 
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'DM Sans', sans-serif;
    background: #0B1628;
}
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse at 10% 30%, rgba(29,105,150,0.15) 0%, transparent 55%),
        radial-gradient(ellipse at 90% 70%, rgba(29,105,150,0.08) 0%, transparent 50%);
    pointer-events: none; z-index: 0;
}
[data-testid="stMain"] { position: relative; z-index: 1; }
 
[data-testid="stSidebar"] {
    background: #0D1E30 !important;
    border-right: 1px solid rgba(29,105,150,0.15) !important;
}
[data-testid="stSidebar"] * { color: #4A7A9A !important; }
[data-testid="stSidebar"] hr { border-color: rgba(29,105,150,0.15) !important; margin: 14px 0; }
.sb-logo {
    font-family: 'Playfair Display', serif;
    font-size: 22px; font-weight: 600; color: #FFFFFF !important; letter-spacing: -0.3px; margin-bottom: 2px;
}
.sb-logo span {
    color: transparent;
    background: linear-gradient(135deg,#52B788,#7EC8E3);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.sb-tagline { font-size: 11px; color: #1D3A50 !important; margin-bottom: 20px; }
.sb-user {
    background: rgba(29,105,150,0.12); border: 1px solid rgba(29,105,150,0.20);
    border-radius: 12px; padding: 12px 14px; margin-bottom: 4px;
}
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
 
.page-header { margin-bottom: 28px; }
.page-eyebrow { font-size: 11px; font-weight: 500; letter-spacing: 1.5px; text-transform: uppercase; color: #1D4A6A; margin-bottom: 6px; }
.page-title { font-family: 'Playfair Display', serif; font-size: 34px; font-weight: 600; color: #FFFFFF; letter-spacing: -0.8px; margin-bottom: 4px; }
.page-sub { font-size: 14px; color: #1D3A50; font-weight: 300; }
 
.section-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 28px 32px; margin-bottom: 20px;
    position: relative; overflow: hidden;
}
.section-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: var(--accent, linear-gradient(to right, #1D6996, #7EC8E3));
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 17px; color: #7EC8E3; margin-bottom: 20px;
    display: flex; align-items: center; gap: 8px;
}
.section-title::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(to right, rgba(29,105,150,0.3), transparent);
    margin-left: 8px;
}
 
.field-label {
    font-size: 11.5px; font-weight: 500; color: #2A5A7A;
    text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 5px;
}
.req { color: #E05252; margin-left: 2px; }
 
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label { display: none; }
 
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,0.05) !important;
    border: 1.5px solid rgba(29,105,150,0.22) !important;
    border-radius: 10px !important; padding: 11px 14px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 14px !important;
    color: #FFFFFF !important; transition: border-color 0.2s, box-shadow 0.2s;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stNumberInput"] input::placeholder { color: #1D3A50 !important; }
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #1D6996 !important;
    box-shadow: 0 0 0 3px rgba(29,105,150,0.15) !important;
    background: rgba(29,105,150,0.08) !important;
}
 
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1.5px solid rgba(29,105,150,0.22) !important;
    border-radius: 10px !important; color: #FFFFFF !important;
}
 
.imc-badge {
    display: inline-flex; align-items: center; gap: 10px;
    background: rgba(29,105,150,0.10);
    border: 1px solid rgba(29,105,150,0.22);
    border-radius: 10px; padding: 10px 18px;
    margin-top: 12px;
}
.imc-label { font-size: 12.5px; color: #4A7A9A; }
.imc-value { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 600; }
 
.tip-box {
    background: rgba(29,105,150,0.08);
    border-left: 3px solid #1D6996;
    border-radius: 0 10px 10px 0;
    padding: 11px 16px; font-size: 13px;
    color: #4A7A9A; margin-bottom: 24px;
}
 
.submit-row [data-testid="stButton"] > button {
    background: linear-gradient(135deg, #1D6996, #155a7a) !important;
    color: #FFFFFF !important; border: none !important;
    border-radius: 10px !important; padding: 14px 0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important; font-weight: 500 !important;
    box-shadow: 0 4px 20px rgba(29,105,150,0.35) !important;
    transition: transform 0.15s, box-shadow 0.15s;
}
.submit-row [data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 28px rgba(29,105,150,0.45) !important;
}
 
[data-testid="stCaptionContainer"] p { color: #1D3A50 !important; font-size: 11.5px !important; }
 
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: #1D6996 !important;
    border-color: #7EC8E3 !important;
}
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
    st.page_link("pages/doctor_dashboard.py",  label="🏠  Tableau de bord")
    st.page_link("pages/doctor_data_entry.py", label="➕  Nouveau patient")
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("🚪  Se déconnecter", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/home.py")
 
# ── Détection du mode (nouveau vs édition) ────────────────────────────────────
existing_patient_id  = st.session_state.get("selected_patient_id")
prefill_patient_info = st.session_state.get("patient_info", {})
# Mode édition seulement si on a un ID ET des infos patient en session
is_edit_mode = bool(existing_patient_id and prefill_patient_info.get("prenom"))

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
    <div class="page-eyebrow">Espace Médecin · Saisie clinique</div>
    <div class="page-title">{'Modifier le dossier' if is_edit_mode else 'Nouveau patient'}</div>
    <div class="page-sub">
        {'Mise à jour des données cliniques de ' + prefill_patient_info.get('prenom','') + ' ' + prefill_patient_info.get('nom','')
         if is_edit_mode else
         "Remplissez les informations du patient pour lancer l'estimation du risque"}
    </div>
</div>
""", unsafe_allow_html=True)
 
st.markdown("""
<div class="tip-box">
    💡 Tous les champs marqués <span style="color:#E05252">*</span> sont obligatoires.
    La prédiction et les explications SHAP seront générées à la soumission.
</div>
""", unsafe_allow_html=True)
 
# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Identité du patient
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-card" style="--accent: linear-gradient(to right,#1D6996,#7EC8E3);">', unsafe_allow_html=True)
st.markdown('<div class="section-title">👤 &nbsp;Identité du patient</div>', unsafe_allow_html=True)
 
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="field-label">Prénom <span class="req">*</span></div>', unsafe_allow_html=True)
    first_name = st.text_input("prenom", placeholder="Prénom",
                               value=prefill_patient_info.get("prenom", "") if is_edit_mode else "",
                               label_visibility="collapsed")
with col2:
    st.markdown('<div class="field-label">Nom <span class="req">*</span></div>', unsafe_allow_html=True)
    last_name = st.text_input("nom", placeholder="Nom",
                              value=prefill_patient_info.get("nom", "") if is_edit_mode else "",
                              label_visibility="collapsed")
with col3:
    st.markdown('<div class="field-label">ID Patient <span class="req">*</span></div>', unsafe_allow_html=True)
    patient_id_input = st.text_input(
        "patient_id",
        placeholder="ex: patient001",
        value=existing_patient_id if is_edit_mode else "",
        disabled=is_edit_mode,   # désactivé seulement en mode édition
        label_visibility="collapsed",
    )
 
col4, col5, col6 = st.columns(3)
with col4:
    st.markdown('<div class="field-label">Sexe <span class="req">*</span></div>', unsafe_allow_html=True)
    gender = st.selectbox("sexe", ["Homme", "Femme"], label_visibility="collapsed")
with col5:
    st.markdown('<div class="field-label">Âge (ans) <span class="req">*</span></div>', unsafe_allow_html=True)
    age = st.number_input("age", min_value=10, max_value=100, value=30, step=1, label_visibility="collapsed")
with col6:
    st.markdown('<div class="field-label">Mot de passe patient</div>', unsafe_allow_html=True)
    patient_pwd = st.text_input("patient_pwd",
                                placeholder="Laisser vide = 'change_me'",
                                type="password",
                                label_visibility="collapsed")
 
st.markdown('</div>', unsafe_allow_html=True)
 
# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Données biométriques
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-card" style="--accent: linear-gradient(to right,#1D6996,#7EC8E3);">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📏 &nbsp;Données biométriques</div>', unsafe_allow_html=True)
 
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="field-label">Taille (m) <span class="req">*</span></div>', unsafe_allow_html=True)
    height = st.number_input("taille", min_value=1.40, max_value=2.20, value=1.70, step=0.01, format="%.2f", label_visibility="collapsed")
with col2:
    st.markdown('<div class="field-label">Poids (kg) <span class="req">*</span></div>', unsafe_allow_html=True)
    weight = st.number_input("poids", min_value=30.0, max_value=250.0, value=70.0, step=0.5, format="%.1f", label_visibility="collapsed")
 
if height > 0:
    bmi = weight / (height ** 2)
    bmi_color = "#52B788" if bmi < 25 else "#F4A261" if bmi < 30 else "#E76F51" if bmi < 35 else "#E05252"
    bmi_label = "Normal" if bmi < 25 else "Surpoids" if bmi < 30 else "Obésité modérée" if bmi < 35 else "Obésité sévère"
    st.markdown(f"""
    <div class="imc-badge">
        <span class="imc-label">IMC calculé</span>
        <span class="imc-value" style="color:{bmi_color};">{bmi:.1f}</span>
        <span style="font-size:12px; color:{bmi_color}; font-weight:500;">kg/m² — {bmi_label}</span>
    </div>
    """, unsafe_allow_html=True)
 
st.markdown('</div>', unsafe_allow_html=True)
 
# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Habitudes alimentaires
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-card" style="--accent: linear-gradient(to right,#1D6996,#52B788);">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🍽️ &nbsp;Habitudes alimentaires</div>', unsafe_allow_html=True)
 
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="field-label">Antécédents familiaux d\'obésité <span class="req">*</span></div>', unsafe_allow_html=True)
    family_history = st.selectbox("family", ["Oui", "Non"], label_visibility="collapsed")
 
    st.markdown('<div class="field-label" style="margin-top:16px;">Aliments très caloriques fréquents (FAVC)</div>', unsafe_allow_html=True)
    favc = st.selectbox("favc", ["Oui", "Non"], label_visibility="collapsed")
 
    st.markdown('<div class="field-label" style="margin-top:16px;">Légumes par repas (FCVC)</div>', unsafe_allow_html=True)
    st.caption("1 = Jamais · 2 = Parfois · 3 = Toujours")
    fcvc = st.slider("fcvc", 1.0, 3.0, 2.0, 0.1, label_visibility="collapsed")
 
with col2:
    st.markdown('<div class="field-label">Repas principaux par jour (NCP)</div>', unsafe_allow_html=True)
    st.caption("1 à 4 repas par jour")
    ncp = st.slider("ncp", 1.0, 4.0, 3.0, 0.1, label_visibility="collapsed")
 
    st.markdown('<div class="field-label" style="margin-top:16px;">Grignotage entre les repas (CAEC)</div>', unsafe_allow_html=True)
    caec = st.selectbox("caec", ["Non", "Parfois", "Fréquemment", "Toujours"], label_visibility="collapsed")
 
    st.markdown('<div class="field-label" style="margin-top:16px;">Surveillance des calories (SCC)</div>', unsafe_allow_html=True)
    scc = st.selectbox("scc", ["Oui", "Non"], label_visibility="collapsed")
 
st.markdown('</div>', unsafe_allow_html=True)
 
# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Hygiène de vie
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-card" style="--accent: linear-gradient(to right,#52B788,#7EC8E3);">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🏃 &nbsp;Hygiène de vie & activité physique</div>', unsafe_allow_html=True)
 
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="field-label">Tabagisme</div>', unsafe_allow_html=True)
    smoke = st.selectbox("smoke", ["Non", "Oui"], label_visibility="collapsed")
 
    st.markdown('<div class="field-label" style="margin-top:16px;">Eau consommée par jour (CH2O)</div>', unsafe_allow_html=True)
    st.caption("1 = <1L · 2 = 1–2L · 3 = >2L")
    ch2o = st.slider("ch2o", 1.0, 3.0, 2.0, 0.1, label_visibility="collapsed")
 
    st.markdown('<div class="field-label" style="margin-top:16px;">Activité physique hebdomadaire (FAF)</div>', unsafe_allow_html=True)
    st.caption("0 = Aucune · 1 = 1-2j · 2 = 3-4j · 3 = Quotidien")
    faf = st.slider("faf", 0.0, 3.0, 1.0, 0.1, label_visibility="collapsed")
 
with col2:
    st.markdown('<div class="field-label">Temps sur écrans / jour (TUE)</div>', unsafe_allow_html=True)
    st.caption("0 = 0-2h · 1 = 3-5h · 2 = >5h")
    tue = st.slider("tue", 0.0, 2.0, 1.0, 0.1, label_visibility="collapsed")
 
    st.markdown('<div class="field-label" style="margin-top:16px;">Consommation d\'alcool (CALC)</div>', unsafe_allow_html=True)
    calc = st.selectbox("calc", ["Non", "Parfois", "Fréquemment", "Toujours"], label_visibility="collapsed")
 
    st.markdown('<div class="field-label" style="margin-top:16px;">Transport principal (MTRANS)</div>', unsafe_allow_html=True)
    mtrans = st.selectbox("mtrans",
        ["Transports en commun", "Voiture", "Vélo", "Moto", "À pied"],
        label_visibility="collapsed")
 
st.markdown('</div>', unsafe_allow_html=True)
 
# ══════════════════════════════════════════════════════════════════════════════
# SUBMIT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="submit-row">', unsafe_allow_html=True)
col_btn, _ = st.columns([2, 5])
with col_btn:
    submit = st.button("🔍  Lancer l'analyse", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
 
if submit:
    errors = []
    if not first_name.strip(): errors.append("Le prénom est obligatoire.")
    if not last_name.strip():  errors.append("Le nom est obligatoire.")
    if not patient_id_input.strip(): errors.append("L'ID patient est obligatoire.")
 
    if errors:
        for e in errors:
            st.error(f"⚠️ {e}")
    else:
        caec_map   = {"Non": 0, "Parfois": 1, "Fréquemment": 2, "Toujours": 3}
        calc_map   = {"Non": 0, "Parfois": 1, "Fréquemment": 2, "Toujours": 3}
        mtrans_map = {"Voiture": 0, "Vélo": 1, "Moto": 2, "Transports en commun": 3, "À pied": 4}
 
        patient_id = patient_id_input.strip()
        full_name  = f"{first_name.strip()} {last_name.strip()}"
 
        pwd = patient_pwd.strip() if patient_pwd.strip() else "change_me"
        save_patient(
            patient_id = patient_id,
            name       = full_name,
            doctor_id  = st.session_state.get("username"),
            password   = pwd,
        )
 
        st.session_state["selected_patient_id"] = patient_id
        st.session_state["patient_info"] = {
            "prenom": first_name.strip(),
            "nom":    last_name.strip(),
        }
        st.session_state["patient_data"] = {
            "Gender":                         1 if gender == "Homme" else 0,
            "Age":                            float(age),
            "Height":                         float(height),
            "Weight":                         float(weight),
            "family_history_with_overweight": 1 if family_history == "Oui" else 0,
            "FAVC":                           1 if favc == "Oui" else 0,
            "FCVC":                           fcvc,
            "NCP":                            ncp,
            "CAEC":                           caec_map[caec],
            "SMOKE":                          1 if smoke == "Oui" else 0,
            "CH2O":                           ch2o,
            "SCC":                            1 if scc == "Oui" else 0,
            "FAF":                            faf,
            "TUE":                            tue,
            "CALC":                           calc_map[calc],
            "MTRANS":                         mtrans_map[mtrans],
        }
        st.session_state.pop("patient_saved", None)
        st.session_state.pop("current_record", None)
        st.session_state.pop("current_patient_id", None)
 
        st.success(f"✅ Dossier de {full_name} créé. Lancement de l'analyse…")
        st.switch_page("pages/doctor_result.py")