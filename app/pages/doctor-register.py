# app/pages/doctor_register.py
import streamlit as st
import json
from pathlib import Path
import re

st.set_page_config(page_title="Inscription Médecin", page_icon="👨‍⚕️")

# Design system (identique au login)
st.markdown("""
<style>
    .stApp { background-color: #0B1628; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; color: white; }
    .stButton > button {
        background-color: #1D6996;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-family: 'DM Sans', sans-serif;
        width: 100%;
    }
    .stTextInput > div > div > input {
        background-color: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        color: white;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("👨‍⚕️ Inscription Médecin")
st.markdown("Créez votre compte pour accéder à l'espace médecin.")

doctors_file = Path("data/doctors.json")

with st.form("register_form"):
    username = st.text_input("Identifiant (ex: dr.dupont) *")
    password = st.text_input("Mot de passe *", type="password")
    confirm = st.text_input("Confirmer le mot de passe *", type="password")
    name = st.text_input("Nom complet (ex: Dr. Jean Dupont) *")
    specialite = st.text_input("Spécialité")
    email = st.text_input("Email")
    telephone = st.text_input("Téléphone")

    submitted = st.form_submit_button("S'inscrire")

    if submitted:
        # Validations simples
        if not username or not password or not name:
            st.error("Veuillez remplir tous les champs obligatoires (*).")
        elif password != confirm:
            st.error("Les mots de passe ne correspondent pas.")
        elif len(password) < 6:
            st.error("Le mot de passe doit contenir au moins 6 caractères.")
        else:
            # Charger le fichier existant
            if doctors_file.exists():
                with open(doctors_file, "r", encoding="utf-8") as f:
                    doctors = json.load(f)
            else:
                doctors = {}

            # Vérifier unicité de l'identifiant
            if username in doctors:
                st.error("Cet identifiant existe déjà. Veuillez en choisir un autre.")
            else:
                # Ajouter le nouveau médecin
                doctors[username] = {
                    "password": password,  # Idéalement, hacher en production
                    "name": name,
                    "specialite": specialite,
                    "email": email,
                    "telephone": telephone
                }
                # Sauvegarder
                with open(doctors_file, "w", encoding="utf-8") as f:
                    json.dump(doctors, f, indent=2, ensure_ascii=False)

                st.success("✅ Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
                # Redirection vers login médecin
                if st.button("Aller à la connexion"):
                    st.switch_page("doctor_login.py")

# Lien vers la connexion
st.markdown("---")
st.markdown("Déjà inscrit ? [Se connecter](doctor_login.py)")