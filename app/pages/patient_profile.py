import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Mon Profil", page_icon="📊", layout="wide")

# ── Cacher la navigation automatique de Streamlit ──────────────
st.markdown("""
<style>
    [data-testid="stSidebarNav"] { display: none; }
    #MainMenu, footer { visibility: hidden; }   /* ← header n'est plus caché */
    /* Optionnel : masquer d'autres éléments du header */
    header [data-testid="stLogo"] { display: none; }
    header [data-testid="stStatusWidget"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Design system ───────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

    .stApp { background-color: #0B1628; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; color: white; }

    /* En-tête patient */
    .patient-header {
        padding: 28px 0 24px 0;
        border-bottom: 1px solid rgba(255,255,255,0.07);
        margin-bottom: 40px;
    }
    .patient-tag {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.72rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #52B788;
        margin-bottom: 10px;
    }
    .patient-greeting {
        font-family: 'Playfair Display', serif;
        font-size: 2.4rem;
        color: white;
        margin: 0;
        font-weight: 600;
        line-height: 1.2;
    }
    .patient-greeting span {
        color: #52B788;
    }
    .patient-meta {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.85rem;
        color: rgba(255,255,255,0.35);
        margin-top: 8px;
    }
    .patient-meta span { color: rgba(255,255,255,0.6); }

    /* Étapes */
    .step-block {
        display: flex;
        gap: 28px;
        align-items: flex-start;
        margin-bottom: 48px;
    }
    .step-number {
        font-family: 'Playfair Display', serif;
        font-size: 4rem;
        font-weight: 700;
        line-height: 1;
        min-width: 60px;
        opacity: 0.12;
        color: white;
        user-select: none;
    }
    .step-content {
        flex: 1;
        border-left: 3px solid;
        padding-left: 24px;
        padding-top: 4px;
    }
    .step-label {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.72rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: rgba(255,255,255,0.35);
        margin-bottom: 8px;
    }
    .step-value {
        font-family: 'Playfair Display', serif;
        font-size: 2.4rem;
        font-weight: 600;
        margin: 0;
        line-height: 1.1;
    }
    .step-sub {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.88rem;
        margin-top: 8px;
        opacity: 0.6;
        color: white;
    }
    .step-diagnosis {
        font-family: 'Playfair Display', serif;
        font-size: 1.6rem;
        font-weight: 600;
        margin: 0;
        line-height: 1.2;
    }
    .step-conseil {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.9rem;
        margin-top: 12px;
        padding: 10px 16px;
        border-radius: 8px;
        display: inline-block;
    }

    /* Barre IMC */
    .imc-bar-wrapper { margin-top: 14px; width: 100%; max-width: 420px; }
    .imc-bar-track {
        height: 6px;
        border-radius: 4px;
        background: linear-gradient(to right, #2196F3 0%, #52B788 25%, #F4A261 55%, #E05252 80%, #7B0000 100%);
        position: relative;
        margin-bottom: 6px;
    }
    .imc-bar-labels {
        display: flex;
        justify-content: space-between;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.68rem;
        color: rgba(255,255,255,0.3);
    }

    /* Recommandations */
    .reco-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        font-family: 'DM Sans', sans-serif;
        font-size: 0.92rem;
        color: rgba(255,255,255,0.8);
        line-height: 1.5;
    }
    .reco-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #52B788;
        margin-top: 8px;
        flex-shrink: 0;
    }

    /* Waiting / Error */
    .waiting-card {
        background-color: rgba(255,255,255,0.02);
        border: 2px dashed #7EC8E3;
        border-radius: 16px;
        padding: 48px;
        text-align: center;
        margin: 30px 0;
        font-family: 'DM Sans', sans-serif;
    }
    .error-card {
        background-color: rgba(224,82,82,0.07);
        border: 1px solid #E05252;
        border-radius: 16px;
        padding: 28px;
        margin: 20px 0;
        color: #E05252;
        text-align: center;
        font-family: 'DM Sans', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0d1f35;
        border-right: 1px solid rgba(255,255,255,0.07);
    }
    .sidebar-logo {
        font-family: 'Playfair Display', serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: white;
        margin-bottom: 4px;
    }
    .sidebar-logo span { color: #52B788; }
    .sidebar-role {
        font-size: 0.72rem;
        color: rgba(255,255,255,0.35);
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }
    .user-card {
        background: rgba(82,183,136,0.08);
        border: 1px solid rgba(82,183,136,0.2);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 2rem;
    }
    .user-name { color: white; font-size: 0.92rem; font-weight: 500; font-family: 'DM Sans', sans-serif; }
    .user-sub  { color: rgba(255,255,255,0.4); font-size: 0.75rem; margin-top: 2px; font-family: 'DM Sans', sans-serif; }
    .nav-section {
        font-size: 0.68rem;
        color: rgba(255,255,255,0.25);
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 1.2rem 0 0.5rem 0;
        font-family: 'DM Sans', sans-serif;
    }
    div[data-testid="stSidebar"] .stButton > button {
        background: transparent;
        color: rgba(255,255,255,0.65);
        border: none;
        border-radius: 8px;
        text-align: left;
        width: 100%;
        padding: 0.5rem 0.75rem;
        font-size: 0.88rem;
        font-family: 'DM Sans', sans-serif;
    }
    div[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.06);
        color: white;
    }
    /* Bouton déconnexion */
    div[data-testid="stSidebar"] [data-testid="stButton"]:last-child > button {
        color: #E05252 !important;
    }
    div[data-testid="stSidebar"] [data-testid="stButton"]:last-child > button:hover {
        background: rgba(224,82,82,0.1) !important;
    }

    /* MainMenu, footer, header : déjà cachés plus haut, on ne cache pas header */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Chemins ─────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ── Vérifier connexion ──────────────────────────────────────────
if not st.session_state.get("logged_in") or st.session_state.get("role") != "patient":
    st.warning("Veuillez vous connecter pour accéder à cette page.")
    if st.button("Aller à la connexion"):
        st.switch_page("pages/patient_login.py")
    st.stop()

# ── Chargement JSON ─────────────────────────────────────────────
def load_json_safe(filepath):
    if not filepath.exists():
        return None
    for enc in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError as e:
            st.error(f"Erreur JSON dans {filepath.name} : {e}")
            return None
    return None

def clean_text(text):
    if not text:
        return text
    text = text.replace("\ufffd", "").replace("\n", "\n")
    text = "".join(c for c in text if ord(c) >= 32 or c == "\n")
    return text.strip()

patient_id    = st.session_state.get("patient_id", "")
patients_file = BASE_DIR / "data" / "patients.json"
record_file   = BASE_DIR / "data" / "records" / f"{patient_id}.json"

record_early  = load_json_safe(record_file)
patients_data = load_json_safe(patients_file)
patient_info  = patients_data.get(patient_id, {}) if patients_data else {}

# ── Nom du patient ──────────────────────────────────────────────
# Priorité : record > session_state > patients.json
if record_early:
    prenom = record_early.get("prenom", "")
    nom    = record_early.get("nom", "")
    display_name = f"{prenom} {nom}".strip()
else:
    display_name = ""

if not display_name:
    display_name = st.session_state.get("display_name", "")
if not display_name:
    prenom = patient_info.get("prenom", "")
    nom    = patient_info.get("nom", "")
    display_name = f"{prenom} {nom}".strip() or "Patient"

# Prénom seul pour le bonjour
prenom_seul = display_name.split()[0] if display_name else "Patient"

# ── Médecin référent ────────────────────────────────────────────
# Priorité : reco_author du record > doctor du record > patients.json
medecin = ""
if record_early:
    medecin = (record_early.get("reco_author", "") or
               record_early.get("doctor", "") or
               record_early.get("medecin", ""))
if not medecin:
    medecin = (patient_info.get("medecin_referent", "") or
               st.session_state.get("medecin_referent", ""))
medecin = medecin if medecin else "Non assigné"

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

# ── Mapping classes ─────────────────────────────────────────────
class_mapping = {
    "Insufficient_Weight": {
        "label": "Poids Insuffisant",
        "color": "#2196F3",
        "conseil": "Consultez un nutritionniste pour un suivi personnalisé.",
        "conseil_bg": "rgba(33,150,243,0.1)"
    },
    "Normal_Weight": {
        "label": "Poids Normal",
        "color": "#52B788",
        "conseil": "Vos indicateurs sont bons. Maintenez vos habitudes saines.",
        "conseil_bg": "rgba(82,183,136,0.1)"
    },
    "Overweight_Level_I": {
        "label": "Surpoids — Niveau I",
        "color": "#F4A261",
        "conseil": "Une activité physique régulière est recommandée.",
        "conseil_bg": "rgba(244,162,97,0.1)"
    },
    "Overweight_Level_II": {
        "label": "Surpoids — Niveau II",
        "color": "#E76F51",
        "conseil": "Un suivi médical est recommandé.",
        "conseil_bg": "rgba(231,111,81,0.1)"
    },
    "Obesity_Type_I": {
        "label": "Obésité — Type I",
        "color": "#E05252",
        "conseil": "Une consultation spécialisée est conseillée.",
        "conseil_bg": "rgba(224,82,82,0.1)"
    },
    "Obesity_Type_II": {
        "label": "Obésité — Type II",
        "color": "#C62828",
        "conseil": "Un suivi médical rapproché est nécessaire.",
        "conseil_bg": "rgba(198,40,40,0.1)"
    },
    "Obesity_Type_III": {
        "label": "Obésité — Type III (Morbide)",
        "color": "#B71C1C",
        "conseil": "Une prise en charge médicale urgente est recommandée.",
        "conseil_bg": "rgba(183,28,28,0.1)"
    }
}

# ── Contenu principal ───────────────────────────────────────────
record    = load_json_safe(record_file)
date_eval = record.get('date_analyse', '') if record else ''
date_str  = f"Évalué le {date_eval} · " if date_eval else ""

st.markdown(f"""
<div class="patient-header">
    <div class="patient-tag">Tableau de bord patient</div>
    <p class="patient-greeting">Bonjour, <span>{prenom_seul}</span></p>
    <p class="patient-meta">{date_str}Médecin référent : <span>{medecin}</span></p>
</div>
""", unsafe_allow_html=True)

if record:
    bmi        = record.get('BMI')
    prediction = record.get('prediction')
    reco_text  = clean_text(record.get('recommendations', ''))

    if bmi:
        if bmi < 18.5:
            bmi_color, imc_marker = "#2196F3", "8%"
        elif bmi < 25:
            bmi_color, imc_marker = "#52B788", "30%"
        elif bmi < 30:
            bmi_color, imc_marker = "#F4A261", "58%"
        elif bmi < 35:
            bmi_color, imc_marker = "#E05252", "75%"
        else:
            bmi_color, imc_marker = "#B71C1C", "92%"
    else:
        bmi_color, imc_marker = "#52B788", "30%"

    info = class_mapping.get(prediction, {
        "label": prediction or "Inconnu",
        "color": "#7EC8E3",
        "conseil": "",
        "conseil_bg": "rgba(126,200,227,0.1)"
    })

    # ÉTAPE 1 — IMC
    if bmi:
        st.markdown(f"""
        <div class="step-block">
            <div class="step-number">1</div>
            <div class="step-content" style="border-color:{bmi_color};">
                <div class="step-label">Votre indice de masse corporelle</div>
                <p class="step-value" style="color:{bmi_color};">{bmi:.1f}</p>
                <div class="step-sub">kg / m²</div>
                <div class="imc-bar-wrapper">
                    <div class="imc-bar-track">
                        <div style="
                            position:absolute; left:{imc_marker}; top:-4px;
                            width:14px; height:14px; border-radius:50%;
                            background:{bmi_color}; border:2px solid #0B1628;
                            transform:translateX(-50%);
                        "></div>
                    </div>
                    <div class="imc-bar-labels">
                        <span>Insuffisant</span>
                        <span>Normal</span>
                        <span>Surpoids</span>
                        <span>Obésité</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ÉTAPE 2 — Diagnostic
    st.markdown(f"""
    <div class="step-block">
        <div class="step-number">2</div>
        <div class="step-content" style="border-color:{info['color']};">
            <div class="step-label">Votre diagnostic</div>
            <p class="step-diagnosis" style="color:{info['color']};">
                Vous présentez un niveau : {info['label']}
            </p>
            <div class="step-conseil" style="background:{info['conseil_bg']}; color:{info['color']};">
                {info['conseil']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ÉTAPE 3 — Recommandations
    if reco_text:
        lignes     = [l.strip() for l in reco_text.replace('●', '\n').split('\n') if l.strip()]
        items_html = "".join(
            f'<div class="reco-item"><div class="reco-dot"></div><span>{l}</span></div>'
            for l in lignes
        )
        st.markdown(f"""
        <div class="step-block">
            <div class="step-number">3</div>
            <div class="step-content" style="border-color:#52B788;">
                <div class="step-label">Ce que votre médecin vous recommande</div>
                <div style="margin-top:8px;">{items_html}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="step-block">
            <div class="step-number">3</div>
            <div class="step-content" style="border-color:rgba(255,255,255,0.1);">
                <div class="step-label">Ce que votre médecin vous recommande</div>
                <p style="color:rgba(255,255,255,0.35); font-family:'DM Sans',sans-serif;
                          font-size:0.9rem; margin-top:8px;">
                    Votre médecin n'a pas encore rédigé de recommandations.<br>
                    Elles apparaîtront ici après votre prochaine consultation.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    if record_file.exists():
        st.markdown("""
        <div class="error-card">
            <strong>Erreur de lecture</strong><br>
            Le fichier de votre dossier médical est illisible.<br>
            Veuillez contacter votre médecin.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="waiting-card">
            <p style="color:#7EC8E3; font-family:'Playfair Display',serif;
                      font-size:1.3rem; margin-bottom:12px;">
                En attente de votre première évaluation
            </p>
            <p style="color:rgba(255,255,255,0.45); font-size:0.9rem;">
                Votre médecin n'a pas encore réalisé votre évaluation médicale.<br>
                Les résultats apparaîtront ici après votre première consultation.
            </p>
        </div>
        """, unsafe_allow_html=True)