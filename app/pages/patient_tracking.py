import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os
from datetime import date
from pathlib import Path

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediObes · Suivi de poids",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auth guard ─────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in") or st.session_state.get("role") != "patient":
    st.markdown("""<style>
        [data-testid="stSidebar"],[data-testid="collapsedControl"],
        header[data-testid="stHeader"]{ display:none !important; }
    </style>""", unsafe_allow_html=True)
    st.switch_page("pages/patient_login.py")

# ── Paths ──────────────────────────────────────────────────────────────────────
patient_id   = st.session_state.get("username", "")
display_name = st.session_state.get("display_name", "Patient")
TRACKING_DIR = Path("data/tracking")
RECORDS_DIR  = Path("data/records")
TRACKING_DIR.mkdir(parents=True, exist_ok=True)

def tracking_path():
    return TRACKING_DIR / f"{patient_id}.csv"

# ── Load IMC from record ───────────────────────────────────────────────────────
def load_imc():
    path = RECORDS_DIR / f"{patient_id}.json"
    if not path.exists():
        return 0.0
    try:
        with open(path, "r") as f:
            record = json.load(f)
        return float(record.get("BMI", 0))
    except Exception:
        return 0.0

imc = load_imc()

# ── CSV helpers ────────────────────────────────────────────────────────────────
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
    path = tracking_path()
    today_str = date.today().isoformat()
    new_row = pd.DataFrame([{"date": today_str, "poids": poids}])
    if path.exists():
        df = pd.read_csv(path)
        df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)
        df = df[df["date"] != today_str]   # évite doublon même jour
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
    df.to_csv(path, index=False)

