import streamlit as st
import json
import os

# ── Config globale — doit être le PREMIER appel Streamlit ─────────────────────
st.set_page_config(
    page_title="MediObes",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Masquer la navigation automatique Streamlit sur toutes les pages ──────────
st.markdown("""
<style>
    /* Cache la sidebar de navigation automatique de Streamlit */
    [data-testid="stSidebarNav"],
    div[data-testid="stSidebarNav"],
    section[data-testid="stSidebarNav"],
    .css-1d391kg, .css-1lcbmhc, .css-1wrcr25,
    .eczjsme11, .eczjsme12, .eczjsme13 {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Initialisation des fichiers de données ────────────────────────────────────
def init_data_files():
    os.makedirs("data/records", exist_ok=True)
    os.makedirs("data/tracking", exist_ok=True)

    if not os.path.exists("data/doctors.json"):
        with open("data/doctors.json", "w", encoding="utf-8") as f:
            json.dump({
                "dr.martin": {"password": "medic123", "name": "Dr. Sophie Martin"},
                "dr.hassan": {"password": "medic456", "name": "Dr. Karim Hassan"},
            }, f, indent=2, ensure_ascii=False)

    if not os.path.exists("data/patients.json"):
        with open("data/patients.json", "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)

init_data_files()

# ── Redirection vers la page d'accueil ────────────────────────────────────────
st.switch_page("pages/home.py")