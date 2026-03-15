## PARTIE 3 : APPLICATION (dossier app/)

### Contexte :
Nous avons développé une application complète avec deux interfaces distinctes :
- **Espace Médecin** : pour saisir les données des patients, visualiser les prédictions SHAP et rédiger des recommandations
- **Espace Patient** : pour consulter son niveau de risque, lire les recommandations de son médecin et suivre son poids

L'idée principale de MediObes est : **"Estimer le risque d'obésité, puis accompagner le patient dans sa guérison."**

---

## 📋 PLAN DE L'APPLICATION (d'après le document MediObes_Documentation.docx)

### 1. Espace Médecin
- Login sécurisé avec identifiants médecin
- Tableau de bord : liste des patients suivis
- Saisie des données cliniques d'un nouveau patient
- Consultation de l'estimation du risque d'obésité + graphique SHAP
- Rédaction et sauvegarde des recommandations personnalisées

### 2. Espace Patient
- Login sécurisé avec identifiants patient
- Consultation du niveau de risque d'obésité et de l'IMC
- Lecture des recommandations rédigées par le médecin
- Plan de style de vie et de diet généré automatiquement par l'assistant IA
- Fiche de suivi hebdomadaire du poids avec graphique d'évolution
- Alertes automatiques si l'évolution du poids est préoccupante

### 3. Assistant IA (Groq + Llama 3)
- Génération de recommandations personnalisées basées sur le dossier médical du patient
- Plan de diet adapté au profil
- Messages d'encouragement ou d'alerte selon l'évolution

---

## 👤 Membre 3 - Espace Patient & Assistant IA

#### Prompt 3.1 : Structure de l'espace patient

**Ce qu'on a tapé dans ChatGPT :**
"Nous développons une application médicale appelée MediObes avec Streamlit.
Je dois créer l'espace patient (membre 3) avec :

Login sécurisé pour les patients (fichier JSON)

Page d'accueil patient avec affichage du niveau de risque d'obésité et IMC

Consultation des recommandations du médecin

Fiche de suivi du poids avec graphique d'évolution

Assistant IA qui génère des recommandations personnalisées

Je ne suis pas très fort en code. Peux-tu me donner la structure complète du code pour ces fonctionnalités ?"

text

