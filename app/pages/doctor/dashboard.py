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
    st.switch_page("pages/doctor/login.py")

# ── Paths ──────────────────────────────────────────────────────────────────────
PATIENTS_PATH = "data/patients.json"
RECORDS_DIR   = "data/records"
TRACKING_DIR  = "data/tracking"

# ── Helpers ───────────────────────────────────────────────────────────────────
def load_patients():
    if not os.path.exists(PATIENTS_PATH):
        return {}
    with open(PATIENTS_PATH, "r") as f:
        return json.load(f)

def load_record(patient_id):
    path = os.path.join(RECORDS_DIR, f"{patient_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)

def load_latest_weight(patient_id):
    path = os.path.join(TRACKING_DIR, f"{patient_id}.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    if df.empty:
        return None
    return df.iloc[-1]["poids"]

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

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0D1E30 !important;
    border-right: 1px solid rgba(29,105,150,0.15) !important;
}
[data-testid="stSidebar"] * { color: #4A7A9A !important; }
[data-testid="stSidebar"] hr { border-color: rgba(29,105,150,0.15) !important; margin: 14px 0; }

.sb-logo {
    font-family: 'Playfair Display', serif;
    font-size: 22px; font-weight: 600;
    color: #FFFFFF !important;
    letter-spacing: -0.3px;
    margin-bottom: 2px;
}
.sb-logo span { color: transparent;
    background: linear-gradient(135deg,#52B788,#7EC8E3);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text;
}
.sb-tagline { font-size: 11px; color: #1D3A50 !important; margin-bottom: 20px; }

.sb-user {
    background: rgba(29,105,150,0.12);
    border: 1px solid rgba(29,105,150,0.20);
    border-radius: 12px; padding: 12px 14px; margin-bottom: 4px;
}
.sb-user-name { font-size: 13.5px; font-weight: 500; color: #FFFFFF !important; }
.sb-user-role { font-size: 11px; color: #52B788 !important; margin-top: 2px; }

[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: rgba(29,105,150,0.12) !important;
    color: #4A7A9A !important;
    border: 1px solid rgba(29,105,150,0.20) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    transition: background 0.2s, color 0.2s !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: rgba(29,105,150,0.22) !important;
    color: #7EC8E3 !important;
    transform: none !important;
}

/* ── Page header ── */
.page-header { margin-bottom: 32px; }
.page-eyebrow {
    font-size: 11px; font-weight: 500;
    letter-spacing: 1.5px; text-transform: uppercase;
    color: #1D4A6A; margin-bottom: 6px;
}
.page-title {
    font-family: 'Playfair Display', serif;
    font-size: 34px; font-weight: 600;
    color: #FFFFFF; letter-spacing: -0.8px; margin-bottom: 4px;
}
.page-sub { font-size: 14px; color: #1D3A50; font-weight: 300; }

/* ── KPI cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}
.kpi-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 20px 22px;
    position: relative; overflow: hidden;
}
.kpi-card::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: var(--kpi-color);
}
.kpi-num {
    font-family: 'Playfair Display', serif;
    font-size: 32px; font-weight: 600;
    color: #FFFFFF; line-height: 1;
    margin-bottom: 4px;
}
.kpi-label { font-size: 12px; color: #1D3A50; text-transform: uppercase; letter-spacing: 0.8px; }
.kpi-icon { position: absolute; top: 18px; right: 18px; font-size: 20px; opacity: 0.4; }

/* ── Section title ── */
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 18px; color: #FFFFFF;
    margin-bottom: 16px;
    display: flex; align-items: center; gap: 10px;
}
.section-title::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(to right, rgba(29,105,150,0.3), transparent);
    margin-left: 8px;
}

/* ── Patient row card ── */
.patient-row {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 16px;
    transition: background 0.2s, border-color 0.2s, transform 0.2s;
    cursor: pointer;
}
.patient-row:hover {
    background: rgba(29,105,150,0.08);
    border-color: rgba(29,105,150,0.25);
    transform: translateX(4px);
}
.patient-avatar {
    width: 44px; height: 44px;
    background: rgba(29,105,150,0.18);
    border: 1px solid rgba(29,105,150,0.25);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
}
.patient-name {
    font-size: 15px; font-weight: 500; color: #FFFFFF;
    margin-bottom: 3px;
}
.patient-meta { font-size: 12px; color: #1D3A50; }
.patient-badge {
    font-size: 11.5px; font-weight: 500;
    padding: 4px 12px; border-radius: 20px;
    border: 1px solid; white-space: nowrap;
}
.patient-date { font-size: 11.5px; color: #1D3A50; white-space: nowrap; }
.patient-weight { font-size: 13px; color: #4A7A9A; white-space: nowrap; font-weight: 500;}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 64px 32px;
    background: rgba(255,255,255,0.02);
    border: 1px dashed rgba(29,105,150,0.20);
    border-radius: 16px;
}
.empty-icon { font-size: 40px; margin-bottom: 16px; opacity: 0.4; }
.empty-title { font-family: 'Playfair Display', serif; font-size: 20px; color: #FFFFFF; margin-bottom: 8px; }
.empty-sub { font-size: 13px; color: #1D3A50; }

/* ── Search input ── */
[data-testid="stTextInput"] label { display: none; }
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1.5px solid rgba(29,105,150,0.20) !important;
    border-radius: 10px !important;
    padding: 11px 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    color: #FFFFFF !important;
}
[data-testid="stTextInput"] input::placeholder { color: #1D3A50 !important; }
[data-testid="stTextInput"] input:focus {
    border-color: #1D6996 !important;
    box-shadow: 0 0 0 3px rgba(29,105,150,0.15) !important;
    background: rgba(29,105,150,0.08) !important;
}

/* ── New patient button ── */
div[data-testid="column"]:last-child [data-testid="stButton"] > button {
    background: linear-gradient(135deg, #1D6996, #155a7a) !important;
    color: #FFFFFF !important; border: none !important;
    border-radius: 10px !important; padding: 11px 20px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important; font-weight: 500 !important;
    box-shadow: 0 4px 16px rgba(29,105,150,0.30) !important;
}

/* ── Select patient button ── */
.select-btn > [data-testid="stButton"] > button {
    background: transparent !important;
    color: #4A9EC0 !important;
    border: 1px solid rgba(29,105,150,0.30) !important;
    border-radius: 8px !important;
    padding: 7px 16px !important;
    font-size: 12.5px !important;
    box-shadow: none !important;
}
.select-btn > [data-testid="stButton"] > button:hover {
    background: rgba(29,105,150,0.15) !important;
    transform: none !important;
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
    st.page_link("pages/doctor/dashboard.py",      label="🏠  Tableau de bord")
    st.page_link("pages/doctor/data_entry.py",     label="➕  Nouveau patient")
    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("🚪  Se déconnecter", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/home.py")

# ── Load data ──────────────────────────────────────────────────────────────────
all_patients = load_patients()
doctor_id    = st.session_state.get("username")

# Filtrer les patients de ce médecin
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
total      = len(my_patients)
with_record = sum(1 for pid in my_patients if load_record(pid) is not None)
with_reco   = sum(
    1 for pid in my_patients
    if load_record(pid) and load_record(pid).get("recommendations")
)
at_risk = sum(
    1 for pid in my_patients
    if load_record(pid) and load_record(pid).get("prediction", "") in
    ["Obesity_Type_I", "Obesity_Type_II", "Obesity_Type_III"]
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
        st.switch_page("pages/doctor/data_entry.py")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
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
    filtered = {
        pid: pdata for pid, pdata in my_patients.items()
        if search.lower() in pdata.get("name", "").lower()
    } if search else my_patients

    if not filtered:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-icon">🔍</div>
            <div class="empty-title">Aucun résultat</div>
            <div class="empty-sub">Aucun patient ne correspond à « {search} ».</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for pid, pdata in filtered.items():
            record  = load_record(pid)
            pred    = record.get("prediction", None) if record else None
            pred_fr = LABEL_FR.get(pred, "—") if pred else "—"
            color   = LABEL_COLOR.get(pred, "#4A7A9A") if pred else "#4A7A9A"
            date    = record.get("date_analyse", "—") if record else "—"
            weight  = load_latest_weight(pid)
            weight_str = f"{weight} kg" if weight else "—"
            has_reco = bool(record and record.get("recommendations")) if record else False

            col_info, col_badge, col_weight, col_date, col_action = st.columns([3, 2.2, 1.2, 1.5, 1.2])

            with col_info:
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:12px; padding:10px 0;">
                    <div class="patient-avatar">👤</div>
                    <div>
                        <div class="patient-name">{pdata.get('name','—')}</div>
                        <div class="patient-meta">ID : {pid} &nbsp;·&nbsp;
                            {'✅ Reco rédigée' if has_reco else '⏳ En attente de reco'}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_badge:
                st.markdown(f"""
                <div style="padding:10px 0; display:flex; align-items:center; height:100%;">
                    <span class="patient-badge"
                        style="color:{color}; border-color:{color}; background:{color}18;">
                        {pred_fr}
                    </span>
                </div>
                """, unsafe_allow_html=True)

            with col_weight:
                st.markdown(f"""
                <div style="padding:10px 0; display:flex; align-items:center; height:100%;">
                    <span class="patient-weight">⚖️ {weight_str}</span>
                </div>
                """, unsafe_allow_html=True)

            with col_date:
                st.markdown(f"""
                <div style="padding:10px 0; display:flex; align-items:center; height:100%;">
                    <span class="patient-date">📅 {date}</span>
                </div>
                """, unsafe_allow_html=True)

            with col_action:
                st.markdown('<div class="select-btn">', unsafe_allow_html=True)
                if st.button("Voir →", key=f"view_{pid}"):
                    st.session_state["selected_patient_id"] = pid
                    if record:
                        st.session_state["patient_info"] = {
                            "prenom": pdata.get("name", "").split()[0] if pdata.get("name") else "—",
                            "nom":    " ".join(pdata.get("name", "").split()[1:]) if pdata.get("name") else "—",
                        }
                        st.session_state["patient_data"]    = record.get("clinical_data", {})
                        st.session_state["prediction"]      = pred
                        st.switch_page("pages/doctor/result.py")
                    else:
                        st.session_state["patient_info"] = {
                            "prenom": pdata.get("name", "").split()[0] if pdata.get("name") else "—",
                            "nom":    " ".join(pdata.get("name", "").split()[1:]) if pdata.get("name") else "—",
                        }
                        st.switch_page("pages/doctor/data_entry.py")
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<div style='height:2px; background:rgba(29,105,150,0.08); border-radius:2px;'></div>",
                        unsafe_allow_html=True)