import streamlit as st

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ObesityRisk · Nouveau Patient",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auth guard — must be BEFORE any rendering ──────────────────────────────────
if not st.session_state.get("logged_in"):
    st.markdown("""
    <style>
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"],
        header[data-testid="stHeader"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    st.switch_page("pages/login.py")

# ── CSS (only rendered if logged in) ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #EEF2F7;
}
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse at 20% 50%, rgba(29,105,150,0.06) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(82,183,136,0.05) 0%, transparent 55%),
        #EEF2F7;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #1A2B3C !important;
    border-right: none;
}
[data-testid="stSidebar"] * { color: #C8D8E8 !important; }
[data-testid="stSidebar"] .sidebar-title {
    font-family: 'DM Serif Display', serif;
    font-size: 20px;
    color: #FFFFFF !important;
    padding: 8px 0 4px;
}
[data-testid="stSidebar"] .sidebar-sub {
    font-size: 12px;
    color: #6A8AA0 !important;
    margin-bottom: 24px;
}
[data-testid="stSidebar"] hr { border-color: #2A3F54 !important; margin: 16px 0; }
[data-testid="stSidebar"] .user-badge {
    background: #243448;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 8px;
}
[data-testid="stSidebar"] .user-name {
    font-size: 14px; font-weight: 500; color: #FFFFFF !important;
}
[data-testid="stSidebar"] .user-role {
    font-size: 11px; color: #52B788 !important;
}

/* ── Page header ── */
.page-header { margin-bottom: 32px; animation: fadein 0.4s ease both; }
.page-title {
    font-family: 'DM Serif Display', serif;
    font-size: 30px; color: #1A2B3C; letter-spacing: -0.5px; margin-bottom: 4px;
}
.page-sub { font-size: 14px; color: #7A8EA0; font-weight: 300; }

/* ── Section cards ── */
.section-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(29,105,150,0.07);
    animation: fadein 0.45s ease both;
}
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 17px; color: #1D6996; margin-bottom: 20px;
    display: flex; align-items: center; gap: 8px;
}
.section-title::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(to right, #DDE3EC, transparent);
    margin-left: 8px;
}

/* ── Labels ── */
.field-label {
    font-size: 12px; font-weight: 500; color: #5A6A7A;
    text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;
}
.req { color: #E05252; margin-left: 2px; }

/* ── Submit button ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #1D6996 0%, #1a5f87 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 13px 32px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    box-shadow: 0 4px 14px rgba(29,105,150,0.28);
    transition: transform 0.15s, box-shadow 0.15s;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(29,105,150,0.36);
}

/* ── Tip box ── */
.tip-box {
    background: #F0F8FF;
    border-left: 3px solid #1D6996;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    font-size: 13px; color: #3A6A8A; margin-bottom: 24px;
}

@keyframes fadein {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-title">🩺 ObesityRisk</div>
    <div class="sidebar-sub">Outil d'aide à la décision clinique</div>
    <hr>
    """, unsafe_allow_html=True)

    display_name = st.session_state.get("display_name", "Médecin")
    st.markdown(f"""
    <div class="user-badge">
        <div class="user-name">👤 {display_name}</div>
        <div class="user-role">● Connecté</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.page_link("pages/data_entry.py", label="📋 Nouveau patient")
    st.page_link("pages/patients.py",   label="🗂️ Inventaire patients")
    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("🚪 Se déconnecter", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/login.py")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-title">Nouveau Patient</div>
    <div class="page-sub">Remplissez les informations ci-dessous pour estimer le risque d'obésité</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="tip-box">
    💡 Tous les champs marqués <span style="color:#E05252">*</span> sont obligatoires.
    Les données seront sauvegardées après analyse.
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Informations générales
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">👤 &nbsp;Informations générales</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="field-label">Prénom <span class="req">*</span></div>', unsafe_allow_html=True)
    first_name = st.text_input("prenom", placeholder="Prénom du patient", label_visibility="collapsed")
with col2:
    st.markdown('<div class="field-label">Nom <span class="req">*</span></div>', unsafe_allow_html=True)
    last_name = st.text_input("nom", placeholder="Nom du patient", label_visibility="collapsed")
with col3:
    st.markdown('<div class="field-label">Sexe <span class="req">*</span></div>', unsafe_allow_html=True)
    gender = st.selectbox("sexe", ["Homme", "Femme"], label_visibility="collapsed")

col4, col5, col6 = st.columns(3)
with col4:
    st.markdown('<div class="field-label">Âge (ans) <span class="req">*</span></div>', unsafe_allow_html=True)
    age = st.number_input("age", min_value=10, max_value=100, value=30, step=1, label_visibility="collapsed")
with col5:
    st.markdown('<div class="field-label">Taille (m) <span class="req">*</span></div>', unsafe_allow_html=True)
    height = st.number_input("taille", min_value=1.40, max_value=2.20, value=1.70, step=0.01, format="%.2f", label_visibility="collapsed")
with col6:
    st.markdown('<div class="field-label">Poids (kg) <span class="req">*</span></div>', unsafe_allow_html=True)
    weight = st.number_input("poids", min_value=30.0, max_value=200.0, value=70.0, step=0.5, format="%.1f", label_visibility="collapsed")

# IMC en temps réel
if height > 0:
    bmi = weight / (height ** 2)
    bmi_color = "#52B788" if bmi < 25 else "#F4A261" if bmi < 30 else "#E05252"
    st.markdown(f"""
    <div style="margin-top:12px; padding:10px 16px; background:#F7FAFC; border-radius:8px;
                display:inline-block; font-size:13.5px; color:#3A5A7A;">
        IMC calculé : <strong style="color:{bmi_color}; font-size:16px;">{bmi:.1f}</strong> kg/m²
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Habitudes alimentaires
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🍽️ &nbsp;Antécédents & habitudes alimentaires</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="field-label">Antécédents familiaux d\'obésité <span class="req">*</span></div>', unsafe_allow_html=True)
    family_history = st.selectbox("family", ["Oui", "Non"], label_visibility="collapsed")

    st.markdown('<div class="field-label" style="margin-top:16px;">Consommation fréquente d\'aliments caloriques (FAVC) <span class="req">*</span></div>', unsafe_allow_html=True)
    favc = st.selectbox("favc", ["Oui", "Non"], label_visibility="collapsed")

    st.markdown('<div class="field-label" style="margin-top:16px;">Consommation de légumes par repas (FCVC)</div>', unsafe_allow_html=True)
    st.caption("1 = Jamais · 2 = Parfois · 3 = Toujours")
    fcvc = st.slider("fcvc", 1.0, 3.0, 2.0, 0.1, label_visibility="collapsed")

