import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediObes · Dashboard",
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
    st.switch_page("pages/doctor_login.py")

# ── Paths ──────────────────────────────────────────────────────────────────────
PATIENTS_PATH = "data/patients.json"
RECORDS_DIR   = "data/records"
TRACKING_DIR  = "data/tracking"

# ── Helpers ───────────────────────────────────────────────────────────────────
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

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [data-testid="stApp"] {
    font-family: 'Inter', sans-serif;
    background: #0f1117;
    color: #e2e8f0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #141920 !important;
    border-right: 1px solid #1e2a38;
}
.sb-logo {
    font-size: 1.6rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.5px;
    margin-bottom: 2px;
}
.sb-logo span { color: #4A9FD8; }
.sb-tagline {
    font-size: 0.75rem;
    color: #6b7a8d;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 16px;
}
.sb-user {
    background: #1a2332;
    border-radius: 10px;
    padding: 12px 14px;
    margin: 10px 0;
}
.sb-user-name { font-weight: 600; font-size: 0.95rem; color: #e2e8f0; }
.sb-user-role { font-size: 0.78rem; color: #52B788; margin-top: 3px; }

/* ── Page header ── */
.page-header { margin-bottom: 28px; padding-top: 8px; }
.page-eyebrow { font-size: 0.72rem; color: #4A9FD8; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; }
.page-title { font-size: 2rem; font-weight: 700; color: #fff; line-height: 1.1; }
.page-sub { font-size: 0.9rem; color: #6b7a8d; margin-top: 6px; }

/* ── KPI grid ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}
.kpi-card {
    background: #141920;
    border: 1px solid #1e2a38;
    border-top: 3px solid var(--kpi-color, #4A9FD8);
    border-radius: 12px;
    padding: 20px 22px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}
.kpi-icon { font-size: 1.5rem; }
.kpi-num { font-size: 2.2rem; font-weight: 700; color: #fff; line-height: 1; }
.kpi-label { font-size: 0.8rem; color: #6b7a8d; font-weight: 500; }

/* ── Toolbar ── */
[data-testid="stTextInput"] input {
    background: #141920 !important;
    border: 1px solid #1e2a38 !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    padding: 10px 14px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #4A9FD8 !important;
    box-shadow: 0 0 0 3px rgba(74,159,216,0.15) !important;
}

/* ── Boutons ── */
[data-testid="stButton"] button {
    background: #4A9FD8 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: background 0.2s ease !important;
}
[data-testid="stButton"] button:hover {
    background: #3a8fc8 !important;
}

/* ── Section title ── */
.section-title {
    font-size: 1rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 16px;
    border-bottom: 1px solid #1e2a38;
    padding-bottom: 10px;
}

/* ── Table header ── */
.table-header {
    display: grid;
    grid-template-columns: 1fr 2fr 2fr 1.5fr 1fr 1fr;
    gap: 8px;
    padding: 8px 12px;
    background: #1a2332;
    border-radius: 8px 8px 0 0;
    border: 1px solid #1e2a38;
    margin-bottom: 0;
}
.table-header span {
    font-size: 0.72rem;
    font-weight: 600;
    color: #4A9FD8;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ── Patient row ── */
.patient-row {
    background: #141920;
    border: 1px solid #1e2a38;
    border-top: none;
    padding: 12px 12px;
    transition: background 0.15s ease;
}
.patient-row:hover { background: #1a2332; }
.patient-id {
    font-size: 0.78rem;
    font-weight: 600;
    color: #4A9FD8;
    font-family: 'Courier New', monospace;
    background: rgba(74,159,216,0.1);
    padding: 3px 7px;
    border-radius: 4px;
    display: inline-block;
}
.patient-name { font-weight: 600; font-size: 0.92rem; color: #e2e8f0; }
.badge {
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 20px;
    display: inline-block;
    margin-top: 4px;
    font-weight: 500;
}
.badge-ok { background: rgba(82,183,136,0.15); color: #52B788; }
.badge-wait { background: rgba(107,122,141,0.15); color: #6b7a8d; }
.diag-pill {
    font-size: 0.8rem;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 20px;
    display: inline-block;
}
.date-text { font-size: 0.82rem; color: #94a3b8; }
.weight-text { font-size: 0.85rem; font-weight: 600; color: #e2e8f0; }

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #6b7a8d;
}
.empty-icon { font-size: 3rem; margin-bottom: 12px; }
.empty-title { font-size: 1.1rem; font-weight: 600; color: #94a3b8; margin-bottom: 6px; }
.empty-sub { font-size: 0.85rem; }

/* Hide streamlit defaults */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; max-width: 1200px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">Medi<span>Obes</span></div>
    <div class="sb-tagline">Espace Médecin</div>
    <hr style="border-color:#1e2a38; margin: 8px 0 16px;">
    """, unsafe_allow_html=True)

    name = st.session_state.get("display_name", "Médecin")
    st.markdown(f"""
    <div class="sb-user">
        <div class="sb-user-name">🩺 {name}</div>
        <div class="sb-user-role">● Médecin connecté</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1e2a38; margin: 12px 0;'>", unsafe_allow_html=True)
    st.page_link("pages/doctor_dashboard.py",  label="🏠  Tableau de bord")
    st.page_link("pages/doctor_data_entry.py", label="➕  Nouveau patient")
    st.markdown("<hr style='border-color:#1e2a38; margin: 12px 0;'>", unsafe_allow_html=True)

    if st.button("🚪  Se déconnecter", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/home.py")

# ── Load data ─────────────────────────────────────────────────────────────────
all_patients = load_patients()
doctor_id    = st.session_state.get("username")

my_patients = {
    pid: pdata for pid, pdata in all_patients.items()
    if pdata.get("doctor_id") == doctor_id
}

# ── Page header ───────────────────────────────────────────────────────────────
today = datetime.now().strftime("%A %d %B %Y").capitalize()
st.markdown(f"""
<div class="page-header">
    <div class="page-eyebrow">Tableau de bord · {today}</div>
    <div class="page-title">Mes patients</div>
    <div class="page-sub">Consultez et gérez les dossiers de vos patients suivis</div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
# Preload records once for KPIs
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
    <div class="kpi-card" style="--kpi-color:#7EC8E3;">
        <div class="kpi-icon">👥</div>
        <div class="kpi-num">{total}</div>
        <div class="kpi-label">Patients suivis</div>
    </div>
    <div class="kpi-card" style="--kpi-color:#52B788;">
        <div class="kpi-icon">📋</div>
        <div class="kpi-num">{with_record}</div>
        <div class="kpi-label">Dossiers analysés</div>
    </div>
    <div class="kpi-card" style="--kpi-color:#F4A261;">
        <div class="kpi-icon">✍️</div>
        <div class="kpi-num">{with_reco}</div>
        <div class="kpi-label">Recommandations rédigées</div>
    </div>
    <div class="kpi-card" style="--kpi-color:#E05252;">
        <div class="kpi-icon">⚠️</div>
        <div class="kpi-num">{at_risk}</div>
        <div class="kpi-label">Patients à risque</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Toolbar ───────────────────────────────────────────────────────────────────
col_search, col_btn = st.columns([4, 1.2])
with col_search:
    search = st.text_input("search", placeholder="🔍  Rechercher un patient par nom…", label_visibility="collapsed")
with col_btn:
    if st.button("➕  Nouveau patient", use_container_width=True):
        st.session_state["new_patient_mode"] = True
        st.switch_page("pages/doctor_data_entry.py")

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-title">Liste des patients</div>', unsafe_allow_html=True)

# ── Patient list ──────────────────────────────────────────────────────────────
if not my_patients:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🗂️</div>
        <div class="empty-title">Aucun patient enregistré</div>
        <div class="empty-sub">Commencez par ajouter un nouveau patient via le bouton ci-dessus.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Filter
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
        # ── Table header ──
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

        # ── Rows ──
        for i, (pid, pdata) in enumerate(filtered.items()):
            record       = records_cache.get(pid)
            pred         = record.get("prediction") if record else None
            pred_fr      = LABEL_FR.get(pred, "—") if pred else "—"
            color        = LABEL_COLOR.get(pred, "#4A7A9A") if pred else "#4A7A9A"
            date_consult = record.get("date_analyse", "—") if record else "—"
            weight       = load_latest_weight(pid)
            weight_str   = f"{weight} kg" if weight else "—"
            has_reco     = bool(record and record.get("recommendations"))

            # Row background via HTML then columns for interaction
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