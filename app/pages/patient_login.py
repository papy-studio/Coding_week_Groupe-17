import streamlit as st
import json
from pathlib import Path
 
st.set_page_config(page_title="Connexion Patient", page_icon="👤")
 
# Design system
st.markdown("""
<style>
    .stApp { background-color: #0B1628; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; color: white; }
    .stButton > button {
        background-color: #52B788;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-family: 'DM Sans', sans-serif;
        width: 100%;
    }
    .stButton > button:hover { background-color: #3d8c6a; }
    .stTextInput > div > div > input {
        background-color: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        color: white;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)
 
st.title("👤 Espace Patient")
st.markdown("Connectez-vous pour accéder à votre espace personnel")
 
# ✅ Chemin absolu basé sur la position du fichier
# __file__ = app/pages/patient_login.py
# .parent   = app/pages/
# .parent   = app/
# .parent   = Coding_week_Groupe-17/  (racine du projet)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
patients_file = BASE_DIR / "data" / "patients.json"
 
# Vérifier si la base de données patients existe
if not patients_file.exists():
    st.warning("""
    ### ⚠️ Base de données en cours d'initialisation
    L'espace patient sera bientôt disponible. 
    Veuillez réessayer dans quelques instants.
    """)
    st.stop()
 
# Formulaire de connexion
with st.form("login_form"):
    username = st.text_input("Nom d'utilisateur", placeholder="ex: patient001")
    password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
    submitted = st.form_submit_button("Se connecter")
 
    if submitted:
        if not username or not password:
            st.error("Veuillez remplir tous les champs")
        else:
            try:
                with open(patients_file, 'r', encoding='utf-8') as f:
                    patients = json.load(f)
 
                if username in patients and patients[username]["password"] == password:
                    patient_info = patients[username]
 
                    # Sauvegarder dans session_state
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = "patient"
                    st.session_state["username"] = username
                    st.session_state["patient_id"] = username
                    st.session_state["display_name"] = f"{patient_info.get('prenom', '')} {patient_info.get('nom', '')}"
                    st.session_state["patient_nom"] = patient_info.get('nom', '')
                    st.session_state["patient_prenom"] = patient_info.get('prenom', '')
                    st.session_state["patient_taille"] = patient_info.get('taille')
                    st.session_state["medecin_referent"] = patient_info.get('medecin_referent')
 
                    st.success(f"Bienvenue, {st.session_state['display_name']} !")
                    # ✅ Chemin correct pour switch_page depuis app/pages/
                    st.switch_page("pages/patient_profile.py")
                else:
                    st.error("❌ Nom d'utilisateur ou mot de passe incorrect")
 
            except json.JSONDecodeError:
                st.error("❌ Erreur de lecture de la base de données. Fichier JSON invalide.")
            except Exception as e:
                st.error(f"Erreur de connexion : {str(e)}")
 
# Pied de page
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>"
    "© 2026 MediObes - Application clinique d'aide à la décision"
    "</p>",
    unsafe_allow_html=True
)