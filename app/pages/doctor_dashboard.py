import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# ── Configuration de la page ───────────────────────────────────────────────────
st.set_page_config(
    page_title="MediObes · Dashboard Médecin",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Vérification de connexion ─────────────────────────────────────────────────
if not st.session_state.get("logged_in") or st.session_state.get("role") != "doctor":
    st.switch_page("pages/doctor_login.py")

# ── Chemins des données ───────────────────────────────────────────────────────
PATIENTS_PATH = "data/patients.json"
RECORDS_DIR   = "data/records"
TRACKING_DIR   = "data/tracking"

# ── Fonctions utilitaires (inchangées) ────────────────────────────────────────
def load_patients():
    if not os.path.exists(PATIENTS_PATH):
        return {}
    with open(PATIENTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_record(patient_id):
    path = os.path.join(RECORDS_DIR, f"{patient_id}.json")
    if not os.path.exists(path):
        return None
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            with open(path, "r", encoding=enc) as f:
                return json.load(f)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return None

def load_latest_weight(patient_id):
    path = os.path.join(TRACKING_DIR, f"{patient_id}.csv")
    if not os.path.exists(path):
        return None
    try:
        df = pd.read_csv(path)
        if df.empty:
            return None
        return df.iloc[-1]["poids"]
    except Exception:
        return None

LABEL_FR = {
    "Insufficient_Weight":  "Poids Insuffisant",
    "Normal_Weight":        "Poids Normal",
    "Overweight_Level_I":   "Surpoids — Niv. I",
    "Overweight_Level_II":  "Surpoids — Niv. II",
    "Obesity_Type_I":       "Obésité — Type I",
    "Obesity_Type_II":      "Obésité — Type II",
    "Obesity_Type_III":     "Obésité — Type III",
}

LABEL_COLOR = {
    "Insufficient_Weight":  "#2196F3",
    "Normal_Weight":        "#52B788",
    "Overweight_Level_I":   "#F4A261",
    "Overweight_Level_II":  "#E76F51",
    "Obesity_Type_I":       "#E05252",
    "Obesity_Type_II":      "#C62828",
    "Obesity_Type_III":     "#7B0000",
}

# ── STYLE (repris de l'espace patient, adapté pour le docteur) ─────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

/* Masquer la navigation automatique de Streamlit dans la sidebar */
[data-testid="stSidebarNav"] { display: none; }

.stApp { background-color: #0B1628; }
h1, h2, h3 { font-family: 'Playfair Display', serif; color: white; }

/* ── Sidebar (identique à l'espace patient) ── */
[data-testid="stSidebar"] {
    background-color: #0d1f35;
    border-right: 1px solid rgba(255,255,255,0.07);
}
.sidebar-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: white;
    margin-bottom: 4px;
}
.sidebar-logo span { color: #52B788; }
.sidebar-role {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.35);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 2rem;
    font-family: 'DM Sans', sans-serif;
}
.user-card {
    background: rgba(82,183,136,0.08);
    border: 1px solid rgba(82,183,136,0.2);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 2rem;
}
.user-name { color: white; font-size: 0.92rem; font-weight: 500; font-family: 'DM Sans', sans-serif; }
.user-sub  { color: rgba(255,255,255,0.4); font-size: 0.75rem; margin-top: 2px; font-family: 'DM Sans', sans-serif; }
.nav-section {
    font-size: 0.68rem;
    color: rgba(255,255,255,0.25);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 1.2rem 0 0.5rem 0;
    font-family: 'DM Sans', sans-serif;
}
div[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    color: rgba(255,255,255,0.65);
    border: none;
    border-radius: 8px;
    text-align: left;
    width: 100%;
    padding: 0.5rem 0.75rem;
    font-size: 0.88rem;
    font-family: 'DM Sans', sans-serif;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.06);
    color: white;
}
/* Bouton déconnexion */
div[data-testid="stSidebar"] [data-testid="stButton"]:last-child > button {
    color: #E05252 !important;
}
div[data-testid="stSidebar"] [data-testid="stButton"]:last-child > button:hover {
    background: rgba(224,82,82,0.1) !important;
}

/* ── Page header ── */
.page-header {
    padding: 28px 0 24px 0;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 40px;
}
.page-eyebrow {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #52B788;
    margin-bottom: 6px;
}
.page-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 600;
    color: white;
    margin-bottom: 4px;
}
.page-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.88rem;
    color: rgba(255,255,255,0.35);
}

/* ── KPIs ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}
.kpi-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 20px 22px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(to right, #52B788, #A8E6CF);
}
.kpi-icon { font-size: 1.5rem; margin-bottom: 8px; }
.kpi-num {
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    font-weight: 600;
    color: white;
    margin-bottom: 4px;
}
.kpi-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem;
    color: rgba(255,255,255,0.35);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Toolbar (recherche + bouton) ── */
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.05) !important;
    border: 1.5px solid rgba(82,183,136,0.22) !important;
    border-radius: 10px !important;
    color: white !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stButton"] button {
    background: linear-gradient(135deg, #52B788, #3d9e70) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
}