**Ce que ChatGPT nous a répondu :**
```python
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime
import hashlib

# Configuration de la page
st.set_page_config(
    page_title="MediObes - Espace Patient",
    page_icon="👤",
    layout="wide"
)

# Fonction pour hasher les mots de passe (sécurité)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Charger les données des patients
def load_patients():
    if not os.path.exists("data/patients.json"):
        return {}
    with open("data/patients.json", "r", encoding='utf-8') as f:
        return json.load(f)

# Charger le dossier médical d'un patient
def load_patient_record(patient_id):
    record_path = f"data/records/{patient_id}.json"
    if not os.path.exists(record_path):
        return {}
    try:
        with open(record_path, "r", encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

# Charger l'historique de poids
def load_weight_history(patient_id):
    weight_path = f"data/tracking/{patient_id}.csv"
    if not os.path.exists(weight_path):
        return pd.DataFrame(columns=['date', 'poids'])
    return pd.read_csv(weight_path)

# Sauvegarder une nouvelle entrée de poids
def save_weight_entry(patient_id, poids):
    os.makedirs("data/tracking", exist_ok=True)
    weight_path = f"data/tracking/{patient_id}.csv"
    
    # Charger l'historique existant
    if os.path.exists(weight_path):
        df = pd.read_csv(weight_path)
    else:
        df = pd.DataFrame(columns=['date', 'poids'])
    
    # Ajouter la nouvelle entrée
    new_entry = pd.DataFrame([{
        'date': datetime.now().strftime("%Y-%m-%d"),
        'poids': poids
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(weight_path, index=False)
    return df

# Page de login
def login_page():
    st.title("👤 Espace Patient - Connexion")
    
    with st.form("login_form"):
        username = st.text_input("Identifiant patient")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")
        
        if submitted:
            patients = load_patients()
            hashed_pwd = hash_password(password)
            
            if username in patients and patients[username]["password"] == hashed_pwd:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = "patient"
                st.session_state["patient_name"] = patients[username]["name"]
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect")

# Page principale de l'espace patient
def patient_dashboard():
    st.sidebar.title(f"👤 {st.session_state['patient_name']}")
    st.sidebar.write(f"ID: {st.session_state['username']}")
    
    menu = st.sidebar.radio(
        "Menu",
        ["🏠 Accueil", "📊 Mon Risque", "📝 Recommandations", "📈 Suivi du poids", "❓ Aide"]
    )
    
    patient_id = st.session_state['username']
    record = load_patient_record(patient_id)
    
    if menu == "🏠 Accueil":
        st.title("🏠 Accueil")
        st.write(f"Bienvenue, {st.session_state['patient_name']} !")
        
        if record:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Niveau de risque", record.get('prediction', 'Non défini'))
            with col2:
                st.metric("IMC", f"{record.get('BMI', 0):.1f}")
            with col3:
                st.metric("Dernière consultation", record.get('date_analyse', 'Jamais'))
        else:
            st.info("Aucun dossier médical trouvé. Consultez votre médecin.")
    
    elif menu == "📊 Mon Risque":
        st.title("📊 Mon niveau de risque")
        
        if record:
            prediction = record.get('prediction', 'Inconnu')
            bmi = record.get('BMI', 0)
            
            # Définir la couleur selon le risque
            if "Obesity" in prediction:
                color = "red"
                emoji = "🔴"
                level = "Élevé"
            elif "Overweight" in prediction:
                color = "orange"
                emoji = "🟠"
                level = "Modéré"
            else:
                color = "green"
                emoji = "🟢"
                level = "Faible"
            
            st.markdown(f"""
            <div style="padding:20px; border-radius:10px; background-color:{color}20; border-left:5px solid {color};">
                <h2>{emoji} Risque {level}</h2>
                <h3 style="color:{color};">{prediction}</h3>
                <p>IMC : <b>{bmi:.1f}</b> kg/m²</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Facteurs de risque
            st.subheader("📋 Facteurs de risque")
            clinical = record.get('clinical_data', {})
            if clinical:
                cols = st.columns(2)
                with cols[0]:
                    st.write(f"Âge : {clinical.get('Age', 'N/A')} ans")
                    st.write(f"Sexe : {'Homme' if clinical.get('Gender') == 1 else 'Femme'}")
                    st.write(f"Taille : {clinical.get('Height', 'N/A')} m")
                with cols[1]:
                    st.write(f"Antécédents familiaux : {'Oui' if clinical.get('family_history_with_overweight') else 'Non'}")
                    st.write(f"Tabac : {'Oui' if clinical.get('SMOKE') else 'Non'}")
                    st.write(f"Activité physique : {clinical.get('FAF', 'N/A')}/3")
        else:
            st.warning("Aucune donnée médicale disponible. Consultez votre médecin.")
    
    elif menu == "📝 Recommandations":
        st.title("📝 Recommandations de votre médecin")
        
        if record:
            recommendations = record.get('recommendations', '')
            diet_plan = record.get('diet_plan', '')
            
            if recommendations:
                st.subheader("👨‍⚕️ Recommandations médicales")
                st.info(recommendations)
            else:
                st.info("Aucune recommandation pour le moment.")
            
            if diet_plan:
                st.subheader("🥗 Plan alimentaire")
                st.success(diet_plan)
            else:
                st.info("Aucun plan alimentaire pour le moment.")
            
            # Assistant IA (à implémenter avec Groq)
            st.subheader("🤖 Assistant personnel")
            if st.button("Générer des conseils personnalisés"):
                with st.spinner("L'assistant réfléchit..."):
                    # Ici, appel à l'API Groq
                    st.success("Fonctionnalité à venir avec Groq API")
        else:
            st.warning("Aucune recommandation disponible.")
    
    elif menu == "📈 Suivi du poids":
        st.title("📈 Suivi du poids")
        
        # Formulaire pour ajouter un poids
        with st.form("weight_form"):
            poids = st.number_input("Votre poids aujourd'hui (kg)", min_value=30.0, max_value=250.0, step=0.1)
            submitted = st.form_submit_button("Enregistrer")
            
            if submitted:
                df = save_weight_entry(patient_id, poids)
                st.success("Poids enregistré !")
        
        # Afficher l'historique
        df_weight = load_weight_history(patient_id)
        
        if not df_weight.empty:
            st.subheader("Historique")
            st.dataframe(df_weight)
            
            # Graphique
            fig, ax = plt.subplots(figsize=(10, 5))
            df_weight['date'] = pd.to_datetime(df_weight['date'])
            df_weight = df_weight.sort_values('date')
            
            ax.plot(df_weight['date'], df_weight['poids'], marker='o', linestyle='-', color='blue')
            ax.set_xlabel('Date')
            ax.set_ylabel('Poids (kg)')
            ax.set_title('Évolution du poids')
            ax.grid(True, alpha=0.3)
            
            # Ajouter une ligne de tendance
            if len(df_weight) > 1:
                z = np.polyfit(range(len(df_weight)), df_weight['poids'], 1)
                p = np.poly1d(z)
                ax.plot(df_weight['date'], p(range(len(df_weight))), 'r--', alpha=0.7, label='Tendance')
                ax.legend()
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            
            # Alertes automatiques
            st.subheader("🔔 Alertes")
            if len(df_weight) >= 2:
                derniers = df_weight.tail(2)
                diff = derniers.iloc[1]['poids'] - derniers.iloc[0]['poids']
                
                if diff < -0.5:
                    st.success("✅ Bravo ! Vous perdez du poids régulièrement. Continuez ! 💪")
                elif diff > 1.0:
                    st.error(f"🔴 Attention : votre poids a augmenté de {diff:.1f} kg cette semaine. Consultez vos recommandations.")
                elif abs(diff) < 0.5:
                    st.warning("🟠 Votre poids est stable. C'est le moment d'intensifier vos efforts !")
        else:
            st.info("Aucun historique de poids. Commencez par enregistrer votre poids.")
    
    elif menu == "❓ Aide":
        st.title("❓ Aide")
        st.write("""
        ### Comment utiliser l'espace patient ?
        
        **📊 Mon Risque** : Consultez votre niveau de risque d'obésité et votre IMC.
        
        **📝 Recommandations** : Lisez les recommandations de votre médecin et les conseils personnalisés.
        
        **📈 Suivi du poids** : Enregistrez votre poids chaque semaine et visualisez votre évolution.
        
        ### Questions fréquentes
        - **Mes données sont-elles sécurisées ?** Oui, toutes vos données sont stockées localement et protégées.
        - **Comment contacter mon médecin ?** Les coordonnées de votre médecin sont disponibles dans vos recommandations.
        """)

# Main
def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    
    if not st.session_state["logged_in"]:
        login_page()
    else:
        patient_dashboard()

if __name__ == "__main__":
    main()
Prompt 3.2 : Intégration de l'assistant IA avec Groq
Ce qu'on a tapé dans ChatGPT :

text
"On veut intégrer un vrai assistant IA avec Groq + Llama 3.
Le dossier patient contient : niveau de risque, IMC, recommandations du médecin, âge, poids.
On veut que l'assistant génère des conseils personnalisés.

Peux-tu nous montrer comment faire avec l'API Groq ?"
Ce que ChatGPT nous a répondu :

python
import os
import requests
import json

# Configuration Groq (à mettre dans un fichier .env en production)
GROQ_API_KEY = "votre_clé_api_ici"  # À remplacer par votre vraie clé
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def generate_ia_recommendations(patient_data):
    """
    Génère des recommandations personnalisées via Llama 3 sur Groq
    """
    
    # Construction du prompt
    prompt = f"""Tu es un assistant médical spécialisé en nutrition et mode de vie.
    
    Voici le dossier d'un patient :
    - Niveau de risque : {patient_data.get('prediction', 'Non défini')}
    - IMC : {patient_data.get('BMI', 0)} kg/m²
    - Âge : {patient_data.get('age', 'Inconnu')} ans
    - Poids actuel : {patient_data.get('weight', 0)} kg
    - Taille : {patient_data.get('height', 0)} m
    
    Recommandations du médecin :
    {patient_data.get('doctor_recommendations', 'Aucune')}
    
    Sur la base de ces informations, génère un plan personnalisé en 3 parties :
    1. Conseils de style de vie (activité physique, sommeil, gestion du stress)
    2. Plan alimentaire détaillé (petit-déjeuner, déjeuner, dîner, collations)
    3. Objectifs réalistes pour les 3 prochains mois
    
    Sois encourageant, précis et médicalement cohérent. Adapte tes conseils au profil du patient.
    """
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Tu es un assistant médical expert en nutrition et accompagnement thérapeutique."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"Erreur lors de l'appel à l'IA : {str(e)}"

# Fonction pour utiliser l'assistant dans Streamlit
def assistant_ui(patient_id):
    st.subheader("🤖 Assistant personnel IA")
    
    # Charger les données du patient
    record = load_patient_record(patient_id)
    
    if not record:
        st.warning("Données patient insuffisantes.")
        return
    
    patient_data = {
        'prediction': record.get('prediction', 'Inconnu'),
        'BMI': record.get('BMI', 0),
        'age': record.get('clinical_data', {}).get('Age', 30),
        'weight': record.get('clinical_data', {}).get('Weight', 70),
        'height': record.get('clinical_data', {}).get('Height', 1.7),
        'doctor_recommendations': record.get('recommendations', '')
    }
    
    if st.button("🔄 Générer des conseils personnalisés"):
        with st.spinner("L'assistant réfléchit..."):
            response = generate_ia_recommendations(patient_data)
            st.session_state['ia_response'] = response
    
    if 'ia_response' in st.session_state:
        st.markdown(st.session_state['ia_response'])
👤 Membre 4 - Interface Médecin & Dashboard
Prompt 3.3 : Structure de l'espace médecin
Ce qu'on a tapé dans ChatGPT :

text
"Je dois créer l'espace médecin avec :
- Login sécurisé (fichier JSON pour les médecins)
- Tableau de bord avec la liste des patients
- Formulaire de saisie des données patient
- Page de résultats avec prédiction et SHAP
- Rédaction des recommandations

Peux-tu me donner la structure complète ?"
Ce que ChatGPT nous a répondu :

python
import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import joblib
from datetime import datetime
import hashlib

# Configuration
st.set_page_config(page_title="MediObes - Espace Médecin", layout="wide")

# Fonctions utilitaires
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_doctors():
    if not os.path.exists("data/doctors.json"):
        # Créer un médecin par défaut
        default_doctors = {
            "dr.martin": {
                "password": hash_password("medic123"),
                "name": "Dr. Sophie Martin",
                "specialite": "Nutrition"
            }
        }
        os.makedirs("data", exist_ok=True)
        with open("data/doctors.json", "w") as f:
            json.dump(default_doctors, f, indent=2)
        return default_doctors
    
    with open("data/doctors.json", "r") as f:
        return json.load(f)

def load_patients():
    if not os.path.exists("data/patients.json"):
        return {}
    with open("data/patients.json", "r") as f:
        return json.load(f)

def save_patient(patient_id, patient_data):
    patients = load_patients()
    patients[patient_id] = patient_data
    with open("data/patients.json", "w") as f:
        json.dump(patients, f, indent=2)

def load_model():
    try:
        return joblib.load("models/lightgbm_model.pkl")
    except:
        try:
            return joblib.load("models/xgboost_model.pkl")
        except:
            return None

# Page de login médecin
def doctor_login():
    st.title("👨‍⚕️ Espace Médecin - Connexion")
    
    doctors = load_doctors()
    
    with st.form("login_form"):
        username = st.text_input("Identifiant")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")
        
        if submitted:
            hashed_pwd = hash_password(password)
            if username in doctors and doctors[username]["password"] == hashed_pwd:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["doctor_name"] = doctors[username]["name"]
                st.session_state["role"] = "doctor"
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect")

# Tableau de bord médecin
def doctor_dashboard():
    st.sidebar.title(f"👨‍⚕️ {st.session_state['doctor_name']}")
    
    menu = st.sidebar.radio(
        "Menu",
        ["📋 Tableau de bord", "➕ Nouveau patient", "📊 Résultats", "📝 Recommandations"]
    )
    
    patients = load_patients()
    
    if menu == "📋 Tableau de bord":
        st.title("📋 Tableau de bord")
        
        # Statistiques
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Patients suivis", len(patients))
        with col2:
            # Compter les patients avec recommandations
            with_reco = sum(1 for p in patients.values() if p.get('has_recommendations', False))
            st.metric("Avec recommandations", with_reco)
        with col3:
            st.metric("Consultations", "À venir")
        
        # Liste des patients
        st.subheader("Liste des patients")
        if patients:
            data = []
            for pid, pinfo in patients.items():
                data.append({
                    "ID": pid,
                    "Nom": pinfo.get('name', ''),
                    "Dernière consultation": pinfo.get('last_visit', 'Jamais'),
                    "Statut": "✅" if pinfo.get('has_recommendations') else "⏳"
                })
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Aucun patient enregistré.")
    
    elif menu == "➕ Nouveau patient":
        st.title("➕ Nouveau patient")
        
        with st.form("patient_form"):
            col1, col2 = st.columns(2)
            with col1:
                patient_id = st.text_input("ID Patient *")
                prenom = st.text_input("Prénom *")
                nom = st.text_input("Nom *")
                age = st.number_input("Âge", 10, 100, 30)
                sexe = st.selectbox("Sexe", ["Homme", "Femme"])
                taille = st.number_input("Taille (m)", 1.4, 2.2, 1.7, 0.01)
                poids = st.number_input("Poids (kg)", 30.0, 250.0, 70.0, 0.1)
            
            with col2:
                st.write("Habitudes alimentaires")
                hist_fam = st.selectbox("Antécédents familiaux", ["Non", "Oui"])
                favc = st.selectbox("Aliments caloriques", ["Non", "Oui"])
                fcvc = st.slider("Légumes/repas", 1.0, 3.0, 2.0, 0.1)
                ncp = st.slider("Repas/jour", 1.0, 4.0, 3.0, 0.1)
                caec = st.selectbox("Grignotage", ["Non", "Parfois", "Fréquemment", "Toujours"])
                smoke = st.selectbox("Tabac", ["Non", "Oui"])
                ch2o = st.slider("Eau/jour", 1.0, 3.0, 2.0, 0.1)
                faf = st.slider("Activité physique", 0.0, 3.0, 1.0, 0.1)
            
            submitted = st.form_submit_button("Enregistrer le patient")
            
            if submitted:
                if not patient_id or not prenom or not nom:
                    st.error("Veuillez remplir tous les champs obligatoires (*)")
                else:
                    # Sauvegarder les infos du patient
                    patient_info = {
                        "name": f"{prenom} {nom}",
                        "doctor_id": st.session_state['username'],
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "has_recommendations": False
                    }
                    save_patient(patient_id, patient_info)
                    
                    # Sauvegarder les données cliniques dans session_state
                    st.session_state['current_patient'] = patient_id
                    st.session_state['patient_data'] = {
                        "Gender": 1 if sexe == "Homme" else 0,
                        "Age": age,
                        "Height": taille,
                        "Weight": poids,
                        "family_history_with_overweight": 1 if hist_fam == "Oui" else 0,
                        "FAVC": 1 if favc == "Oui" else 0,
                        "FCVC": fcvc,
                        "NCP": ncp,
                        "CAEC": ["Non", "Parfois", "Fréquemment", "Toujours"].index(caec),
                        "SMOKE": 1 if smoke == "Oui" else 0,
                        "CH2O": ch2o,
                        "SCC": 0,  # Par défaut
                        "FAF": faf,
                        "TUE": 1,  # Par défaut
                        "CALC": 0,  # Par défaut
                        "MTRANS": 3  # Par défaut (transport en commun)
                    }
                    
                    st.success(f"Patient {prenom} {nom} créé avec succès !")
                    st.info("Redirection vers l'analyse...")
                    st.session_state['page'] = "analyse"
                    st.rerun()
Prompt 3.4 : Page de résultats avec SHAP
Ce qu'on a tapé dans ChatGPT :

text
"Maintenant, je dois créer la page de résultats qui affiche :
- La prédiction du niveau d'obésité
- Les probabilités pour chaque classe
- Les graphiques SHAP pour expliquer la prédiction
- Un bouton pour rédiger les recommandations

Peux-tu me donner le code complet ?"
Ce que ChatGPT nous a répondu :

python
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import shap
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime

# Fonction pour charger le modèle
@st.cache_resource
def load_model():
    model = joblib.load("models/lightgbm_model.pkl")
    return model

# Fonction pour faire la prédiction
def predict(patient_data):
    model = load_model()
    df = pd.DataFrame([patient_data])
    prediction = model.predict(df)[0]
    probabilities = model.predict_proba(df)[0]
    
    # Classes
    classes = [
        'Insufficient_Weight', 'Normal_Weight', 'Obesity_Type_I',
        'Obesity_Type_II', 'Obesity_Type_III', 'Overweight_Level_I',
        'Overweight_Level_II'
    ]
    
    return classes[prediction], probabilities

# Fonction pour générer les graphiques SHAP
@st.cache_data
def generate_shap_plot(patient_data):
    model = load_model()
    df = pd.DataFrame([patient_data])
    
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(df)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if isinstance(shap_values, list):
        # Modèle multi-classes
        prediction = model.predict(df)[0]
        shap_values_class = shap_values[int(prediction)][0]
    else:
        shap_values_class = shap_values[0]
    
    # Trier par importance
    feature_names = df.columns
    values = shap_values_class
    indices = np.argsort(np.abs(values))[::-1][:10]  # Top 10
    
    colors = ['red' if v > 0 else 'blue' for v in values[indices]]
    
    ax.barh([feature_names[i] for i in indices], values[indices], color=colors)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.set_xlabel('Valeur SHAP')
    ax.set_title('Top 10 facteurs influençant la prédiction')
    
    plt.tight_layout()
    return fig

# Page de résultats
def results_page():
    st.title("📊 Résultat de l'estimation")
    
    if 'patient_data' not in st.session_state:
        st.warning("Aucune donnée patient. Veuillez d'abord saisir un patient.")
        if st.button("← Retour"):
            st.session_state['page'] = "dashboard"
            st.rerun()
        return
    
    patient_data = st.session_state['patient_data']
    patient_id = st.session_state.get('current_patient', 'Inconnu')
    
    # Afficher les infos patient
    st.write(f"**Patient :** {patient_id}")
    
    # Calculer l'IMC
    imc = patient_data['Weight'] / (patient_data['Height'] ** 2)
    
    # Prédiction
    with st.spinner("Calcul en cours..."):
        prediction, probabilities = predict(patient_data)
    
    # Définir la couleur selon la prédiction
    if "Obesity" in prediction:
        color = "#E74C3C"
        bg_color = "#FADBD8"
        emoji = "🔴"
    elif "Overweight" in prediction:
        color = "#F39C12"
        bg_color = "#FEF5E7"
        emoji = "🟠"
    else:
        color = "#2ECC71"
        bg_color = "#DFF2E1"
        emoji = "🟢"
    
    # Affichage du résultat principal
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <div style="padding:20px; border-radius:10px; background-color:{bg_color}; border-left:5px solid {color};">
            <h2>{emoji} Résultat</h2>
            <h3 style="color:{color};">{prediction.replace('_', ' ')}</h3>
            <p>IMC : <b>{imc:.1f}</b> kg/m²</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("📊 Probabilités")
        
        classes = [
            'Insuffisance', 'Normal', 'Obésité I',
            'Obésité II', 'Obésité III', 'Surpoids I',
            'Surpoids II'
        ]
        
        for i, (cls, prob) in enumerate(zip(classes, probabilities)):
            st.write(f"{cls}: {prob*100:.1f}%")
            st.progress(float(prob))
    
    # Graphique SHAP
    st.subheader("🔍 Explication SHAP")
    st.write("Facteurs influençant la prédiction (rouge = augmente le risque, bleu = diminue le risque)")
    
    with st.spinner("Génération du graphique SHAP..."):
        fig = generate_shap_plot(patient_data)
        st.pyplot(fig)
        plt.close(fig)
    
    # Sauvegarder le résultat
    if st.button("💾 Sauvegarder ce résultat"):
        record = {
            "patient_id": patient_id,
            "doctor": st.session_state.get('doctor_name', 'Inconnu'),
            "date_analyse": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prediction": prediction,
            "BMI": float(imc),
            "clinical_data": patient_data,
            "probabilities": probabilities.tolist()
        }
        
        os.makedirs("data/records", exist_ok=True)
        with open(f"data/records/{patient_id}.json", "w") as f:
            json.dump(record, f, indent=2)
        
        st.success("Résultat sauvegardé !")
        st.session_state['current_record'] = record
    
    # Bouton pour rédiger les recommandations
    if st.button("✍️ Rédiger des recommandations"):
        st.session_state['page'] = "recommendations"
        st.rerun()
Prompt 3.5 : Page de recommandations
Ce qu'on a tapé dans ChatGPT :

text
"Maintenant, je dois créer la page de rédaction des recommandations avec :
- Des templates pré-définis selon le niveau de risque
- Un éditeur de texte pour personnaliser
- La sauvegarde dans le dossier du patient

Peux-tu m'aider ?"
Ce que ChatGPT nous a répondu :

python
import streamlit as st
import json
import os
from datetime import datetime

# Templates de recommandations par niveau de risque
RECOMMENDATIONS_TEMPLATES = {
    "Insufficient_Weight": """
    Recommandations pour poids insuffisant :
    - Augmenter progressivement les apports caloriques (+300 kcal/j)
    - Privilégier les aliments riches en nutriments (noix, avocat, produits laitiers)
    - Consulter un nutritionniste pour un plan personnalisé
    - Surveillance mensuelle du poids
    """,
    
    "Normal_Weight": """
    Recommandations pour poids normal :
    - Maintenir les habitudes alimentaires actuelles
    - Activité physique régulière (150 min/semaine)
    - Suivi annuel recommandé
    """,
    
    "Overweight_Level_I": """
    Recommandations pour surpoids niveau I :
    - Réduire les apports caloriques (-400 kcal/j)
    - Augmenter l'activité physique (30 min/jour)
    - Limiter les aliments transformés et sucres
    - Objectif : perte de 0.5-1 kg/semaine
    """,
    
    "Overweight_Level_II": """
    Recommandations pour surpoids niveau II :
    - Consultation diététique urgente
    - Plan alimentaire structuré
    - Programme d'activité physique progressif
    - Bilan métabolique recommandé
    """,
    
    "Obesity_Type_I": """
    Recommandations pour obésité type I :
    - Prise en charge multidisciplinaire
    - Programme de rééducation alimentaire
    - Activité physique adaptée
    - Bilan cardiologique recommandé
    """,
    
    "Obesity_Type_II": """
    Recommandations pour obésité type II :
    - Orientation vers service spécialisé
    - Évaluation chirurgicale bariatrique à discuter
    - Traitement médicamenteux possible
    - Surveillance cardiaque rapprochée
    """,
    
    "Obesity_Type_III": """
    Recommandations pour obésité type III (morbide) :
    - PRISE EN CHARGE URGENTE REQUISE
    - Référence vers chirurgie bariatrique
    - Hospitalisation pour bilan complet
    - Équipe pluridisciplinaire obligatoire
    """
}

DIET_TEMPLATES = {
    "Insufficient_Weight": """
    Plan alimentaire - Prise de poids :
    - Petit-déjeuner : flocons d'avoine + lait entier + fruits
    - Déjeuner : riz complet + poulet + légumes
    - Collation : yaourt grec + noix
    - Dîner : pâtes + saumon + avocat
    """,
    
    "Normal_Weight": """
    Plan alimentaire - Maintien :
    - Petit-déjeuner : pain complet + œuf + fruit
    - Déjeuner : légumineuses + protéine maigre + légumes
    - Dîner : poisson + légumes vapeur
    """,
    
    "Overweight_Level_I": """
    Plan alimentaire - Perte modérée :
    - Petit-déjeuner : yaourt 0% + fruits
    - Déjeuner : salade composée + protéine maigre
    - Dîner : légumes vapeur + poisson
    """,
    
    "Overweight_Level_II": """
    Plan alimentaire - Perte significative :
    - Petit-déjeuner : œuf + légumes
    - Déjeuner : protéine maigre + légumes verts
    - Dîner : soupe de légumes
    """,
    
    "Obesity_Type_I": """
    Plan alimentaire - Supervisé :
    - Régime 1400-1600 kcal/j
    - 50% glucides complexes, 25% protéines, 25% lipides
    - 3 repas/jour sans grignotage
    """,
    
    "Obesity_Type_II": """
    Plan alimentaire - Strict :
    - Régime 1200-1400 kcal/j sous supervision
    - Complements vitaminiques
    - Journal alimentaire quotidien
    """,
    
    "Obesity_Type_III": """
    Plan alimentaire - Pré-opératoire :
    - Régime prescrit par chirurgien
    - Supplémentation systématique
    - Aucun régime sans supervision
    """
}

def recommendations_page():
    st.title("📝 Rédaction des recommandations")
    
    if 'current_record' not in st.session_state:
        st.warning("Aucun résultat sélectionné. Veuillez d'abord faire une analyse.")
        if st.button("← Retour"):
            st.session_state['page'] = "dashboard"
            st.rerun()
        return
    
    record = st.session_state['current_record']
    prediction = record['prediction']
    patient_id = record['patient_id']
    
    st.write(f"**Patient :** {patient_id}")
    st.write(f"**Diagnostic :** {prediction}")
    
    # Charger les templates
    default_reco = RECOMMENDATIONS_TEMPLATES.get(prediction, "")
    default_diet = DIET_TEMPLATES.get(prediction, "")
    
    # Formulaire
    with st.form("reco_form"):
        st.subheader("📋 Recommandations cliniques")
        reco_text = st.text_area("Recommandations", value=default_reco, height=200)
        
        st.subheader("🥗 Plan alimentaire")
        diet_text = st.text_area("Plan alimentaire", value=default_diet, height=200)
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Sauvegarder")
        with col2:
            cancel = st.form_submit_button("← Annuler")
    
    if submitted:
        # Mettre à jour le record
        record['recommendations'] = reco_text
        record['diet_plan'] = diet_text
        record['reco_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record['reco_author'] = st.session_state.get('doctor_name', 'Inconnu')
        
        # Sauvegarder
        with open(f"data/records/{patient_id}.json", "w") as f:
            json.dump(record, f, indent=2)
        
        # Mettre à jour le statut du patient
        patients_file = "data/patients.json"
        if os.path.exists(patients_file):
            with open(patients_file, "r") as f:
                patients = json.load(f)
            if patient_id in patients:
                patients[patient_id]['has_recommendations'] = True
                patients[patient_id]['last_reco'] = datetime.now().strftime("%Y-%m-%d")
                with open(patients_file, "w") as f:
                    json.dump(patients, f, indent=2)
        
        st.success("Recommandations sauvegardées !")
        st.balloons()
        
        if st.button("← Retour au tableau de bord"):
            st.session_state['page'] = "dashboard"
            st.rerun()
    
    if cancel:
        st.session_state['page'] = "dashboard"
        st.rerun()
RÉSUMÉ PARTIE 3 (Application) :
Membre	Fonctionnalité	Prompts
Membre 3	Espace Patient	2 prompts
Membre 3	Assistant IA Groq	1 prompt
Membre 4	Espace Médecin	3 prompts
Total		6 prompts
