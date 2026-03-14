import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Connexion Patient", page_icon="👤", layout="centered")

# ── Cacher la navigation automatique de Streamlit ──────────────
st.markdown("""
<style>
    [data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Design system ───────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

    .stApp { background-color: #0B1628; }

    h1, h2, h3 { font-family: 'Playfair Display', serif; color: white; }

    /* Card centrale */
    .login-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 20px;
        padding: 2.5rem;
        margin-top: 1rem;
    }

    /* Badge rôle */
    .role-badge {
        display: inline-block;
        background: rgba(82,183,136,0.15);
        border: 1px solid rgba(82,183,136,0.3);
        color: #52B788;
        padding: 4px 14px;
        border-radius: 20px;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.78rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    /* Sous-titre */
    .login-subtitle {
        font-family: 'DM Sans', sans-serif;
        color: rgba(255,255,255,0.45);
        font-size: 0.92rem;
        margin-bottom: 2rem;
    }

    /* Inputs */
    .stTextInput > div > div > input {
        background-color: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.10);
        color: white;
        border-radius: 10px;
        font-family: 'DM Sans', sans-serif;
        padding: 0.6rem 1rem;
        transition: border-color 0.2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(82,183,136,0.5);
        box-shadow: 0 0 0 2px rgba(82,183,136,0.1);
    }
    .stTextInput label {
        color: rgba(255,255,255,0.6) !important;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.85rem;
    }

    /* Bouton */
    .stButton > button {
        background-color: #52B788;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 2rem;
        font-family: 'DM Sans', sans-serif;
        font-weight: 500;
        width: 100%;
        font-size: 0.95rem;
        transition: opacity 0.2s, transform 0.1s;
        letter-spacing: 0.02em;
    }
    .stButton > button:hover { background-color: #3d8c6a; opacity: 1; transform: none; }

    /* Lien médecin */
    .doctor-link {
        text-align: center;
        margin-top: 1.5rem;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.85rem;
        color: rgba(255,255,255,0.35);
    }
    .doctor-link a {
        color: #52B788;
        text-decoration: none;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: rgba(255,255,255,0.2);
        font-family: 'DM Sans', sans-serif;
        font-size: 0.78rem;
        margin-top: 3rem;
    }

    /* Masquer éléments Streamlit par défaut */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar minimale (login) ───────────────────────────────────
with st.sidebar:
    st.markdown(
        '<style>[data-testid="stSidebar"]{background-color:#0d1f35;border-right:1px solid rgba(255,255,255,0.07);}'
        '.sidebar-logo{font-family:"Playfair Display",serif;font-size:1.6rem;font-weight:700;color:white;}'
        '.sidebar-logo span{color:#52B788;}'
        'div[data-testid="stSidebar"] .stButton>button{background:transparent;color:rgba(255,255,255,0.65);border:none;border-radius:8px;width:100%;padding:0.5rem 0.75rem;font-size:0.88rem;text-align:left;}'
        'div[data-testid="stSidebar"] .stButton>button:hover{background:rgba(255,255,255,0.06);color:white;}</style>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="sidebar-logo">Medi<span>Obes</span></div>', unsafe_allow_html=True)
    st.markdown("---")
    if st.button("Accueil", use_container_width=True, key="home_link"):
        st.switch_page("pages/home.py")

# ── Layout centré ───────────────────────────────────────────────
_, col, _ = st.columns([1, 2, 1])

with col:
    # Logo + titre
    st.markdown('<div class="role-badge">👤 Espace Patient</div>', unsafe_allow_html=True)
    st.markdown("## Connexion")
    st.markdown('<p class="login-subtitle">Accédez à votre dossier médical et votre suivi personnalisé</p>', unsafe_allow_html=True)

    # ── Chargement du fichier patients ─────────────────────────
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    patients_file = BASE_DIR / "data" / "patients.json"

    if not patients_file.exists():
        st.warning("⚠️ Base de données en cours d'initialisation. Veuillez réessayer dans quelques instants.")
        st.stop()

    # ── Formulaire ─────────────────────────────────────────────
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Nom d'utilisateur", placeholder="ex: patient001")
        password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Se connecter →")

        if submitted:
            if not username or not password:
                st.error("Veuillez remplir tous les champs.")
            else:
                try:
                    with open(patients_file, 'r', encoding='utf-8') as f:
                        patients = json.load(f)

                    if username in patients and patients[username]["password"] == password:
                        info = patients[username]

                        st.session_state["logged_in"]        = True
                        st.session_state["role"]             = "patient"
                        st.session_state["username"]         = username
                        st.session_state["patient_id"]       = username
                        st.session_state["display_name"]     = f"{info.get('prenom', '')} {info.get('nom', '')}"
                        st.session_state["patient_nom"]      = info.get('nom', '')
                        st.session_state["patient_prenom"]   = info.get('prenom', '')
                        st.session_state["patient_taille"]   = info.get('taille')
                        st.session_state["medecin_referent"] = info.get('medecin_referent')

                        st.success(f"Bienvenue, {st.session_state['display_name']} !")
                        st.switch_page("pages/patient_profile.py")
                    else:
                        st.error("Nom d'utilisateur ou mot de passe incorrect.")

                except json.JSONDecodeError:
                    st.error("Erreur de lecture de la base de données.")
                except Exception as e:
                    st.error(f"Erreur de connexion : {str(e)}")

    # Lien vers espace médecin
    st.markdown(
        '<p class="doctor-link">Vous êtes médecin ? '
        '<a href="/doctor_login">Accéder à l\'espace médecin →</a></p>',
        unsafe_allow_html=True
    )

# Footer
st.markdown(
    '<p class="footer">© 2026 MediObes — Application clinique d\'aide à la décision</p>',
    unsafe_allow_html=True
)