/* ── Section title ── */
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    color: #52B788;
    margin-bottom: 18px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    padding-bottom: 8px;
}

/* ── Table header ── */
.table-header {
    display: grid;
    grid-template-columns: 1fr 2fr 2fr 1.5fr 1fr 1fr;
    gap: 8px;
    padding: 8px 12px;
    background: rgba(82,183,136,0.08);
    border-radius: 8px 8px 0 0;
    border: 1px solid rgba(82,183,136,0.2);
    border-bottom: none;
    margin-bottom: 0;
}
.table-header span {
    font-size: 0.72rem;
    font-weight: 600;
    color: #52B788;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'DM Sans', sans-serif;
}

/* ── Patient row ── */
.patient-row {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-top: none;
    padding: 12px 12px;
    transition: background 0.15s ease;
}
.patient-row:hover { background: rgba(255,255,255,0.04); }
.patient-id {
    font-size: 0.78rem;
    font-weight: 600;
    color: #52B788;
    font-family: 'Courier New', monospace;
    background: rgba(82,183,136,0.1);
    padding: 3px 7px;
    border-radius: 4px;
    display: inline-block;
}
.patient-name {
    font-weight: 600;
    font-size: 0.92rem;
    color: white;
    font-family: 'DM Sans', sans-serif;
}
.badge {
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 20px;
    display: inline-block;
    margin-top: 4px;
    font-weight: 500;
    font-family: 'DM Sans', sans-serif;
}
.badge-ok { background: rgba(82,183,136,0.15); color: #52B788; }
.badge-wait { background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.5); }
.diag-pill {
    font-size: 0.8rem;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 20px;
    display: inline-block;
    font-family: 'DM Sans', sans-serif;
}
.date-text, .weight-text {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.7);
    font-family: 'DM Sans', sans-serif;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: rgba(255,255,255,0.3);
    font-family: 'DM Sans', sans-serif;
}
.empty-icon { font-size: 3rem; margin-bottom: 12px; }
.empty-title { font-size: 1.1rem; font-weight: 600; color: rgba(255,255,255,0.6); margin-bottom: 6px; }
.empty-sub { font-size: 0.85rem; }

/* ── CORRECTION DU HEADER (garder le bouton de réouverture) ── */
#MainMenu, footer {
    visibility: hidden;
}
header[data-testid="stHeader"] {
    display: flex !important;
    visibility: visible !important;
    background-color: #0B1628;  /* assorti au fond */
}
header [data-testid="stLogo"] {
    display: none !important;
}
header [data-testid="stStatusWidget"] {
    display: none !important;
}

