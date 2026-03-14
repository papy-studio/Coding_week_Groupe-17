import streamlit as st
import json
import os
from pathlib import Path
 
# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediObes · Médecin",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed",
)
 
# ── Hide sidebar & header ──────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
header[data-testid="stHeader"] { display: none !important; }
</style>
""", unsafe_allow_html=True)
 
# ── Chemins absolus ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCTORS_PATH = BASE_DIR / "data" / "doctors.json"
 
def load_doctors():
    if not DOCTORS_PATH.exists():
        DOCTORS_PATH.parent.mkdir(parents=True, exist_ok=True)
        default = {
            "dr.martin": {"password": "medic123", "name": "Dr. Sophie Martin"},
            "dr.hassan": {"password": "medic456", "name": "Dr. Karim Hassan"},
        }
        with open(DOCTORS_PATH, "w") as f:
            json.dump(default, f, indent=2, ensure_ascii=False)
        return default
    try:
        with open(DOCTORS_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        default = {
            "dr.martin": {"password": "medic123", "name": "Dr. Sophie Martin"},
            "dr.hassan": {"password": "medic456", "name": "Dr. Karim Hassan"},
        }
        with open(DOCTORS_PATH, "w") as f:
            json.dump(default, f, indent=2, ensure_ascii=False)
        return default
 
DOCTORS = load_doctors()
 
# ── Redirect if already logged in as doctor ───────────────────────────────────
if st.session_state.get("role") == "doctor":
    st.switch_page("pages/doctor_dashboard.py")
 
# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap');
 
html, body { margin: 0; padding: 0; }
 
[data-testid="stAppViewContainer"] {
    min-height: 100vh;
    font-family: 'DM Sans', sans-serif;
    background: #0B1628;
}
 
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse at 15% 50%, rgba(29,105,150,0.20) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 20%, rgba(29,105,150,0.10) 0%, transparent 50%);
    pointer-events: none; z-index: 0;
}
[data-testid="stMain"] { position: relative; z-index: 1; }
[data-testid="block-container"] { padding-top: 0 !important; }
 
.login-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 52px 48px 44px;
    max-width: 420px;
    margin: 60px auto 0;
    box-shadow:
        0 0 0 1px rgba(29,105,150,0.10),
        0 24px 64px rgba(0,0,0,0.40);
    animation: rise 0.55s cubic-bezier(.22,1,.36,1) both;
    position: relative;
    overflow: hidden;
}
 
.login-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(to right, #1D6996, #7EC8E3);
}
 
@keyframes rise {
    from { opacity: 0; transform: translateY(28px); }
    to   { opacity: 1; transform: translateY(0); }
}
 
.card-icon-wrap {
    width: 52px; height: 52px;
    background: rgba(29,105,150,0.20);
    border: 1px solid rgba(29,105,150,0.30);
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px;
    margin-bottom: 20px;
}
 
.card-role-tag {
    font-size: 10.5px; font-weight: 500;
    letter-spacing: 1.5px; text-transform: uppercase;
    color: #4A9EC0; margin-bottom: 6px;
}
 
.card-title {
    font-family: 'Playfair Display', serif;
    font-size: 30px; font-weight: 600;
    color: #FFFFFF; letter-spacing: -0.5px;
    margin-bottom: 6px;
}
 
.card-subtitle {
    font-size: 13px; color: #2A4A5A;
    font-weight: 300; margin-bottom: 36px;
}
 
.divider {
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(29,105,150,0.25), transparent);
    margin-bottom: 32px;
}
 
.field-label {
    font-size: 11.5px; font-weight: 500;
    color: #2A5A7A; text-transform: uppercase;
    letter-spacing: 0.6px; margin-bottom: 6px;
}
 
[data-testid="stTextInput"] label { display: none; }
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.05) !important;
    border: 1.5px solid rgba(29,105,150,0.25) !important;
    border-radius: 10px !important;
    padding: 12px 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    color: #FFFFFF !important;
    transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
}
[data-testid="stTextInput"] input::placeholder { color: #2A4A5A !important; }
[data-testid="stTextInput"] input:focus {
    border-color: #1D6996 !important;
    background: rgba(29,105,150,0.10) !important;
    box-shadow: 0 0 0 3px rgba(29,105,150,0.15) !important;
}
 
[data-testid="stButton"] > button {
    width: 100%;
    background: linear-gradient(135deg, #1D6996, #155a7a) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 13px 0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    letter-spacing: 0.2px;
    box-shadow: 0 4px 20px rgba(29,105,150,0.35) !important;
    transition: transform 0.15s, box-shadow 0.15s;
    margin-top: 8px;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 28px rgba(29,105,150,0.45) !important;
}
 
[data-testid="stAlert"] { border-radius: 10px !important; font-size: 13.5px !important; }
 
.card-footer {
    text-align: center;
    margin-top: 28px;
    font-size: 11.5px;
    color: #1A3040;
    line-height: 1.6;
}
 
.register-link {
    text-align: center;
    margin-top: 20px;
    font-size: 13px;
    color: #2A5A7A;
}
</style>
""", unsafe_allow_html=True)
 
# ── Back to home ──────────────────────────────────────────────────────────────
_, col, _ = st.columns([0.5, 3, 0.5])
with col:
    if st.button("← Retour à l'accueil", key="back_home"):
        st.switch_page("pages/home.py")
 
# ── Card header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="login-card">
    <div class="card-icon-wrap">🩺</div>
    <div class="card-role-tag">Personnel médical</div>
    <div class="card-title">Connexion<br>Médecin</div>
    <div class="card-subtitle">Accès réservé au personnel médical autorisé</div>
    <div class="divider"></div>
</div>
""", unsafe_allow_html=True)
 
# ── Form ──────────────────────────────────────────────────────────────────────
_, col, _ = st.columns([0.5, 3, 0.5])
 
with col:
    st.markdown('<div class="field-label">Identifiant</div>', unsafe_allow_html=True)
    username = st.text_input("doc_username", placeholder="ex: dr.martin", label_visibility="collapsed")
 
    st.markdown('<div class="field-label" style="margin-top:16px;">Mot de passe</div>', unsafe_allow_html=True)
    password = st.text_input("doc_password", type="password", placeholder="••••••••", label_visibility="collapsed")
 
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
 
    login_btn = st.button("Se connecter", use_container_width=True, key="login_btn")
 
    # ── Auth logic ────────────────────────────────────────────────────────────
    if login_btn:
        if not username.strip() or not password.strip():
            st.error("Veuillez remplir tous les champs.")
        elif username in DOCTORS and DOCTORS[username]["password"] == password:
            st.session_state["logged_in"]    = True
            st.session_state["role"]         = "doctor"
            st.session_state["username"]     = username
            st.session_state["display_name"] = DOCTORS[username]["name"]
            st.success(f"Bienvenue, {DOCTORS[username]['name']} !")
            st.switch_page("pages/doctor_dashboard.py")
        else:
            st.error("Identifiant ou mot de passe incorrect.")
 
    # ── ✅ Lien inscription — dans la même colonne, avec un vrai bouton ───────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='register-link'>Pas encore de compte ?</div>",
        unsafe_allow_html=True
    )
    if st.button("📝 S'inscrire", use_container_width=True, key="register_btn"):
        st.switch_page("pages/doctor-register.py")
 
    st.markdown("""
    <div class="card-footer">
        © 2026 MediObes · Centrale Casablanca<br>
        Toutes les données sont confidentielles
    </div>
    """, unsafe_allow_html=True)