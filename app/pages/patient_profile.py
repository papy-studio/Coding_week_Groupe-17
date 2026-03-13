import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Mon Profil", page_icon="📊")

# Design system
st.markdown("""
<style>
    .stApp { background-color: #0B1628; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; color: white; }
    .metric-card {
        background-color: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
    }
    .reco-card {
        background-color: rgba(82, 183, 136, 0.1);
        border: 1px solid #52B788;
        border-radius: 16px;
        padding: 25px;
        margin: 20px 0;
        color: white;
        font-size: 16px;
        line-height: 1.6;
    }
    .risk-badge {
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        margin: 20px 0;
    }
    .waiting-card {
        background-color: rgba(255,255,255,0.02);
        border: 2px dashed #7EC8E3;
        border-radius: 16px;
        padding: 40px;
        text-align: center;
        margin: 30px 0;
    }
    .error-card {
        background-color: rgba(224, 82, 82, 0.1);
        border: 1px solid #E05252;
        border-radius: 16px;
        padding: 20px;
        margin: 20px 0;
        color: #E05252;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ✅ Chemins absolus
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ✅ Vérifier la connexion
if not st.session_state.get("logged_in") or st.session_state.get("role") != "patient":
    st.warning("Veuillez vous connecter pour accéder à cette page.")
    if st.button("🔐 Aller à la connexion"):
        st.switch_page("pages/patient_login.py")
    st.stop()

# Titre
st.title(f"📊 Bienvenue, {st.session_state.get('display_name', 'Patient')}")

# Récupérer l'ID du patient
patient_id = st.session_state.get("patient_id")
if not patient_id:
    st.error("Erreur : ID patient non trouvé")
    st.stop()

# Mapping des classes d'obésité
class_mapping = {
    "Insufficient_Weight": {
        "label": "Poids Insuffisant",
        "color": "#2196F3",
        "conseil": "Consultez un nutritionniste pour un suivi personnalisé"
    },
    "Normal_Weight": {
        "label": "Poids Normal",
        "color": "#52B788",
        "conseil": "Maintenez vos habitudes saines !"
    },
    "Overweight_Level_I": {
        "label": "Surpoids — Niveau I",
        "color": "#F4A261",
        "conseil": "Augmentez votre activité physique"
    },
    "Overweight_Level_II": {
        "label": "Surpoids — Niveau II",
        "color": "#E76F51",
        "conseil": "Suivi médical recommandé"
    },
    "Obesity_Type_I": {
        "label": "Obésité — Type I",
        "color": "#E05252",
        "conseil": "Consultation spécialisée conseillée"
    },
    "Obesity_Type_II": {
        "label": "Obésité — Type II",
        "color": "#C62828",
        "conseil": "Suivi rapproché nécessaire"
    },
    "Obesity_Type_III": {
        "label": "Obésité — Type III (Morbide)",
        "color": "#7B0000",
        "conseil": "Prise en charge médicale urgente recommandée"
    }
}

# Chemins des fichiers
record_file = BASE_DIR / "data" / "records" / f"{patient_id}.json"
patients_file = BASE_DIR / "data" / "patients.json"

# Fonction pour charger un fichier JSON avec gestion d'encodage
def load_json_safe(filepath):
    """Tente de charger un fichier JSON avec différents encodages."""
    if not filepath.exists():
        return None
    encodings = ['utf-8', 'latin-1', 'cp1252']
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError as e:
            st.error(f"Erreur de format JSON dans {filepath.name} : {e}")
            return None
    st.error(f"Impossible de lire le fichier {filepath.name} (encodage non supporté).")
    return None

# Charger les infos de base du patient
patient_info = {}
patients_data = load_json_safe(patients_file)
if patients_data:
    patient_info = patients_data.get(patient_id, {})

# Afficher les infos de base
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("### 📅 Inscription")
    date_inscription = patient_info.get('date_inscription', 'N/A')
    st.markdown(f"**{date_inscription}**")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("### 📏 Taille")
    taille = patient_info.get('taille', 'N/A')
    if taille != 'N/A':
        st.markdown(f"**{taille} m**")
    else:
        st.markdown("**N/A**")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("### 👨‍⚕️ Médecin")
    medecin = patient_info.get('medecin_referent', 'Non assigné')
    st.markdown(f"**{medecin}**")
    st.markdown('</div>', unsafe_allow_html=True)

# Vérifier si le dossier médical existe
record = load_json_safe(record_file)

if record:
    st.markdown("---")
    st.subheader("📋 Dernière évaluation médicale")
    st.caption(f"Date : {record.get('date_analyse', 'Date inconnue')}")

    bmi = record.get('BMI')
    if bmi:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("### ⚖️ IMC")

            if bmi < 18.5:
                bmi_color = "#2196F3"
            elif bmi < 25:
                bmi_color = "#52B788"
            elif bmi < 30:
                bmi_color = "#F4A261"
            else:
                bmi_color = "#E05252"

            st.markdown(f"<h1 style='color:{bmi_color}; margin:0;'>{bmi:.1f}</h1>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🎯 Niveau de risque évalué")

    prediction = record.get('prediction')
    if prediction in class_mapping:
        info = class_mapping[prediction]
        st.markdown(f"""
        <div class="risk-badge" style="background-color:{info['color']}20; border:2px solid {info['color']};">
            <span style="color:{info['color']};">{info['label']}</span>
        </div>
        <p style="color:#7EC8E3; text-align:center; font-size:18px; margin-top:10px;">
            💡 {info['conseil']}
        </p>
        """, unsafe_allow_html=True)
    else:
        st.info("Aucune évaluation de risque disponible.")

    st.markdown("---")
    st.subheader("📋 Recommandations de votre médecin")

    recommendations = record.get('recommendations', '')
    if recommendations and recommendations.strip():
        st.markdown(f"""
        <div class="reco-card">
            {recommendations}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("""
        Votre médecin n'a pas encore rédigé de recommandations personnalisées.
        Elles apparaîtront ici après votre prochaine consultation.
        """)
else:
    # Aucun dossier ou erreur de lecture
    st.markdown("---")
    if record_file.exists():
        st.markdown("""
        <div class="error-card">
            <h3>❌ Erreur de lecture</h3>
            <p>Le fichier de votre dossier médical est corrompu ou illisible.<br>
            Veuillez contacter votre médecin pour qu'il le régénère.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="waiting-card">
            <h3 style="color:#7EC8E3;">⏳ En attente d'évaluation</h3>
            <p style="color:white; margin-top:20px;">
                Votre médecin n'a pas encore réalisé votre évaluation médicale.<br>
                Les résultats apparaîtront ici après votre première consultation.
            </p>
        </div>
        """, unsafe_allow_html=True)

# Boutons de navigation
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("📈 Suivi de poids", use_container_width=True):
        st.switch_page("pages/patient_tracking.py")

with col2:
    if st.button("🚪 Se déconnecter", use_container_width=True):
        for key in ['logged_in', 'role', 'username', 'patient_id',
                    'display_name', 'patient_nom', 'patient_prenom']:
            if key in st.session_state:
                del st.session_state[key]
        st.switch_page("pages/home.py")