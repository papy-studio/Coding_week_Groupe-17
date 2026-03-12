import streamlit as st
import json
import os
from datetime import datetime

# ── Page config ────────────────────────────────────────────────────────────────
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

# ── Paths ──────────────────────────────────────────────────────────────────────
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

# ── Load record ────────────────────────────────────────────────────────────────
def load_record(pid):
    path = os.path.join(RECORDS_DIR, f"{pid}.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_record(pid, record):
    os.makedirs(RECORDS_DIR, exist_ok=True)
    path = os.path.join(RECORDS_DIR, f"{pid}.json")
    with open(path, "w") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

# ── Load data ──────────────────────────────────────────────────────────────────
patient_id   = st.session_state["selected_patient_id"]
patient_info = st.session_state.get("patient_info", {})
record       = load_record(patient_id)

prenom       = patient_info.get("prenom") or record.get("patient_name", "").split()[0]
nom          = patient_info.get("nom")    or " ".join(record.get("patient_name", "").split()[1:])
prediction   = record.get("prediction", st.session_state.get("prediction", ""))
bmi          = record.get("BMI", 0)
pred_fr      = LABEL_FR.get(prediction, prediction)
accent, bg   = LABEL_COLOR.get(prediction, ("#1D6996", "rgba(29,105,150,0.12)"))
existing_reco = record.get("recommendations", "")
existing_diet = record.get("diet_plan", "")
last_updated  = record.get("reco_date", "")

# ── Templates par niveau d'obésité ────────────────────────────────────────────
RECO_TEMPLATES = {
    "Insufficient_Weight": """• Augmenter progressivement les apports caloriques quotidiens (+300 à 500 kcal/j).
• Privilégier des aliments riches en nutriments : légumineuses, noix, produits laitiers, viandes maigres.
• Consulter un nutritionniste pour un plan alimentaire personnalisé.
• Surveillance mensuelle du poids et de l'IMC.
• Bilan biologique recommandé pour vérifier les carences éventuelles.""",

    "Normal_Weight": """• Maintenir les habitudes alimentaires actuelles équilibrées.
• Conserver une activité physique régulière (minimum 150 min/semaine).
• Suivi annuel de l'IMC et des constantes biologiques.
• Encourager la prévention : hydratation suffisante, limitation des aliments ultra-transformés.""",

    "Overweight_Level_I": """• Réduire modérément les apports caloriques (-300 à 400 kcal/j par rapport aux apports actuels).
• Augmenter l'activité physique : minimum 30 min/jour de marche rapide ou équivalent.
• Limiter les aliments ultra-transformés, sucreries et boissons sucrées.
• Favoriser les légumes, protéines maigres et grains entiers.
• Suivi mensuel du poids. Objectif : perte de 0.5 à 1 kg/semaine.""",

    "Overweight_Level_II": """• Consultation diététique urgente pour un plan alimentaire structuré.
• Réduction calorique supervisée (-500 kcal/j), jamais en dessous de 1200 kcal/j.
• Programme d'activité physique progressif : démarrer par 20 min/jour, augmenter graduellement.
• Bilan métabolique recommandé (glycémie, cholestérol, tension artérielle).
• Suivi bimensuel du poids. Objectif : perte de 1 à 2 kg/semaine sur 3 mois.""",

    "Obesity_Type_I": """• Prise en charge multidisciplinaire : médecin, diététicien, psychologue si nécessaire.
• Programme de rééducation alimentaire complet sur 6 mois minimum.
• Activité physique adaptée supervisée : kinésithérapeute recommandé.
• Bilan cardiologique et métabolique complet obligatoire.
• Suivi hebdomadaire du poids les 2 premiers mois, puis mensuel.
• Objectif : perte de 5 à 10% du poids initial sur 6 mois.""",

    "Obesity_Type_II": """• Orientation vers un service spécialisé en obésité (CHU recommandé).
• Évaluation chirurgicale bariatrique possible selon critères.
• Traitement médicamenteux à discuter avec endocrinologue.
• Programme intensif d'activité physique adaptée.
• Surveillance cardiaque et respiratoire rapprochée.
• Bilan polysomnographique (apnée du sommeil) recommandé.""",

    "Obesity_Type_III": """🚨 PRISE EN CHARGE URGENTE REQUISE
• Référence immédiate vers chirurgie bariatrique si eligible (IMC > 40).
• Hospitalisation possible pour bilan complet.
• Équipe pluridisciplinaire obligatoire : endocrinologue, cardiologue, pneumologue, psychologue.
• Surveillance continue des comorbidités (diabète, HTA, apnées).
• Arrêt de toute activité physique intense jusqu'à évaluation cardiologique.
• Objectif à 6 mois : stabilisation du poids avant intervention chirurgicale.""",
}

DIET_TEMPLATES = {
    "Insufficient_Weight": """Petit-déjeuner : flocons d'avoine (80g) + lait entier + 2 œufs + fruit frais
Collation matin : poignée de noix + yaourt grec
Déjeuner : riz complet (150g) + poulet (150g) + légumes sautés + huile d'olive
Collation soir : pain complet + fromage
Dîner : pâtes (120g) + saumon (120g) + salade verte + avocat
Hydratation : 1.5 à 2L d'eau/jour""",

    "Normal_Weight": """Petit-déjeuner : pain complet + œuf + fruit frais + café/thé
Déjeuner : légumineuses ou céréales complètes + protéine maigre + légumes
Dîner : poisson ou volaille + légumes vapeur + féculent en quantité modérée
Hydratation : 1.5 à 2L d'eau/jour
Snacks : fruits frais, oléagineux en petite quantité""",

    "Overweight_Level_I": """Petit-déjeuner : yaourt nature 0% + fruits rouges + flocons d'avoine (40g)
Déjeuner : salade composée + protéine maigre (120g) + pain complet (1 tranche)
Collation (si besoin) : 1 fruit frais
Dîner : légumes vapeur (250g) + poisson (150g) ou légumineuses
Éviter : boissons sucrées, fast-food, grignotage après 20h
Hydratation : 2L d'eau/jour minimum""",

    "Overweight_Level_II": """Petit-déjeuner : œuf à la coque + légumes + café sans sucre
Déjeuner : protéine maigre (100g) + légumes verts (300g) + féculents limités (50g sec)
Dîner : soupe de légumes maison + protéine légère
Supprimer : alcool, sodas, sucreries, plats industriels
Cuisson : vapeur, four, poêle anti-adhésive sans matière grasse
Hydratation : 2L d'eau/jour minimum""",

    "Obesity_Type_I": """⚠️ Plan à valider avec un diététicien agréé
Apport calorique cible : 1400–1600 kcal/jour (femme) / 1600–1800 kcal/jour (homme)
Répartition : 50% glucides complexes, 25% protéines, 25% lipides sains
Repas structurés : 3 repas/jour sans grignotage
Aliments à éliminer totalement : boissons sucrées, fast-food, alcool
Portions contrôlées : utiliser une balance alimentaire les 2 premiers mois""",

    "Obesity_Type_II": """⚠️ Plan médical obligatoire — ne pas auto-gérer
Régime hypocalorique strict sous supervision médicale (1200–1400 kcal/j)
Compléments vitaminiques recommandés
Suivi hebdomadaire avec diététicien
Tenir un journal alimentaire quotidien""",

    "Obesity_Type_III": """🚨 Régime pré-opératoire possible — consultation chirurgien bariatrique
Régime liquide ou très basse calorie possible sur prescription médicale
Supplémentation systématique : vitamines D, B12, fer, calcium
Aucun régime restrictif sans supervision médicale stricte""",
}

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'DM Sans', sans-serif; background: #0B1628;
}
[data-testid="stAppViewContainer"]::before {
    content: ''; position: fixed; inset: 0;
    background:
        radial-gradient(ellipse at 10% 30%, rgba(29,105,150,0.15) 0%, transparent 55%),
        radial-gradient(ellipse at 90% 70%, rgba(29,105,150,0.08) 0%, transparent 50%);
    pointer-events: none; z-index: 0;
}
[data-testid="stMain"] { position: relative; z-index: 1; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: #0D1E30 !important; border-right: 1px solid rgba(29,105,150,0.15) !important; }
[data-testid="stSidebar"] * { color: #4A7A9A !important; }
[data-testid="stSidebar"] hr { border-color: rgba(29,105,150,0.15) !important; margin: 14px 0; }
.sb-logo { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 600; color: #FFFFFF !important; letter-spacing: -0.3px; margin-bottom: 2px; }
.sb-logo span { color: transparent; background: linear-gradient(135deg,#52B788,#7EC8E3); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.sb-tagline { font-size: 11px; color: #1D3A50 !important; margin-bottom: 20px; }
.sb-user { background: rgba(29,105,150,0.12); border: 1px solid rgba(29,105,150,0.20); border-radius: 12px; padding: 12px 14px; margin-bottom: 4px; }
.sb-user-name { font-size: 13.5px; font-weight: 500; color: #FFFFFF !important; }
.sb-user-role { font-size: 11px; color: #52B788 !important; margin-top: 2px; }
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: rgba(29,105,150,0.12) !important; color: #4A7A9A !important;
    border: 1px solid rgba(29,105,150,0.20) !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 13px !important;
    box-shadow: none !important; transition: background 0.2s !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: rgba(29,105,150,0.22) !important; color: #7EC8E3 !important; transform: none !important;
}

/* ── Page header ── */
.page-header { margin-bottom: 28px; }
.page-eyebrow { font-size: 11px; font-weight: 500; letter-spacing: 1.5px; text-transform: uppercase; color: #1D4A6A; margin-bottom: 6px; }
.page-title { font-family: 'Playfair Display', serif; font-size: 34px; font-weight: 600; color: #FFFFFF; letter-spacing: -0.8px; margin-bottom: 4px; }
.page-sub { font-size: 14px; color: #1D3A50; font-weight: 300; }

/* ── Patient summary banner ── */
.patient-banner {
    background: var(--bg);
    border: 1px solid var(--accent);
    border-radius: 14px; padding: 20px 24px;
    margin-bottom: 24px;
    display: flex; align-items: center; gap: 20px;
    position: relative; overflow: hidden;
}
.patient-banner::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: var(--accent);
}
.banner-avatar {
    width: 52px; height: 52px; border-radius: 14px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; flex-shrink: 0;
}
.banner-name { font-family: 'Playfair Display', serif; font-size: 20px; color: #FFFFFF; font-weight: 600; margin-bottom: 4px; }
.banner-meta { font-size: 12px; color: #2A5A7A; }
.banner-badge {
    margin-left: auto; font-size: 13px; font-weight: 500;
    padding: 8px 18px; border-radius: 20px;
    border: 1px solid var(--accent); color: var(--accent);
    background: var(--bg); white-space: nowrap;
}

/* ── Section card ── */
.section-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 28px 32px; margin-bottom: 20px;
    position: relative; overflow: hidden;
}
.section-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: var(--top, linear-gradient(to right, #1D6996, #7EC8E3));
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 17px; color: #7EC8E3; margin-bottom: 8px;
    display: flex; align-items: center; gap: 8px;
}
.section-title::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(to right, rgba(29,105,150,0.3), transparent); margin-left: 8px;
}
.section-hint { font-size: 12.5px; color: #1D3A50; margin-bottom: 18px; font-weight: 300; }

/* ── Textarea override ── */
[data-testid="stTextArea"] label { display: none; }
[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1.5px solid rgba(29,105,150,0.22) !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important; line-height: 1.7 !important;
    color: #FFFFFF !important;
    resize: vertical !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #1D6996 !important;
    box-shadow: 0 0 0 3px rgba(29,105,150,0.15) !important;
    background: rgba(29,105,150,0.06) !important;
}

/* ── Template chips ── */
.template-label { font-size: 12px; color: #1D4A6A; margin-bottom: 10px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
.tpl-btn [data-testid="stButton"] > button {
    background: rgba(29,105,150,0.10) !important; color: #4A9EC0 !important;
    border: 1px solid rgba(29,105,150,0.25) !important; border-radius: 20px !important;
    padding: 6px 16px !important; font-size: 12.5px !important;
    font-family: 'DM Sans', sans-serif !important; box-shadow: none !important;
    transition: background 0.2s !important;
}
.tpl-btn [data-testid="stButton"] > button:hover {
    background: rgba(29,105,150,0.22) !important; color: #7EC8E3 !important; transform: none !important;
}

/* ── Save button ── */
.save-btn [data-testid="stButton"] > button {
    background: linear-gradient(135deg, #52B788, #3d9e70) !important;
    color: #FFFFFF !important; border: none !important; border-radius: 10px !important;
    padding: 14px 0 !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important; font-weight: 500 !important;
    box-shadow: 0 4px 16px rgba(82,183,136,0.30) !important;
}
.save-btn [data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important; box-shadow: 0 8px 24px rgba(82,183,136,0.40) !important;
}

/* ── Back button ── */
.back-btn [data-testid="stButton"] > button {
    background: transparent !important; color: #4A7A9A !important;
    border: 1px solid rgba(29,105,150,0.25) !important; border-radius: 10px !important;
    padding: 13px 0 !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important; box-shadow: none !important;
}
.back-btn [data-testid="stButton"] > button:hover {
    background: rgba(29,105,150,0.10) !important; color: #7EC8E3 !important; transform: none !important;
}

/* ── Last updated ── */
.last-updated {
    font-size: 11.5px; color: #1D3A50;
    margin-top: 8px; font-style: italic;
}

/* ── Char counter ── */
.char-count { font-size: 11px; color: #1D3A50; text-align: right; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">Medi<span>Obes</span></div>
    <div class="sb-tagline">Espace Médecin</div>
    <hr>
    """, unsafe_allow_html=True)
    display_name = st.session_state.get("display_name", "Médecin")
    st.markdown(f"""
    <div class="sb-user">
        <div class="sb-user-name">🩺 {display_name}</div>
        <div class="sb-user-role">● Médecin connecté</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.page_link("pages/doctor_dashboard.py",  label="🏠  Tableau de bord")
    st.page_link("pages/doctor_data_entry.py", label="➕  Nouveau patient")
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("🚪  Se déconnecter", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/home.py")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
    <div class="page-eyebrow">Espace Médecin · Suivi</div>
    <div class="page-title">Recommandations</div>
    <div class="page-sub">Rédigez les recommandations et le plan alimentaire pour votre patient</div>
</div>
""", unsafe_allow_html=True)

# ── Patient banner ────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="patient-banner" style="--accent:{accent}; --bg:{bg};">
    <div class="banner-avatar">👤</div>
    <div>
        <div class="banner-name">{prenom} {nom}</div>
        <div class="banner-meta">
            ID : {patient_id}
            &nbsp;·&nbsp; IMC : {bmi:.1f} kg/m²
            &nbsp;·&nbsp; Suivi par {display_name}
        </div>
    </div>
    <div class="banner-badge">{pred_fr}</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Recommandations cliniques
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-card" style="--top: linear-gradient(to right,#1D6996,#7EC8E3);">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📋 &nbsp;Recommandations cliniques</div>', unsafe_allow_html=True)
st.markdown('<div class="section-hint">Rédigez vos recommandations personnalisées. Le patient pourra les consulter depuis son espace.</div>', unsafe_allow_html=True)

# Bouton template
st.markdown('<div class="template-label">Charger un modèle</div>', unsafe_allow_html=True)
st.markdown('<div class="tpl-btn">', unsafe_allow_html=True)
load_reco_tpl = st.button("📄  Utiliser le modèle pour ce niveau d'obésité", key="tpl_reco")
st.markdown('</div>', unsafe_allow_html=True)

# Initialiser le contenu
if "reco_text" not in st.session_state:
    st.session_state["reco_text"] = existing_reco

if load_reco_tpl and prediction in RECO_TEMPLATES:
    st.session_state["reco_text"] = RECO_TEMPLATES[prediction]

reco_text = st.text_area(
    "reco",
    value=st.session_state["reco_text"],
    height=220,
    placeholder="Ex: Réduire les apports en sucres raffinés, augmenter l'activité physique à 30 min/jour...",
    label_visibility="collapsed",
)
st.session_state["reco_text"] = reco_text

st.markdown(f'<div class="char-count">{len(reco_text)} caractères</div>', unsafe_allow_html=True)

if last_updated:
    st.markdown(f'<div class="last-updated">Dernière mise à jour : {last_updated}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Plan alimentaire
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-card" style="--top: linear-gradient(to right,#52B788,#7EC8E3);">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🥗 &nbsp;Plan alimentaire</div>', unsafe_allow_html=True)
st.markdown('<div class="section-hint">Proposez un plan de repas hebdomadaire adapté au profil du patient.</div>', unsafe_allow_html=True)

st.markdown('<div class="template-label">Charger un modèle</div>', unsafe_allow_html=True)
st.markdown('<div class="tpl-btn">', unsafe_allow_html=True)
load_diet_tpl = st.button("🥗  Utiliser le plan alimentaire suggéré", key="tpl_diet")
st.markdown('</div>', unsafe_allow_html=True)

if "diet_text" not in st.session_state:
    st.session_state["diet_text"] = existing_diet

if load_diet_tpl and prediction in DIET_TEMPLATES:
    st.session_state["diet_text"] = DIET_TEMPLATES[prediction]

diet_text = st.text_area(
    "diet",
    value=st.session_state["diet_text"],
    height=200,
    placeholder="Ex: Petit-déjeuner : yaourt + fruits, Déjeuner : protéine maigre + légumes...",
    label_visibility="collapsed",
)
st.session_state["diet_text"] = diet_text

st.markdown(f'<div class="char-count">{len(diet_text)} caractères</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ACTIONS
# ══════════════════════════════════════════════════════════════════════════════
col_save, col_back, _ = st.columns([1.8, 1.5, 4])

with col_save:
    st.markdown('<div class="save-btn">', unsafe_allow_html=True)
    save_btn = st.button("💾  Sauvegarder les recommandations", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_back:
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    back_btn = st.button("← Retour au résultat", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Save logic ─────────────────────────────────────────────────────────────────
if save_btn:
    if not reco_text.strip() and not diet_text.strip():
        st.warning("⚠️ Veuillez rédiger au moins les recommandations avant de sauvegarder.")
    else:
        try:
            updated_record = {
                **record,
                "recommendations": reco_text.strip(),
                "diet_plan":        diet_text.strip(),
                "reco_date":        datetime.now().strftime("%d/%m/%Y à %H:%M"),
                "reco_author":      display_name,
            }
            save_record(patient_id, updated_record)

            # Nettoyer le cache session
            st.session_state.pop("reco_text", None)
            st.session_state.pop("diet_text", None)

            st.success(f"✅ Recommandations sauvegardées pour {prenom} {nom}.")
            st.info("💡 Le patient peut désormais les consulter depuis son espace personnel.")
        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde : {e}")

if back_btn:
    st.switch_page("pages/doctor_result.py")