# ── Alerte logic ───────────────────────────────────────────────────────────────
def get_alerte(df: pd.DataFrame, imc: float):
    if len(df) < 2:
        return None, None
    poids = df["poids"].tolist()

    # Baisse régulière ≥ 2 entrées
    n = min(3, len(poids))
    if n >= 2 and all(poids[i] > poids[i+1] for i in range(-n, -1)):
        return "success", "💪 Excellent travail ! Votre poids est en baisse régulière. Continuez ainsi !"

    # Hausse 2 entrées consécutives (priorité sur stable)
    if len(poids) >= 2 and poids[-1] > poids[-2]:
        return "error", "⚠️ Votre poids augmente depuis 2 semaines. Consultez votre médecin prochainement."

    # Stable ≥ 3 entrées (variation < 0.5 kg)
    if len(poids) >= 3:
        variation = max(poids[-3:]) - min(poids[-3:])
        if variation < 0.5:
            return "warning", "🏃 Votre poids est stable depuis 3 semaines. Pensez à varier votre activité physique."

    # IMC critique après 4 entrées
    if len(df) >= 4 and imc >= 35:
        return "error", "🚨 Votre IMC reste critique après 1 mois de suivi. Une consultation urgente est recommandée."

    return None, None

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
        radial-gradient(ellipse at 10% 30%, rgba(82,183,136,0.12) 0%, transparent 55%),
        radial-gradient(ellipse at 90% 70%, rgba(82,183,136,0.06) 0%, transparent 50%);
    pointer-events: none; z-index: 0;
}
[data-testid="stMain"] { position: relative; z-index: 1; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: #0D1E30 !important; border-right: 1px solid rgba(82,183,136,0.12) !important; }
[data-testid="stSidebar"] * { color: #3A7A5A !important; }
[data-testid="stSidebar"] hr { border-color: rgba(82,183,136,0.12) !important; margin: 14px 0; }
.sb-logo { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 600; color: #FFFFFF !important; letter-spacing: -0.3px; margin-bottom: 2px; }
.sb-logo span { color: transparent; background: linear-gradient(135deg,#52B788,#A8E6CF); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.sb-tagline { font-size: 11px; color: #1A3A2A !important; margin-bottom: 20px; }
.sb-user { background: rgba(82,183,136,0.10); border: 1px solid rgba(82,183,136,0.20); border-radius: 12px; padding: 12px 14px; margin-bottom: 4px; }
.sb-user-name { font-size: 13.5px; font-weight: 500; color: #FFFFFF !important; }
.sb-user-role { font-size: 11px; color: #52B788 !important; margin-top: 2px; }
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: rgba(82,183,136,0.10) !important; color: #3A7A5A !important;
    border: 1px solid rgba(82,183,136,0.20) !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 13px !important; box-shadow: none !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: rgba(82,183,136,0.20) !important; color: #A8E6CF !important; transform: none !important;
}

/* ── Page header ── */
.page-header { margin-bottom: 28px; }
.page-eyebrow { font-size: 11px; font-weight: 500; letter-spacing: 1.5px; text-transform: uppercase; color: #1A4A3A; margin-bottom: 6px; }
.page-title { font-family: 'Playfair Display', serif; font-size: 34px; font-weight: 600; color: #FFFFFF; letter-spacing: -0.8px; margin-bottom: 4px; }
.page-sub { font-size: 14px; color: #1A3A2A; font-weight: 300; }

/* ── KPI cards ── */
.kpi-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 20px 22px; text-align: center; position: relative; overflow: hidden;
    margin-bottom: 20px;
}
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(to right, #52B788, #A8E6CF);
}
.kpi-value { font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 600; color: #FFFFFF; margin-bottom: 4px; }
.kpi-label { font-size: 11px; color: #1A4A3A; text-transform: uppercase; letter-spacing: 0.8px; }

/* ── Section card ── */
.section-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 28px 32px; margin-bottom: 20px;
    position: relative; overflow: hidden;
}
.section-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(to right, #52B788, #A8E6CF);
}
.section-title {
    font-family: 'Playfair Display', serif; font-size: 17px; color: #52B788; margin-bottom: 18px;
    display: flex; align-items: center; gap: 8px;
}
.section-title::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(to right, rgba(82,183,136,0.3), transparent); margin-left: 8px;
}

/* ── Alerte boxes ── */
.alerte-success { background: rgba(82,183,136,0.12); border: 1px solid rgba(82,183,136,0.35); border-radius: 12px; padding: 14px 18px; font-size: 14px; color: #A8E6CF; margin-bottom: 20px; }
.alerte-warning { background: rgba(244,162,97,0.12); border: 1px solid rgba(244,162,97,0.35); border-radius: 12px; padding: 14px 18px; font-size: 14px; color: #F4C261; margin-bottom: 20px; }
.alerte-error   { background: rgba(224,82,82,0.12);  border: 1px solid rgba(224,82,82,0.35);  border-radius: 12px; padding: 14px 18px; font-size: 14px; color: #FF9999;  margin-bottom: 20px; }

/* ── Number input ── */
[data-testid="stNumberInput"] label { color: #3A7A5A !important; font-size: 13px !important; }
[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,0.05) !important;
    border: 1.5px solid rgba(82,183,136,0.22) !important;
    border-radius: 10px !important; color: #FFFFFF !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 15px !important;
}
[data-testid="stNumberInput"] input:focus {
    border-color: #52B788 !important; box-shadow: 0 0 0 3px rgba(82,183,136,0.12) !important;
}

/* ── Save button ── */
.save-btn [data-testid="stButton"] > button {
    background: linear-gradient(135deg, #52B788, #3d9e70) !important;
    color: #FFFFFF !important; border: none !important; border-radius: 10px !important;
    padding: 13px 0 !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 14.5px !important; font-weight: 500 !important;
    box-shadow: 0 4px 16px rgba(82,183,136,0.28) !important;
}
.save-btn [data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important; box-shadow: 0 8px 24px rgba(82,183,136,0.38) !important;
}

/* ── Empty state ── */
.empty-state {
    background: rgba(255,255,255,0.02); border: 2px dashed rgba(82,183,136,0.25);
    border-radius: 16px; padding: 48px; text-align: center;
}
.empty-title { font-family: 'Playfair Display', serif; font-size: 20px; color: #52B788; margin-bottom: 10px; }
.empty-sub { font-size: 13.5px; color: #1A4A3A; line-height: 1.7; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">Medi<span>Obes</span></div>
    <div class="sb-tagline">Espace Patient</div>
    <hr>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sb-user">
        <div class="sb-user-name">👤 {display_name}</div>
        <div class="sb-user-role">● Patient connecté</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.page_link("pages/patient_profile.py",  label="📊  Mon profil")
    st.page_link("pages/patient_tracking.py", label="📈  Suivi de poids")
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("🚪  Se déconnecter", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/home.py")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-eyebrow">Espace Patient · Suivi</div>
    <div class="page-title">Suivi de poids</div>
    <div class="page-sub">Enregistrez votre poids chaque semaine et suivez votre évolution</div>
</div>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────────
df = load_suivi()

# ── KPIs ──────────────────────────────────────────────────────────────────────
if not df.empty:
    poids_actuel  = df["poids"].iloc[-1]
    poids_initial = df["poids"].iloc[0]
    variation     = poids_actuel - poids_initial
    nb_semaines   = len(df)
    imc_color     = "#52B788" if imc < 25 else "#F4A261" if imc < 30 else "#E76F51" if imc < 35 else "#E05252"
    var_color     = "#52B788" if variation <= 0 else "#E05252"
    var_sign      = "+" if variation > 0 else ""

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-value">{poids_actuel:.1f}</div>
            <div class="kpi-label">Poids actuel (kg)</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-value" style="color:{var_color};">{var_sign}{variation:.1f}</div>
            <div class="kpi-label">Variation totale (kg)</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-value" style="color:{imc_color};">{imc:.1f}</div>
            <div class="kpi-label">IMC (kg/m²)</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-value">{nb_semaines}</div>
            <div class="kpi-label">Semaines de suivi</div>
        </div>""", unsafe_allow_html=True)

    # ── Alerte ────────────────────────────────────────────────────────────────
    alerte_type, alerte_msg = get_alerte(df, imc)
    if alerte_msg:
        st.markdown(f'<div class="alerte-{alerte_type}">{alerte_msg}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SAISIE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">⚖️ &nbsp;Saisir mon poids cette semaine</div>', unsafe_allow_html=True)

col_input, col_btn, _ = st.columns([1.5, 1, 3])
with col_input:
    default_poids = float(df["poids"].iloc[-1]) if not df.empty else 70.0
    poids_saisi = st.number_input(
        "Poids (kg)", min_value=30.0, max_value=300.0,
        value=default_poids, step=0.1, format="%.1f",
    )
with col_btn:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="save-btn">', unsafe_allow_html=True)
    save_btn = st.button("💾  Enregistrer", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

if save_btn:
    save_poids(poids_saisi)
    st.success(f"✅ Poids de {poids_saisi:.1f} kg enregistré pour aujourd'hui ({date.today().strftime('%d/%m/%Y')}).")
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# GRAPHIQUE + HISTORIQUE
# ══════════════════════════════════════════════════════════════════════════════
df = load_suivi()   # recharger après éventuel save

if df.empty:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-title">📭 Aucune donnée de suivi</div>
        <div class="empty-sub">Enregistrez votre premier poids ci-dessus.<br>
        Le graphique d'évolution apparaîtra ici.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    # ── Graphique ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 &nbsp;Évolution du poids</div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["poids"],
        mode="lines+markers",
        name="Poids",
        line=dict(color="#52B788", width=2.5),
        marker=dict(size=8, color="#52B788", line=dict(color="#A8E6CF", width=1.5)),
        fill="tozeroy",
        fillcolor="rgba(82,183,136,0.06)",
    ))
    fig.add_hline(
        y=df["poids"].iloc[0],
        line_dash="dot", line_color="rgba(126,200,227,0.30)",
        annotation_text=f"Initial : {df['poids'].iloc[0]:.1f} kg",
        annotation_font_color="#7EC8E3", annotation_font_size=11,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#4A7A6A"),
        xaxis=dict(showgrid=True, gridcolor="rgba(82,183,136,0.08)", tickfont=dict(color="#3A7A5A", size=11), title=None),
        yaxis=dict(showgrid=True, gridcolor="rgba(82,183,136,0.08)", tickfont=dict(color="#3A7A5A", size=11), title="Poids (kg)", titlefont=dict(color="#3A7A5A", size=12)),
        margin=dict(l=0, r=0, t=10, b=0),
        height=320, showlegend=False, hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Historique ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📅 &nbsp;Historique des entrées</div>', unsafe_allow_html=True)

    df_display = df.copy()
    df_display["date"]      = df_display["date"].dt.strftime("%d/%m/%Y")
    df_display["variation"] = df_display["poids"].diff().round(1).apply(
        lambda x: f"+{x:.1f} kg" if x > 0 else (f"{x:.1f} kg" if x < 0 else "—") if pd.notna(x) else "—"
    )
    df_display.columns = ["Date", "Poids (kg)", "Variation"]
    st.dataframe(df_display.iloc[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)