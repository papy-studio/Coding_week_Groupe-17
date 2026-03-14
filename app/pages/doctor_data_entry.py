import streamlit as st
import json
from pathlib import Path

st.set_page_config(
    page_title="MediObes · Nouveau Patient",
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
    st.warning("Accès réservé aux médecins connectés.")
    if st.button("🔐 Se connecter"):
        st.switch_page("pages/doctor_login.py")
    st.stop()

# ── Vider la session si nouveau patient ───────────────────────────────────────
if st.session_state.get("new_patient_mode"):
    for key in [
        "selected_patient_id", "patient_info", "patient_data",
        "patient_saved", "current_record", "current_patient_id",
        "reco_text", "diet_text", "prediction",
        "prediction_label", "prediction_confidence", "prediction_bmi",
    ]:
        st.session_state.pop(key, None)
    st.session_state.pop("new_patient_mode", None)

# ── Chemins ────────────────────────────────────────────────────────────────────
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
    patients[patient_id] = {"password": password, "name": name, "doctor_id": doctor_id}
    with open(PATIENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(patients, f, indent=2, ensure_ascii=False)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

section[data-testid="stSidebar"] { display: block !important; background-color: #0d1f35 !important; }
[data-testid="stSidebarNav"], div[data-testid="stSidebarNav"],
.css-1d391kg, .css-1lcbmhc, .css-1wrcr25,
.eczjsme11, .eczjsme12, .eczjsme13 { display: none !important; }

.stApp { background-color: #0B1628; }
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
.section-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 16px; padding: 28px 32px; margin-bottom: 20px; position: relative; overflow: hidden; }
.section-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(to right, #52B788, #A8E6CF); }
.section-title { font-family: 'Playfair Display', serif; font-size: 1.1rem; color: #52B788; margin-bottom: 18px; display: flex; align-items: center; gap: 8px; }
.section-title::after { content: ''; flex: 1; height: 1px; background: linear-gradient(to right, #52B788, transparent); margin-left: 8px; }
.field-label { font-size: 11.5px; font-weight: 500; color: #2A5A7A; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 5px; }
.req { color: #E05252; margin-left: 2px; }
[data-testid="stTextInput"] label, [data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label, [data-testid="stSlider"] label { display: none; }
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input { background: rgba(255,255,255,0.05) !important; border: 1.5px solid rgba(82,183,136,0.22) !important; border-radius: 10px !important; padding: 11px 14px !important; font-family: 'DM Sans', sans-serif !important; font-size: 14px !important; color: #FFFFFF !important; }
[data-testid="stTextInput"] input:focus, [data-testid="stNumberInput"] input:focus { border-color: #52B788 !important; box-shadow: 0 0 0 3px rgba(82,183,136,0.15) !important; background: rgba(82,183,136,0.06) !important; }
[data-testid="stSelectbox"] > div > div { background: rgba(255,255,255,0.05) !important; border: 1.5px solid rgba(82,183,136,0.22) !important; border-radius: 10px !important; color: #FFFFFF !important; }
.imc-badge { display: inline-flex; align-items: center; gap: 10px; background: rgba(82,183,136,0.10); border: 1px solid rgba(82,183,136,0.22); border-radius: 10px; padding: 10px 18px; margin-top: 12px; }
.imc-label { font-size: 12.5px; color: #4A7A9A; }
.imc-value { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 600; }
.tip-box { background: rgba(82,183,136,0.08); border-left: 3px solid #52B788; border-radius: 0 10px 10px 0; padding: 11px 16px; font-size: 13px; color: #4A7A9A; margin-bottom: 24px; }
.submit-row [data-testid="stButton"] > button { background: linear-gradient(135deg, #52B788, #3d9e70) !important; color: #FFFFFF !important; border: none !important; border-radius: 10px !important; padding: 14px 0 !important; font-family: 'DM Sans', sans-serif !important; font-size: 15px !important; font-weight: 500 !important; box-shadow: 0 4px 20px rgba(82,183,136,0.35) !important; }
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
    if st.button("📋  Tableau de bord",  use_container_width=True, key="nav_dashboard"):      st.switch_page("pages/doctor_dashboard.py")
    if st.button("➕  Nouveau patient",  use_container_width=True, key="nav_new_patient"):    st.switch_page("pages/doctor_data_entry.py")
    if st.button("📊  Résultat",         use_container_width=True, key="nav_result"):         st.switch_page("pages/doctor_result.py")
    if st.button("📝  Recommandations",  use_container_width=True, key="nav_recommendations"):st.switch_page("pages/doctor_recommendations.py")
    st.markdown("---")
    if st.button("🚪  Se déconnecter",   use_container_width=True, key="logout"):
        st.session_state.clear()
        st.switch_page("pages/home.py")

# ── Détection mode ─────────────────────────────────────────────────────────────
existing_patient_id  = st.session_state.get("selected_patient_id")
prefill_patient_info = st.session_state.get("patient_info", {})
is_edit_mode = bool(existing_patient_id and prefill_patient_info.get("prenom"))

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
    <div class="page-eyebrow">Espace Médecin · Saisie clinique</div>
    <div class="page-title">{'Modifier le dossier' if is_edit_mode else 'Nouveau patient'}</div>
    <div class="page-sub">{'Mise à jour des données cliniques de ' + prefill_patient_info.get('prenom','') + ' ' + prefill_patient_info.get('nom','') if is_edit_mode else "Remplissez les informations du patient pour lancer l'estimation du risque"}</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="tip-box">💡 Tous les champs marqués <span style="color:#E05252">*</span> sont obligatoires. La prédiction et les explications SHAP seront générées à la soumission.</div>', unsafe_allow_html=True)

# ── Section 1 — Identité ──────────────────────────────────────────────────────
st.markdown('<div class="section-card"><div class="section-title">👤 &nbsp;Identité du patient</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="field-label">Prénom <span class="req">*</span></div>', unsafe_allow_html=True)
    first_name = st.text_input("prenom", placeholder="Prénom", value=prefill_patient_info.get("prenom", "") if is_edit_mode else "", label_visibility="collapsed")
with col2:
    st.markdown('<div class="field-label">Nom <span class="req">*</span></div>', unsafe_allow_html=True)
    last_name = st.text_input("nom", placeholder="Nom", value=prefill_patient_info.get("nom", "") if is_edit_mode else "", label_visibility="collapsed")
with col3:
    st.markdown('<div class="field-label">ID Patient <span class="req">*</span></div>', unsafe_allow_html=True)
    patient_id_input = st.text_input("patient_id", placeholder="ex: patient001", value=existing_patient_id if is_edit_mode else "", disabled=is_edit_mode, label_visibility="collapsed")
col4, col5, col6 = st.columns(3)
with col4:
    st.markdown('<div class="field-label">Sexe <span class="req">*</span></div>', unsafe_allow_html=True)
    gender = st.selectbox("sexe", ["Homme", "Femme"], label_visibility="collapsed")
with col5:
    st.markdown('<div class="field-label">Âge (ans) <span class="req">*</span></div>', unsafe_allow_html=True)
    age = st.number_input("age", min_value=10, max_value=100, value=30, step=1, label_visibility="collapsed")
with col6:
    st.markdown('<div class="field-label">Mot de passe patient</div>', unsafe_allow_html=True)
    patient_pwd = st.text_input("patient_pwd", placeholder="Laisser vide = 'change_me'", type="password", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# ── Section 2 — Biométrie ─────────────────────────────────────────────────────
st.markdown('<div class="section-card"><div class="section-title">📏 &nbsp;Données biométriques</div>', unsafe_allow_html=True)
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
    st.markdown(f'<div class="imc-badge"><span class="imc-label">IMC calculé</span><span class="imc-value" style="color:{bmi_color};">{bmi:.1f}</span><span style="font-size:12px; color:{bmi_color}; font-weight:500;">kg/m² — {bmi_label}</span></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Section 3 — Alimentation ──────────────────────────────────────────────────
st.markdown('<div class="section-card"><div class="section-title">🍽️ &nbsp;Habitudes alimentaires</div>', unsafe_allow_html=True)
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

# ── Section 4 — Hygiène de vie ────────────────────────────────────────────────
st.markdown('<div class="section-card"><div class="section-title">🏃 &nbsp;Hygiène de vie & activité physique</div>', unsafe_allow_html=True)
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
    mtrans = st.selectbox("mtrans", ["Transports en commun", "Voiture", "Vélo", "Moto", "À pied"], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# ── Submit ─────────────────────────────────────────────────────────────────────
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
        for e in errors: st.error(f"⚠️ {e}")
    else:
        caec_map   = {"Non": 0, "Parfois": 1, "Fréquemment": 2, "Toujours": 3}
        calc_map   = {"Non": 0, "Parfois": 1, "Fréquemment": 2, "Toujours": 3}
        mtrans_map = {"Voiture": 0, "Vélo": 1, "Moto": 2, "Transports en commun": 3, "À pied": 4}
        patient_id = patient_id_input.strip()
        full_name  = f"{first_name.strip()} {last_name.strip()}"
        pwd = patient_pwd.strip() if patient_pwd.strip() else "change_me"
        save_patient(patient_id=patient_id, name=full_name, doctor_id=st.session_state.get("username"), password=pwd)
        st.session_state["selected_patient_id"] = patient_id
        st.session_state["patient_info"] = {"prenom": first_name.strip(), "nom": last_name.strip()}
        st.session_state["patient_data"] = {
            "Gender": 1 if gender == "Homme" else 0, "Age": float(age),
            "Height": float(height), "Weight": float(weight),
            "family_history_with_overweight": 1 if family_history == "Oui" else 0,
            "FAVC": 1 if favc == "Oui" else 0, "FCVC": fcvc, "NCP": ncp,
            "CAEC": caec_map[caec], "SMOKE": 1 if smoke == "Oui" else 0,
            "CH2O": ch2o, "SCC": 1 if scc == "Oui" else 0,
            "FAF": faf, "TUE": tue, "CALC": calc_map[calc], "MTRANS": mtrans_map[mtrans],
        }
        st.session_state.pop("patient_saved", None)
        st.session_state.pop("current_record", None)
        st.session_state.pop("current_patient_id", None)
        st.session_state.pop(f"shap_done_{patient_id}", None)
        st.success(f"✅ Dossier de {full_name} créé. Lancement de l'analyse…")
        st.switch_page("pages/doctor_result.py")