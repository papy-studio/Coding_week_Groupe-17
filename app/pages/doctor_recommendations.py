import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="MediObes · Recommandations",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auth guard ─────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in") or st.session_state.get("role") != "doctor":
    st.markdown("""<style>
        [data-testid="stSidebar"],[data-testid="collapsedControl"],
        header[data-testid="stHeader"]{ display:none !important; }
    </style>""", unsafe_allow_html=True)
    st.switch_page("pages/doctor_login.py")

if "selected_patient_id" not in st.session_state:
    st.warning("Aucun patient sélectionné.")
    st.switch_page("pages/doctor_dashboard.py")

RECORDS_DIR = "data/records"

LABEL_FR = {
    "Insufficient_Weight":  "Poids Insuffisant",
    "Normal_Weight":        "Poids Normal",
    "Overweight_Level_I":   "Surpoids — Niveau I",
    "Overweight_Level_II":  "Surpoids — Niveau II",
    "Obesity_Type_I":       "Obésité — Type I",
    "Obesity_Type_II":      "Obésité — Type II",
    "Obesity_Type_III":     "Obésité — Type III (Morbide)",
}
LABEL_COLOR = {
    "Insufficient_Weight":  ("#2196F3", "rgba(33,150,243,0.12)"),
    "Normal_Weight":        ("#52B788", "rgba(82,183,136,0.12)"),
    "Overweight_Level_I":   ("#F4A261", "rgba(244,162,97,0.12)"),
    "Overweight_Level_II":  ("#E76F51", "rgba(231,111,81,0.12)"),
    "Obesity_Type_I":       ("#E05252", "rgba(224,82,82,0.12)"),
    "Obesity_Type_II":      ("#C62828", "rgba(198,40,40,0.12)"),
    "Obesity_Type_III":     ("#B71C1C", "rgba(183,28,28,0.12)"),
}
RECO_TEMPLATES = {
    "Insufficient_Weight": """- Augmenter progressivement les apports caloriques quotidiens (+300 a 500 kcal/j).
- Privilegier des aliments riches en nutriments : legumineuses, noix, produits laitiers, viandes maigres.
- Consulter un nutritionniste pour un plan alimentaire personnalise.
- Surveillance mensuelle du poids et de l'IMC.
- Bilan biologique recommande pour verifier les carences eventuelles.""",
    "Normal_Weight": """- Maintenir les habitudes alimentaires actuelles equilibrees.
- Conserver une activite physique reguliere (minimum 150 min/semaine).
- Suivi annuel de l'IMC et des constantes biologiques.
- Encourager la prevention : hydratation suffisante, limitation des aliments ultra-transformes.""",
    "Overweight_Level_I": """- Reduire moderement les apports caloriques (-300 a 400 kcal/j par rapport aux apports actuels).
- Augmenter l'activite physique : minimum 30 min/jour de marche rapide ou equivalent.
- Limiter les aliments ultra-transformes, sucreries et boissons sucrees.
- Favoriser les legumes, proteines maigres et grains entiers.
- Suivi mensuel du poids. Objectif : perte de 0.5 a 1 kg/semaine.""",
    "Overweight_Level_II": """- Consultation dietetique urgente pour un plan alimentaire structure.
- Reduction calorique supervisee (-500 kcal/j), jamais en dessous de 1200 kcal/j.
- Programme d'activite physique progressif : demarrer par 20 min/jour, augmenter graduellement.
- Bilan metabolique recommande (glycemie, cholesterol, tension arterielle).
- Suivi bimensuel du poids. Objectif : perte de 1 a 2 kg/semaine sur 3 mois.""",
    "Obesity_Type_I": """- Prise en charge multidisciplinaire : medecin, dieteticien, psychologue si necessaire.
- Programme de reeducation alimentaire complet sur 6 mois minimum.
- Activite physique adaptee supervisee : kinesitherapeute recommande.
- Bilan cardiologique et metabolique complet obligatoire.
- Suivi hebdomadaire du poids les 2 premiers mois, puis mensuel.
- Objectif : perte de 5 a 10% du poids initial sur 6 mois.""",
    "Obesity_Type_II": """- Orientation vers un service specialise en obesite (CHU recommande).
- Evaluation chirurgicale bariatrique possible selon criteres.
- Traitement medicamenteux a discuter avec endocrinologue.
- Programme intensif d'activite physique adaptee.
- Surveillance cardiaque et respiratoire rapprochee.
- Bilan polysomnographique (apnee du sommeil) recommande.""",
    "Obesity_Type_III": """PRISE EN CHARGE URGENTE REQUISE
- Reference immediate vers chirurgie bariatrique si eligible (IMC > 40).
- Hospitalisation possible pour bilan complet.
- Equipe pluridisciplinaire obligatoire : endocrinologue, cardiologue, pneumologue, psychologue.
- Surveillance continue des comorbidites (diabete, HTA, apnees).
- Arret de toute activite physique intense jusqu'a evaluation cardiologique.
- Objectif a 6 mois : stabilisation du poids avant intervention chirurgicale.""",
}
DIET_TEMPLATES = {
    "Insufficient_Weight": """Petit-dejeuner : flocons d'avoine (80g) + lait entier + 2 oeufs + fruit frais
Collation matin : poignee de noix + yaourt grec
Dejeuner : riz complet (150g) + poulet (150g) + legumes sautes + huile d'olive
Collation soir : pain complet + fromage
Diner : pates (120g) + saumon (120g) + salade verte + avocat
Hydratation : 1.5 a 2L d'eau/jour""",
    "Normal_Weight": """Petit-dejeuner : pain complet + oeuf + fruit frais + cafe/the
Dejeuner : legumineuses ou cereales completes + proteine maigre + legumes
Diner : poisson ou volaille + legumes vapeur + feculent en quantite moderee
Hydratation : 1.5 a 2L d'eau/jour
Snacks : fruits frais, oleagineux en petite quantite""",
    "Overweight_Level_I": """Petit-dejeuner : yaourt nature 0% + fruits rouges + flocons d'avoine (40g)
Dejeuner : salade composee + proteine maigre (120g) + pain complet (1 tranche)
Collation (si besoin) : 1 fruit frais
Diner : legumes vapeur (250g) + poisson (150g) ou legumineuses
Eviter : boissons sucrees, fast-food, grignotage apres 20h
Hydratation : 2L d'eau/jour minimum""",
    "Overweight_Level_II": """Petit-dejeuner : oeuf a la coque + legumes + cafe sans sucre
Dejeuner : proteine maigre (100g) + legumes verts (300g) + feculent limite (50g sec)
Diner : soupe de legumes maison + proteine legere
Supprimer : alcool, sodas, sucreries, plats industriels
Cuisson : vapeur, four, poele anti-adherente sans matiere grasse
Hydratation : 2L d'eau/jour minimum""",
    "Obesity_Type_I": """Plan a valider avec un dieteticien agree
Apport calorique cible : 1400-1600 kcal/jour (femme) / 1600-1800 kcal/jour (homme)
Repartition : 50% glucides complexes, 25% proteines, 25% lipides sains
Repas structures : 3 repas/jour sans grignotage
Aliments a eliminer totalement : boissons sucrees, fast-food, alcool
Portions controlees : utiliser une balance alimentaire les 2 premiers mois""",
    "Obesity_Type_II": """Plan medical obligatoire - ne pas auto-gerer
Regime hypocalorique strict sous supervision medicale (1200-1400 kcal/j)
Complements vitaminiques recommandes
Suivi hebdomadaire avec dieteticien
Tenir un journal alimentaire quotidien""",
    "Obesity_Type_III": """Regime pre-operatoire possible - consultation chirurgien bariatrique
Regime liquide ou tres basse calorie possible sur prescription medicale
Supplementation systematique : vitamines D, B12, fer, calcium
Aucun regime restrictif sans supervision medicale stricte""",
}

