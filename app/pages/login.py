import streamlit as st

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ObesityRisk · Login",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Hardcoded users (replace with DB in production) ────────────────────────────
USERS = {
    "dr.martin": {"password": "medic123", "name": "Dr. Sophie Martin"},
    "dr.hassan": {"password": "medic456", "name": "Dr. Karim Hassan"},
    "admin":     {"password": "admin000", "name": "Administrateur"},
}

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #EEF2F7;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse at 20% 50%, rgba(29,105,150,0.08) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(82,183,136,0.07) 0%, transparent 55%),
        #EEF2F7;
}

/* ── Hide sidebar completely ── */
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
button[kind="header"] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
}

/* hide top header bar */
header[data-testid="stHeader"] { display: none !important; }

/* ── card ── */
.login-card {
    background: #FFFFFF;
    border-radius: 20px;
    padding: 52px 48px 44px;
    box-shadow:
        0 1px 3px rgba(0,0,0,0.04),
        0 8px 32px rgba(29,105,150,0.10),
        0 0 0 1px rgba(29,105,150,0.06);
    max-width: 420px;
    margin: 80px auto 0;
    animation: rise 0.5s cubic-bezier(.22,1,.36,1) both;
}

@keyframes rise {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}

.logo-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 6px;
}

.logo-icon {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, #1D6996 0%, #52B788 100%);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    box-shadow: 0 4px 12px rgba(29,105,150,0.25);
}

.app-name {
    font-family: 'DM Serif Display', serif;
    font-size: 24px;
    color: #1A2B3C;
    letter-spacing: -0.3px;
}
.app-name span { color: #1D6996; }

.tagline {
    font-size: 13px;
    color: #8A9BB0;
    margin-bottom: 36px;
    font-weight: 300;
    letter-spacing: 0.2px;
}

.field-label {
    font-size: 12.5px;
    font-weight: 500;
    color: #4A5A6A;
    margin-bottom: 6px;
    letter-spacing: 0.4px;
    text-transform: uppercase;
}

[data-testid="stTextInput"] input {
    border: 1.5px solid #DDE3EC !important;
    border-radius: 10px !important;
    padding: 11px 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14.5px !important;
    color: #1A2B3C !important;
    background: #FAFBFD !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
[data-testid="stTextInput"] input:focus {
    border-color: #1D6996 !important;
    box-shadow: 0 0 0 3px rgba(29,105,150,0.12) !important;
    background: #FFFFFF !important;
}

[data-testid="stButton"] > button {
    width: 100%;
    background: linear-gradient(135deg, #1D6996 0%, #1a5f87 100%);
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 13px 0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    cursor: pointer;
    box-shadow: 0 4px 14px rgba(29,105,150,0.30);
    margin-top: 8px;
    transition: transform 0.15s, box-shadow 0.15s;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(29,105,150,0.38);
}

[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 13.5px !important;
}

.login-footer {
    text-align: center;
    margin-top: 28px;
    font-size: 12px;
    color: #B0BCCC;
    letter-spacing: 0.2px;
}

.divider {
    height: 1px;
    background: linear-gradient(to right, transparent, #DDE3EC, transparent);
    margin: 28px 0;
}

[data-testid="stTextInput"] label { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Redirect if already logged in ─────────────────────────────────────────────
if st.session_state.get("logged_in"):
    st.switch_page("pages/data_entry.py")

# ── Card header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="login-card">
    <div class="logo-row">
        <div class="logo-icon">🩺</div>
        <div class="app-name">Obesity<span>Risk</span></div>
    </div>
    <div class="tagline">Outil d'aide à la décision clinique · Centrale Casablanca</div>
    <div class="divider"></div>
</div>
""", unsafe_allow_html=True)

# ── Form ──────────────────────────────────────────────────────────────────────
_, col, _ = st.columns([0.5, 3, 0.5])

with col:
    st.markdown('<div class="field-label">Identifiant</div>', unsafe_allow_html=True)
    username = st.text_input("username", placeholder="ex: dr.martin", label_visibility="collapsed")

    st.markdown('<div class="field-label" style="margin-top:16px;">Mot de passe</div>', unsafe_allow_html=True)
    password = st.text_input("password", type="password", placeholder="••••••••", label_visibility="collapsed")

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    login_btn = st.button("Se connecter", use_container_width=True)

    if login_btn:
        if not username or not password:
            st.error("Veuillez remplir tous les champs.")
        elif username in USERS and USERS[username]["password"] == password:
            st.session_state["logged_in"]    = True
            st.session_state["username"]     = username
            st.session_state["display_name"] = USERS[username]["name"]
            st.success(f"Bienvenue, {USERS[username]['name']} !")
            st.switch_page("pages/data_entry.py")
        else:
            st.error("Identifiant ou mot de passe incorrect.")

    st.markdown("""
    <div class="login-footer">
        © 2026 Centrale Casablanca · Coding Week<br>
        Accès réservé au personnel médical autorisé
    </div>
    """, unsafe_allow_html=True)
