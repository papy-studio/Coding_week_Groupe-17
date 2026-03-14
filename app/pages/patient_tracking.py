import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os
from datetime import date
from pathlib import Path

st.set_page_config(
    page_title="MediObes · Suivi de poids",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    [data-testid="stSidebarNav"] { display: none; }
    #MainMenu, footer { visibility: hidden; }   /* ← header n'est plus caché */
    /* Optionnel : masquer d'autres éléments du header */
    header [data-testid="stLogo"] { display: none; }
    header [data-testid="stStatusWidget"] { display: none; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("logged_in") or st.session_state.get("role") != "patient":
    st.switch_page("pages/patient_login.py")

patient_id   = st.session_state.get("username", "")
TRACKING_DIR = Path("data/tracking")
RECORDS_DIR  = Path("data/records")
TRACKING_DIR.mkdir(parents=True, exist_ok=True)

def tracking_path():
    return TRACKING_DIR / f"{patient_id}.csv"

def load_imc():
    path = RECORDS_DIR / f"{patient_id}.json"
    if not path.exists():
        return 0.0
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            with open(path, "r", encoding=enc) as f:
                record = json.load(f)
            return float(record.get("BMI", 0))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return 0.0

def load_patient_info():
    patients_file = Path("data/patients.json")
    record_file   = RECORDS_DIR / f"{patient_id}.json"
    display_name  = st.session_state.get("display_name", "")
    medecin       = ""

    for enc in ["utf-8", "latin-1", "cp1252"]:
        try:
            if record_file.exists():
                with open(record_file, "r", encoding=enc) as f:
                    rec = json.load(f)
                if not display_name:
                    prenom = rec.get("prenom", "")
                    nom    = rec.get("nom", "")
                    display_name = f"{prenom} {nom}".strip()
                medecin = (rec.get("reco_author", "") or
                           rec.get("doctor", "") or
                           rec.get("medecin", ""))
                break
        except Exception:
            continue

    if not display_name or not medecin:
        try:
            if patients_file.exists():
                with open(patients_file, "r", encoding="utf-8") as f:
                    patients = json.load(f)
                info = patients.get(patient_id, {})
                if not display_name:
                    prenom = info.get("prenom", "")
                    nom    = info.get("nom", "")
                    display_name = f"{prenom} {nom}".strip()
                if not medecin:
                    medecin = info.get("medecin_referent", "")
        except Exception:
            pass

    return display_name or "Patient", medecin or "Non assigné"

def load_suivi() -> pd.DataFrame:
    path = tracking_path()
    if not path.exists():
        return pd.DataFrame(columns=["date", "poids"])
    try:
        df = pd.read_csv(path)
        df["date"] = pd.to_datetime(df["date"])
        return df.sort_values("date").reset_index(drop=True)
    except Exception:
        return pd.DataFrame(columns=["date", "poids"])

def save_poids(poids: float):
    path      = tracking_path()
    today_str = date.today().isoformat()
    new_row   = pd.DataFrame([{"date": today_str, "poids": poids}])
    if path.exists():
        df = pd.read_csv(path)
        df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)
        df = df[df["date"] != today_str]
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
    df.to_csv(path, index=False)

def get_alerte(df: pd.DataFrame, imc: float):
    if len(df) < 2:
        return None, None
    poids = df["poids"].tolist()
    n = min(3, len(poids))
    if n >= 2 and all(poids[i] > poids[i+1] for i in range(-n, -1)):
        return "success", "Excellent travail ! Votre poids est en baisse régulière. Continuez ainsi !"
    if len(poids) >= 2 and poids[-1] > poids[-2]:
        return "error", "Votre poids augmente depuis 2 semaines. Consultez votre médecin prochainement."
    if len(poids) >= 3:
        variation = max(poids[-3:]) - min(poids[-3:])
        if variation < 0.5:
            return "warning", "Votre poids est stable depuis 3 semaines. Pensez à varier votre activité physique."
    if len(df) >= 4 and imc >= 35:
        return "error", "Votre IMC reste critique après 1 mois de suivi. Une consultation urgente est recommandée."
    return None, None

imc                   = load_imc()
display_name, medecin = load_patient_info()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

.stApp { background-color: #0B1628; }

[data-testid="stSidebar"] {
    background-color: #0d1f35;
    border-right: 1px solid rgba(255,255,255,0.07);
}
.sidebar-logo { font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700; color: white; margin-bottom: 4px; }
.sidebar-logo span { color: #52B788; }
.sidebar-role { font-size: 0.72rem; color: rgba(255,255,255,0.35); letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 2rem; }
.user-card { background: rgba(82,183,136,0.08); border: 1px solid rgba(82,183,136,0.2); border-radius: 12px; padding: 12px 16px; margin-bottom: 2rem; }
.user-name { color: white; font-size: 0.92rem; font-weight: 500; font-family: 'DM Sans', sans-serif; }
.user-sub  { color: rgba(255,255,255,0.4); font-size: 0.75rem; margin-top: 2px; font-family: 'DM Sans', sans-serif; }
.nav-section { font-size: 0.68rem; color: rgba(255,255,255,0.25); letter-spacing: 0.12em; text-transform: uppercase; margin: 1.2rem 0 0.5rem 0; font-family: 'DM Sans', sans-serif; }
div[data-testid="stSidebar"] .stButton > button {
    background: transparent; color: rgba(255,255,255,0.65); border: none;
    border-radius: 8px; text-align: left; width: 100%;
    padding: 0.5rem 0.75rem; font-size: 0.88rem; font-family: 'DM Sans', sans-serif;
}
div[data-testid="stSidebar"] .stButton > button:hover { background: rgba(255,255,255,0.06); color: white; }

/* Bouton déconnexion — ciblé par key */
div[data-testid="stSidebar"] [data-testid="stButton"]:last-child > button {
    color: #E05252 !important;
}
div[data-testid="stSidebar"] [data-testid="stButton"]:last-child > button:hover {
    background: rgba(224,82,82,0.1) !important;
}

/* Bouton enregistrer — ciblé par key */
div[data-testid="stMain"] [data-testid="stButton"]:first-of-type > button {
    background: linear-gradient(135deg, #52B788, #3d9e70) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
}

.page-header { margin-bottom: 28px; }
.page-eyebrow { font-family: 'DM Sans', sans-serif; font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase; color: #52B788; margin-bottom: 6px; }
.page-title { font-family: 'Playfair Display', serif; font-size: 2.2rem; font-weight: 600; color: white; margin-bottom: 4px; }
.page-sub { font-family: 'DM Sans', sans-serif; font-size: 0.88rem; color: rgba(255,255,255,0.35); }

.kpi-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 20px 22px; text-align: center; position: relative; overflow: hidden; margin-bottom: 20px; }
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(to right, #52B788, #A8E6CF); }
.kpi-value { font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 600; color: white; margin-bottom: 4px; }
.kpi-label { font-family: 'DM Sans', sans-serif; font-size: 0.7rem; color: rgba(255,255,255,0.35); text-transform: uppercase; letter-spacing: 0.08em; }

.section-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 16px; padding: 28px 32px; margin-bottom: 20px; position: relative; overflow: hidden; }
.section-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(to right, #52B788, #A8E6CF); }
.section-title { font-family: 'Playfair Display', serif; font-size: 1.1rem; color: #52B788; margin-bottom: 18px; }

.alerte-success { background: rgba(82,183,136,0.12); border: 1px solid rgba(82,183,136,0.35); border-radius: 12px; padding: 14px 18px; font-family: 'DM Sans', sans-serif; font-size: 0.9rem; color: #A8E6CF; margin-bottom: 20px; }
.alerte-warning { background: rgba(244,162,97,0.12); border: 1px solid rgba(244,162,97,0.35); border-radius: 12px; padding: 14px 18px; font-family: 'DM Sans', sans-serif; font-size: 0.9rem; color: #F4C261; margin-bottom: 20px; }
.alerte-error   { background: rgba(224,82,82,0.12);  border: 1px solid rgba(224,82,82,0.35);  border-radius: 12px; padding: 14px 18px; font-family: 'DM Sans', sans-serif; font-size: 0.9rem; color: #FF9999;  margin-bottom: 20px; }

[data-testid="stNumberInput"] input { background: rgba(255,255,255,0.05) !important; border: 1.5px solid rgba(82,183,136,0.22) !important; border-radius: 10px !important; color: white !important; font-family: 'DM Sans', sans-serif !important; }

.empty-state { background: rgba(255,255,255,0.02); border: 2px dashed rgba(82,183,136,0.25); border-radius: 16px; padding: 48px; text-align: center; font-family: 'DM Sans', sans-serif; }

#MainMenu, footer { visibility: hidden; }   /* header est exclu */
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">Medi<span>Obes</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-role">Espace Patient</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="user-card">
        <div class="user-name">{display_name}</div>
        <div class="user-sub">Médecin : {medecin}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="nav-section">Navigation</div>', unsafe_allow_html=True)
    if st.button("Mon profil", use_container_width=True, key="nav_profile"):
        st.switch_page("pages/patient_profile.py")
    if st.button("Mon suivi de poids", use_container_width=True, key="nav_tracking"):
        st.switch_page("pages/patient_tracking.py")
    st.markdown("---")
    if st.button("Se déconnecter", use_container_width=True, key="logout"):
        for key in ['logged_in', 'role', 'username', 'patient_id',
                    'display_name', 'patient_nom', 'patient_prenom']:
            st.session_state.pop(key, None)
        st.switch_page("pages/home.py")

# ── Page header ─────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-eyebrow">Espace Patient · Suivi</div>
    <div class="page-title">Suivi de poids</div>
    <div class="page-sub">Enregistrez votre poids chaque semaine et suivez votre évolution</div>
</div>
""", unsafe_allow_html=True)

df = load_suivi()

if not df.empty:
    poids_actuel  = df["poids"].iloc[-1]
    poids_initial = df["poids"].iloc[0]
    variation     = poids_actuel - poids_initial
    nb_semaines   = len(df)
    imc_color = "#52B788" if imc < 25 else "#F4A261" if imc < 30 else "#E76F51" if imc < 35 else "#E05252"
    var_color = "#52B788" if variation <= 0 else "#E05252"
    var_sign  = "+" if variation > 0 else ""

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{poids_actuel:.1f}</div><div class="kpi-label">Poids actuel (kg)</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value" style="color:{var_color};">{var_sign}{variation:.1f}</div><div class="kpi-label">Variation totale (kg)</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value" style="color:{imc_color};">{imc:.1f}</div><div class="kpi-label">IMC (kg/m²)</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{nb_semaines}</div><div class="kpi-label">Semaines de suivi</div></div>', unsafe_allow_html=True)

    alerte_type, alerte_msg = get_alerte(df, imc)
    if alerte_msg:
        st.markdown(f'<div class="alerte-{alerte_type}">{alerte_msg}</div>', unsafe_allow_html=True)

# ── Saisie ──────────────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Saisir mon poids cette semaine</div>', unsafe_allow_html=True)

col_input, col_btn, _ = st.columns([1.5, 1, 3])
with col_input:
    default_poids = float(df["poids"].iloc[-1]) if not df.empty else 70.0
    poids_saisi   = st.number_input(
        "Poids (kg)", min_value=30.0, max_value=300.0,
        value=default_poids, step=0.1, format="%.1f", key="poids_input"
    )
with col_btn:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    save_btn = st.button("Enregistrer", use_container_width=True, key="save_poids")

if save_btn:
    save_poids(poids_saisi)
    st.success(f"Poids de {poids_saisi:.1f} kg enregistré pour aujourd'hui ({date.today().strftime('%d/%m/%Y')}).")
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

df = load_suivi()

if df.empty:
    st.markdown("""
    <div class="empty-state">
        <p style="font-family:'Playfair Display',serif; font-size:1.2rem; color:#52B788; margin-bottom:10px;">Aucune donnée de suivi</p>
        <p style="color:rgba(255,255,255,0.35); font-size:0.88rem;">Enregistrez votre premier poids ci-dessus.<br>Le graphique d'évolution apparaîtra ici.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Évolution du poids</div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["poids"], mode="lines+markers",
        line=dict(color="#52B788", width=2.5),
        marker=dict(size=8, color="#52B788", line=dict(color="#A8E6CF", width=1.5)),
        fill="tozeroy", fillcolor="rgba(82,183,136,0.06)",
    ))
    fig.add_hline(
        y=df["poids"].iloc[0], line_dash="dot", line_color="rgba(126,200,227,0.30)",
        annotation_text=f"Initial : {df['poids'].iloc[0]:.1f} kg",
        annotation_font_color="#7EC8E3", annotation_font_size=11,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="rgba(255,255,255,0.4)"),
        xaxis=dict(showgrid=True, gridcolor="rgba(82,183,136,0.08)", title=None),
        yaxis=dict(showgrid=True, gridcolor="rgba(82,183,136,0.08)",
                   title=dict(text="Poids (kg)", font=dict(color="rgba(255,255,255,0.4)", size=12))),
        margin=dict(l=0, r=0, t=10, b=0), height=320, showlegend=False, hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Historique des entrées</div>', unsafe_allow_html=True)
    df_display = df.copy()
    df_display["date"] = df_display["date"].dt.strftime("%d/%m/%Y")
    df_display["variation"] = df_display["poids"].diff().round(1).apply(
        lambda x: f"+{x:.1f} kg" if x > 0 else (f"{x:.1f} kg" if x < 0 else "—") if pd.notna(x) else "—"
    )
    df_display.columns = ["Date", "Poids (kg)", "Variation"]
    st.dataframe(df_display.iloc[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)