.block-container { padding-top: 2rem !important; max-width: 1200px; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR (STYLE PATIENT, CONTENU MÉDECIN) ──────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">Medi<span>Obes</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-role">Espace Médecin</div>', unsafe_allow_html=True)

    # Informations du médecin connecté
    doctor_name = st.session_state.get("display_name", "Dr. Martin")
    st.markdown(f"""
    <div class="user-card">
        <div class="user-name">{doctor_name}</div>
        <div class="user-sub">Médecin traitant</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-section">Navigation</div>', unsafe_allow_html=True)
    if st.button("📋  Tableau de bord", use_container_width=True, key="nav_dashboard"):
        st.switch_page("pages/doctor_dashboard.py")
    if st.button("➕  Nouveau patient", use_container_width=True, key="nav_new_patient"):
        st.switch_page("pages/doctor_data_entry.py")
    if st.button("📊  Résultat", use_container_width=True, key="nav_result"):
        st.switch_page("pages/doctor_result.py")
    if st.button("📝  Recommandations", use_container_width=True, key="nav_recommendations"):
        st.switch_page("pages/doctor_recommendations.py")
    st.markdown("---")
    if st.button("🚪  Se déconnecter", use_container_width=True, key="logout"):
        st.session_state.clear()
        st.switch_page("pages/home.py")

# ── CHARGEMENT DES DONNÉES (inchangé) ─────────────────────────────────────────
all_patients = load_patients()
doctor_id    = st.session_state.get("username")

my_patients = {
    pid: pdata for pid, pdata in all_patients.items()
    if pdata.get("doctor_id") == doctor_id
}

# ── EN-TÊTE DE PAGE ───────────────────────────────────────────────────────────
today = datetime.now().strftime("%A %d %B %Y").capitalize()
st.markdown(f"""
<div class="page-header">
    <div class="page-eyebrow">Tableau de bord · {today}</div>
    <div class="page-title">Mes patients</div>
    <div class="page-sub">Consultez et gérez les dossiers de vos patients suivis</div>
</div>
""", unsafe_allow_html=True)

# ── INDICATEURS (KPIs) ────────────────────────────────────────────────────────
records_cache = {pid: load_record(pid) for pid in my_patients}

total       = len(my_patients)
with_record = sum(1 for r in records_cache.values() if r is not None)
with_reco   = sum(1 for r in records_cache.values() if r and r.get("recommendations"))
at_risk     = sum(
    1 for r in records_cache.values()
    if r and r.get("prediction", "") in ["Obesity_Type_I", "Obesity_Type_II", "Obesity_Type_III"]
)

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-icon">👥</div>
        <div class="kpi-num">{total}</div>
        <div class="kpi-label">Patients suivis</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon">📋</div>
        <div class="kpi-num">{with_record}</div>
        <div class="kpi-label">Dossiers analysés</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon">✍️</div>
        <div class="kpi-num">{with_reco}</div>
        <div class="kpi-label">Recommandations</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon">⚠️</div>
        <div class="kpi-num">{at_risk}</div>
        <div class="kpi-label">Patients à risque</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── BARRE D'OUTILS ────────────────────────────────────────────────────────────
col_search, col_btn = st.columns([4, 1.2])
with col_search:
    search = st.text_input("search", placeholder="🔍  Rechercher un patient par nom…", label_visibility="collapsed")
with col_btn:
    if st.button("➕  Nouveau patient", use_container_width=True):
        st.session_state["new_patient_mode"] = True
        st.switch_page("pages/doctor_data_entry.py")

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-title">Liste des patients</div>', unsafe_allow_html=True)

# ── LISTE DES PATIENTS (inchangée) ────────────────────────────────────────────
if not my_patients:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🗂️</div>
        <div class="empty-title">Aucun patient enregistré</div>
        <div class="empty-sub">Commencez par ajouter un nouveau patient via le bouton ci-dessus.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    filtered = {
        pid: pdata for pid, pdata in my_patients.items()
        if not search or search.lower() in pdata.get("name", "").lower()
    }

    if not filtered:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-icon">🔍</div>
            <div class="empty-title">Aucun résultat</div>
            <div class="empty-sub">Aucun patient ne correspond à « {search} ».</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # En-tête du tableau
        st.markdown("""
        <div class="table-header">
            <span>ID Patient</span>
            <span>Nom</span>
            <span>Diagnostic</span>
            <span>Dernière consultation</span>
            <span>Poids</span>
            <span>Action</span>
        </div>
        """, unsafe_allow_html=True)

        # Lignes patients
        for i, (pid, pdata) in enumerate(filtered.items()):
            record       = records_cache.get(pid)
            pred         = record.get("prediction") if record else None
            pred_fr      = LABEL_FR.get(pred, "—") if pred else "—"
            color        = LABEL_COLOR.get(pred, "#4A7A9A") if pred else "#4A7A9A"
            date_consult = record.get("date_analyse", "—") if record else "—"
            weight       = load_latest_weight(pid)
            weight_str   = f"{weight} kg" if weight else "—"
            has_reco     = bool(record and record.get("recommendations"))

            st.markdown('<div class="patient-row">', unsafe_allow_html=True)
            col_id, col_nom, col_diag, col_date, col_poids, col_action = st.columns([1, 2, 2, 1.5, 1, 1])

            with col_id:
                st.markdown(f'<span class="patient-id">{pid}</span>', unsafe_allow_html=True)

            with col_nom:
                badge_cls  = "badge-ok" if has_reco else "badge-wait"
                badge_text = "✅ Recommandation" if has_reco else "⏳ En attente"
                st.markdown(f"""
                <div class="patient-name">{pdata.get('name', '—')}</div>
                <span class="badge {badge_cls}">{badge_text}</span>
                """, unsafe_allow_html=True)

            with col_diag:
                if pred:
                    bg = color + "22"
                    st.markdown(
                        f'<span class="diag-pill" style="background:{bg}; color:{color};">{pred_fr}</span>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown('<span style="color:#4b5563;">—</span>', unsafe_allow_html=True)

            with col_date:
                st.markdown(f'<div class="date-text">{date_consult}</div>', unsafe_allow_html=True)

            with col_poids:
                st.markdown(f'<div class="weight-text">{weight_str}</div>', unsafe_allow_html=True)

            with col_action:
                if st.button("Voir →", key=f"view_{pid}_{i}"):
                    st.session_state["selected_patient_id"] = pid
                    name_parts = pdata.get("name", "").split()
                    st.session_state["patient_info"] = {
                        "prenom": name_parts[0] if name_parts else "—",
                        "nom":    " ".join(name_parts[1:]) if len(name_parts) > 1 else "—",
                    }
                    if record:
                        st.session_state["patient_data"] = record.get("clinical_data", {})
                        st.session_state["prediction"]   = pred
                        st.switch_page("pages/doctor_result.py")
                    else:
                        st.switch_page("pages/doctor_data_entry.py")

            st.markdown('</div>', unsafe_allow_html=True)