def load_record(pid):
    path = os.path.join(RECORDS_DIR, f"{pid}.json")
    if not os.path.exists(path):
        return {}
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            with open(path, "r", encoding=enc) as f:
                return json.load(f)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return {}

def save_record(pid, record):
    os.makedirs(RECORDS_DIR, exist_ok=True)
    path = os.path.join(RECORDS_DIR, f"{pid}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

patient_id   = st.session_state["selected_patient_id"]
patient_info = st.session_state.get("patient_info", {})
doctor_name  = st.session_state.get("display_name", "Médecin")

if "current_record" not in st.session_state or st.session_state.get("current_patient_id") != patient_id:
    st.session_state.current_record     = load_record(patient_id)
    st.session_state.current_patient_id = patient_id

record     = st.session_state.current_record
prenom     = patient_info.get("prenom") or (record.get("patient_name", "").split()[0] if record.get("patient_name") else "—")
nom        = patient_info.get("nom")    or " ".join(record.get("patient_name", "").split()[1:])
prediction = record.get("prediction", st.session_state.get("prediction", ""))
bmi        = record.get("BMI", 0)
pred_fr    = LABEL_FR.get(prediction, prediction)
accent, bg = LABEL_COLOR.get(prediction, ("#1D6996", "rgba(29,105,150,0.12)"))

if "reco_text" not in st.session_state:
    st.session_state.reco_text = record.get("recommendations", "")
if "diet_text" not in st.session_state:
    st.session_state.diet_text = record.get("diet_plan", "")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

section[data-testid="stSidebar"] { display: block !important; background-color: #0d1f35 !important; }
[data-testid="stSidebarNav"], div[data-testid="stSidebarNav"],
.css-1d391kg, .css-1lcbmhc, .css-1wrcr25,
.eczjsme11, .eczjsme12, .eczjsme13 { display: none !important; }

.stApp { background-color: #0B1628; }
.sidebar-logo { font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700; color: white; margin-bottom: 4px; }
.sidebar-logo span { color: #52B788; }
.sidebar-role { font-size: 0.72rem; color: rgba(255,255,255,0.35); letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 2rem; font-family: 'DM Sans', sans-serif; }
.user-card { background: rgba(82,183,136,0.08); border: 1px solid rgba(82,183,136,0.2); border-radius: 12px; padding: 12px 16px; margin-bottom: 2rem; }
.user-name { color: white; font-size: 0.92rem; font-weight: 500; font-family: 'DM Sans', sans-serif; }
.user-sub  { color: rgba(255,255,255,0.4); font-size: 0.75rem; margin-top: 2px; font-family: 'DM Sans', sans-serif; }
.nav-section { font-size: 0.68rem; color: rgba(255,255,255,0.25); letter-spacing: 0.12em; text-transform: uppercase; margin: 1.2rem 0 0.5rem 0; font-family: 'DM Sans', sans-serif; }
div[data-testid="stSidebar"] .stButton > button { background: transparent; color: rgba(255,255,255,0.65); border: none; border-radius: 8px; text-align: left; width: 100%; padding: 0.5rem 0.75rem; font-size: 0.88rem; font-family: 'DM Sans', sans-serif; }
div[data-testid="stSidebar"] .stButton > button:hover { background: rgba(255,255,255,0.06); color: white; }
div[data-testid="stSidebar"] [data-testid="stButton"]:last-child > button { color: #E05252 !important; }
div[data-testid="stSidebar"] [data-testid="stButton"]:last-child > button:hover { background: rgba(224,82,82,0.1) !important; }

.page-header { margin-bottom: 28px; }
.page-eyebrow { font-size: 0.72rem; color: #52B788; text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 6px; font-family: 'DM Sans', sans-serif; }
.page-title { font-family: 'Playfair Display', serif; font-size: 2.2rem; font-weight: 600; color: white; margin-bottom: 4px; }
.page-sub { font-family: 'DM Sans', sans-serif; font-size: 0.88rem; color: rgba(255,255,255,0.35); }
.patient-banner { background: var(--bg); border: 1px solid var(--accent); border-radius: 14px; padding: 20px 24px; margin-bottom: 24px; display: flex; align-items: center; gap: 20px; position: relative; overflow: hidden; }
.patient-banner::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: var(--accent); }
.banner-avatar { width: 52px; height: 52px; border-radius: 14px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.10); display: flex; align-items: center; justify-content: center; font-size: 22px; flex-shrink: 0; }
.banner-name { font-family: 'Playfair Display', serif; font-size: 20px; color: #FFFFFF; font-weight: 600; margin-bottom: 4px; }
.banner-meta { font-size: 12px; color: rgba(255,255,255,0.5); font-family: 'DM Sans', sans-serif; }
.banner-badge { margin-left: auto; font-size: 13px; font-weight: 500; padding: 8px 18px; border-radius: 20px; border: 1px solid var(--accent); color: var(--accent); background: var(--bg); white-space: nowrap; font-family: 'DM Sans', sans-serif; }
[data-testid="stTextArea"] label { display: none; }
[data-testid="stTextArea"] textarea { background: rgba(255,255,255,0.04) !important; border: 1.5px solid rgba(82,183,136,0.22) !important; border-radius: 12px !important; padding: 14px 16px !important; font-family: 'DM Sans', sans-serif !important; font-size: 14px !important; line-height: 1.7 !important; color: #FFFFFF !important; resize: vertical !important; }
[data-testid="stTextArea"] textarea:focus { border-color: #52B788 !important; box-shadow: 0 0 0 3px rgba(82,183,136,0.15) !important; background: rgba(82,183,136,0.06) !important; }
.save-btn [data-testid="stButton"] > button { background: linear-gradient(135deg, #52B788, #3d9e70) !important; color: #FFFFFF !important; border: none !important; border-radius: 10px !important; padding: 14px 0 !important; font-size: 15px !important; font-weight: 500 !important; box-shadow: 0 4px 16px rgba(82,183,136,0.30) !important; }
.back-btn [data-testid="stButton"] > button { background: transparent !important; color: rgba(255,255,255,0.65) !important; border: 1px solid rgba(255,255,255,0.15) !important; border-radius: 10px !important; padding: 13px 0 !important; font-size: 14px !important; box-shadow: none !important; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { display: flex !important; visibility: visible !important; background-color: #0B1628; }
header [data-testid="stLogo"], header [data-testid="stStatusWidget"] { display: none !important; }
.block-container { padding-top: 2rem !important; max-width: 900px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">Medi<span>Obes</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-role">Espace Médecin</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-card"><div class="user-name">🩺 {doctor_name}</div><div class="user-sub">Médecin traitant</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-section">Navigation</div>', unsafe_allow_html=True)
    if st.button("📋  Tableau de bord",  use_container_width=True, key="nav_dashboard"):       st.switch_page("pages/doctor_dashboard.py")
    if st.button("➕  Nouveau patient",  use_container_width=True, key="nav_new_patient"):     st.switch_page("pages/doctor_data_entry.py")
    if st.button("📊  Résultat",         use_container_width=True, key="nav_result"):          st.switch_page("pages/doctor_result.py")
    if st.button("📝  Recommandations",  use_container_width=True, key="nav_recommendations"): st.switch_page("pages/doctor_recommendations.py")
    st.markdown("---")
    if st.button("🚪  Se déconnecter",   use_container_width=True, key="logout"):
        st.session_state.clear()
        st.switch_page("pages/home.py")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-eyebrow">Espace Médecin · Suivi</div>
    <div class="page-title">Recommandations</div>
    <div class="page-sub">Rédigez les recommandations et le plan alimentaire pour votre patient</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="patient-banner" style="--accent:{accent}; --bg:{bg};">
    <div class="banner-avatar">👤</div>
    <div>
        <div class="banner-name">{prenom} {nom}</div>
        <div class="banner-meta">ID : {patient_id} &nbsp;·&nbsp; IMC : {bmi:.1f} kg/m² &nbsp;·&nbsp; Suivi par {doctor_name}</div>
    </div>
    <div class="banner-badge">{pred_fr}</div>
</div>
""", unsafe_allow_html=True)

col_tpl_reco, col_tpl_diet = st.columns(2)
with col_tpl_reco:
    if st.button("📄  Utiliser le modèle de recommandations", key="tpl_reco"):
        if prediction in RECO_TEMPLATES:
            st.session_state.reco_text = RECO_TEMPLATES[prediction]
            st.rerun()
with col_tpl_diet:
    if st.button("🥗  Utiliser le plan alimentaire suggéré", key="tpl_diet"):
        if prediction in DIET_TEMPLATES:
            st.session_state.diet_text = DIET_TEMPLATES[prediction]
            st.rerun()

with st.form("reco_form"):
    st.markdown("### 📋 Recommandations cliniques")
    reco_text = st.text_area("Recommandations", value=st.session_state.reco_text, height=220,
                             placeholder="Ex: Réduire les apports en sucres raffinés…",
                             label_visibility="collapsed")
    st.caption(f"{len(reco_text)} caractères")
    st.markdown("### 🥗 Plan alimentaire")
    diet_text = st.text_area("Plan alimentaire", value=st.session_state.diet_text, height=200,
                             placeholder="Ex: Petit-déjeuner : yaourt + fruits…",
                             label_visibility="collapsed")
    st.caption(f"{len(diet_text)} caractères")
    col_save, col_back = st.columns([1.8, 1.5])
    with col_save:
        st.markdown('<div class="save-btn">', unsafe_allow_html=True)
        save_btn = st.form_submit_button("💾  Sauvegarder les recommandations", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_back:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        back_btn = st.form_submit_button("← Retour au résultat", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

if save_btn:
    if not reco_text.strip() and not diet_text.strip():
        st.error("⚠️ Veuillez rédiger au moins les recommandations avant de sauvegarder.")
    else:
        try:
            updated_record = {
                **record,
                "recommendations": reco_text.strip(),
                "diet_plan":       diet_text.strip(),
                "reco_date":       datetime.now().strftime("%d/%m/%Y à %H:%M"),
                "reco_author":     doctor_name,
            }
            save_record(patient_id, updated_record)
            st.session_state.current_record = updated_record
            st.session_state.reco_text = reco_text.strip()
            st.session_state.diet_text = diet_text.strip()
            st.success(f"✅ Recommandations sauvegardées pour {prenom} {nom}.")
            st.info("💡 Le patient peut désormais les consulter depuis son espace personnel.")
        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde : {e}")

if back_btn:
    st.switch_page("pages/doctor_result.py")