with col2:
    st.markdown('<div class="field-label">Nombre de repas principaux par jour (NCP) <span class="req">*</span></div>', unsafe_allow_html=True)
    ncp = st.slider("ncp", 1.0, 4.0, 3.0, 0.1, label_visibility="collapsed")

    st.markdown('<div class="field-label" style="margin-top:16px;">Grignotage entre les repas (CAEC)</div>', unsafe_allow_html=True)
    caec = st.selectbox("caec", ["Non", "Parfois", "Fréquemment", "Toujours"], label_visibility="collapsed")

    st.markdown('<div class="field-label" style="margin-top:16px;">Surveillance des apports caloriques (SCC)</div>', unsafe_allow_html=True)
    scc = st.selectbox("scc", ["Oui", "Non"], label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Hygiène de vie
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🏃 &nbsp;Hygiène de vie</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="field-label">Tabagisme</div>', unsafe_allow_html=True)
    smoke = st.selectbox("smoke", ["Non", "Oui"], label_visibility="collapsed")

    st.markdown('<div class="field-label" style="margin-top:16px;">Consommation d\'eau par jour (CH2O)</div>', unsafe_allow_html=True)
    st.caption("1 = Moins d'1L · 2 = Entre 1 et 2L · 3 = Plus de 2L")
    ch2o = st.slider("ch2o", 1.0, 3.0, 2.0, 0.1, label_visibility="collapsed")

    st.markdown('<div class="field-label" style="margin-top:16px;">Activité physique (FAF)</div>', unsafe_allow_html=True)
    st.caption("0 = Aucune · 1 = 1-2j/sem · 2 = 3-4j/sem · 3 = Quotidien")
    faf = st.slider("faf", 0.0, 3.0, 1.0, 0.1, label_visibility="collapsed")

with col2:
    st.markdown('<div class="field-label">Temps passé sur écrans (TUE)</div>', unsafe_allow_html=True)
    st.caption("0 = 0-2h · 1 = 3-5h · 2 = Plus de 5h")
    tue = st.slider("tue", 0.0, 2.0, 1.0, 0.1, label_visibility="collapsed")

    st.markdown('<div class="field-label" style="margin-top:16px;">Consommation d\'alcool (CALC)</div>', unsafe_allow_html=True)
    calc = st.selectbox("calc", ["Non", "Parfois", "Fréquemment", "Toujours"], label_visibility="collapsed")

    st.markdown('<div class="field-label" style="margin-top:16px;">Moyen de transport principal (MTRANS)</div>', unsafe_allow_html=True)
    mtrans = st.selectbox(
        "mtrans",
        ["Transports en commun", "Voiture", "Vélo", "Moto", "À pied"],
        label_visibility="collapsed"
    )

st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SUBMIT
# ══════════════════════════════════════════════════════════════════════════════
col_btn, _ = st.columns([2, 5])
with col_btn:
    submit = st.button("🔍 Analyser le patient", use_container_width=True)

if submit:
    if not first_name.strip() or not last_name.strip():
        st.error("⚠️ Le prénom et le nom du patient sont obligatoires.")
    else:
        caec_map   = {"Non": 0, "Parfois": 1, "Fréquemment": 2, "Toujours": 3}
        calc_map   = {"Non": 0, "Parfois": 1, "Fréquemment": 2, "Toujours": 3}
        mtrans_map = {
            "Voiture": 0, "Vélo": 1, "Moto": 2,
            "Transports en commun": 3, "À pied": 4
        }

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

        st.success(f"✅ Données enregistrées pour {first_name} {last_name}. Redirection en cours…")
        st.switch_page("pages/result.py")
