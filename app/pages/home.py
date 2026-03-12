import streamlit as st

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediObes · Accueil",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Hide sidebar & header completely ──────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
header[data-testid="stHeader"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Full CSS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Reset & background ── */
html, body { margin: 0; padding: 0; }

[data-testid="stAppViewContainer"] {
    min-height: 100vh;
    background: #0B1628;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse at 15% 40%, rgba(29,105,150,0.22) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 20%, rgba(82,183,136,0.14) 0%, transparent 50%),
        radial-gradient(ellipse at 60% 80%, rgba(29,105,150,0.10) 0%, transparent 45%);
    pointer-events: none;
    z-index: 0;
}

[data-testid="stMain"] {
    position: relative;
    z-index: 1;
}

[data-testid="block-container"] {
    padding-top: 0 !important;
    max-width: 860px;
}

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 72px 24px 48px;
    animation: fadeUp 0.7s cubic-bezier(.22,1,.36,1) both;
}

.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(29,105,150,0.18);
    border: 1px solid rgba(29,105,150,0.35);
    border-radius: 100px;
    padding: 5px 16px;
    font-size: 11.5px;
    font-weight: 500;
    color: #7EC8E3;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 28px;
}

.hero-eyebrow-dot {
    width: 6px; height: 6px;
    background: #52B788;
    border-radius: 50%;
    animation: pulse 2s ease infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.5; transform: scale(0.8); }
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 58px;
    font-weight: 600;
    line-height: 1.1;
    color: #FFFFFF;
    letter-spacing: -1.5px;
    margin-bottom: 8px;
}

.hero-title span {
    color: transparent;
    background: linear-gradient(135deg, #52B788, #7EC8E3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-tagline {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 18px;
    color: #6A8AA0;
    margin-bottom: 16px;
    letter-spacing: 0.2px;
}

.hero-desc {
    font-size: 14.5px;
    color: #5A7A8A;
    line-height: 1.7;
    max-width: 520px;
    margin: 0 auto 48px;
    font-weight: 300;
}

/* ── Divider label ── */
.choose-label {
    text-align: center;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #2A4A5A;
    margin-bottom: 24px;
    position: relative;
    animation: fadeUp 0.7s 0.15s cubic-bezier(.22,1,.36,1) both;
}

.choose-label::before,
.choose-label::after {
    content: '';
    position: absolute;
    top: 50%;
    width: 28%;
    height: 1px;
    background: linear-gradient(to var(--dir), #1D3A50, transparent);
}
.choose-label::before { left: 0;   --dir: right; }
.choose-label::after  { right: 0;  --dir: left; }

/* ── Cards grid ── */
.cards-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 48px;
    animation: fadeUp 0.7s 0.25s cubic-bezier(.22,1,.36,1) both;
}

/* ── Path card ── */
.path-card {
    position: relative;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 36px 32px 32px;
    cursor: pointer;
    transition: transform 0.25s cubic-bezier(.22,1,.36,1),
                border-color 0.25s,
                background 0.25s,
                box-shadow 0.25s;
    overflow: hidden;
    text-decoration: none;
}

.path-card::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 20px;
    opacity: 0;
    transition: opacity 0.3s;
}

.path-card.doctor::before {
    background: radial-gradient(ellipse at 30% 30%, rgba(29,105,150,0.15), transparent 70%);
}
.path-card.patient::before {
    background: radial-gradient(ellipse at 30% 30%, rgba(82,183,136,0.15), transparent 70%);
}

.path-card:hover {
    transform: translateY(-6px);
    border-color: rgba(255,255,255,0.16);
    background: rgba(255,255,255,0.06);
}
.path-card.doctor:hover { box-shadow: 0 20px 48px rgba(29,105,150,0.22); }
.path-card.patient:hover { box-shadow: 0 20px 48px rgba(82,183,136,0.18); }
.path-card:hover::before { opacity: 1; }

/* Card top accent line */
.path-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 20px 20px 0 0;
    opacity: 0;
    transition: opacity 0.3s;
}
.path-card.doctor::after  { background: linear-gradient(to right, #1D6996, #7EC8E3); }
.path-card.patient::after { background: linear-gradient(to right, #52B788, #A8E6CF); }
.path-card:hover::after   { opacity: 1; }

/* Icon */
.card-icon {
    width: 56px; height: 56px;
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    font-size: 26px;
    margin-bottom: 20px;
    position: relative;
}
.doctor  .card-icon { background: rgba(29,105,150,0.20); }
.patient .card-icon { background: rgba(82,183,136,0.18); }

.card-role {
    font-size: 10.5px;
    font-weight: 500;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.doctor  .card-role { color: #4A9EC0; }
.patient .card-role { color: #52B788; }

.card-title {
    font-family: 'Playfair Display', serif;
    font-size: 26px;
    font-weight: 600;
    color: #FFFFFF;
    margin-bottom: 12px;
    letter-spacing: -0.5px;
}

.card-desc {
    font-size: 13px;
    color: #4A6A7A;
    line-height: 1.65;
    font-weight: 300;
    margin-bottom: 24px;
}

/* Feature list */
.card-features {
    list-style: none;
    padding: 0; margin: 0 0 28px;
}
.card-features li {
    font-size: 12.5px;
    color: #3A5A6A;
    padding: 5px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.card-features li::before {
    content: '';
    width: 5px; height: 5px;
    border-radius: 50%;
    flex-shrink: 0;
}
.doctor  .card-features li::before { background: #1D6996; }
.patient .card-features li::before { background: #52B788; }

/* CTA inside card */
.card-cta {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 13.5px;
    font-weight: 500;
    padding: 10px 20px;
    border-radius: 10px;
    border: 1px solid;
    transition: background 0.2s, color 0.2s;
}
.doctor  .card-cta { color: #7EC8E3; border-color: rgba(29,105,150,0.4); }
.patient .card-cta { color: #52B788; border-color: rgba(82,183,136,0.4); }
.path-card:hover .card-cta { }
.doctor:hover  .card-cta { background: rgba(29,105,150,0.15); }
.patient:hover .card-cta { background: rgba(82,183,136,0.12); }

/* ── Footer ── */
.home-footer {
    text-align: center;
    font-size: 11.5px;
    color: #1E3040;
    padding-bottom: 40px;
    animation: fadeUp 0.7s 0.35s cubic-bezier(.22,1,.36,1) both;
}
.home-footer strong { color: #2A4A5A; }

/* ── Stats strip ── */
.stats-strip {
    display: flex;
    justify-content: center;
    gap: 48px;
    margin-bottom: 48px;
    animation: fadeUp 0.7s 0.2s cubic-bezier(.22,1,.36,1) both;
}
.stat-item { text-align: center; }
.stat-num {
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    color: #FFFFFF;
    font-weight: 600;
    letter-spacing: -0.5px;
}
.stat-label {
    font-size: 11px;
    color: #2A4A5A;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 2px;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">
        <span class="hero-eyebrow-dot"></span>
        Centrale Casablanca · Coding Week 2026
    </div>
    <div class="hero-title">Medi<span>Obes</span></div>
    <div class="hero-tagline">"Estimer le risque d'obésité, puis accompagner le patient."</div>
    <div class="hero-desc">
        Outil clinique d'aide à la décision médicale basé sur le machine learning et 
        l'explicabilité SHAP. Une plateforme partagée entre médecins et patients pour 
        un suivi continu et personnalisé.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Stats strip ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="stats-strip">
    <div class="stat-item">
        <div class="stat-num">7</div>
        <div class="stat-label">Niveaux d'obésité</div>
    </div>
    <div class="stat-item">
        <div class="stat-num">16</div>
        <div class="stat-label">Features cliniques</div>
    </div>
    <div class="stat-item">
        <div class="stat-num">SHAP</div>
        <div class="stat-label">Explicabilité</div>
    </div>
    <div class="stat-item">
        <div class="stat-num">2</div>
        <div class="stat-label">Espaces dédiés</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Choose label ──────────────────────────────────────────────────────────────
st.markdown('<div class="choose-label">Choisissez votre espace</div>', unsafe_allow_html=True)

# ── Cards (HTML only for layout, buttons below) ───────────────────────────────
st.markdown("""
<div class="cards-grid">

    <!-- Médecin -->
    <div class="path-card doctor">
        <div class="card-icon">🩺</div>
        <div class="card-role">Personnel médical</div>
        <div class="card-title">Espace<br>Médecin</div>
        <div class="card-desc">
            Accédez au tableau de bord clinique, 
            analysez le risque d'obésité de vos patients 
            et rédigez des recommandations personnalisées.
        </div>
        <ul class="card-features">
            <li>Tableau de bord patients</li>
            <li>Saisie des données cliniques</li>
            <li>Prédiction + explication SHAP</li>
            <li>Rédaction des recommandations</li>
        </ul>
    </div>

    <!-- Patient -->
    <div class="path-card patient">
        <div class="card-icon">👤</div>
        <div class="card-role">Espace personnel</div>
        <div class="card-title">Espace<br>Patient</div>
        <div class="card-desc">
            Consultez votre niveau de risque, lisez 
            les recommandations de votre médecin et 
            suivez l'évolution de votre poids semaine après semaine.
        </div>
        <ul class="card-features">
            <li>Résultat & IMC personnalisé</li>
            <li>Recommandations du médecin</li>
            <li>Suivi poids hebdomadaire</li>
            <li>Alertes automatiques</li>
        </ul>
    </div>

</div>
""", unsafe_allow_html=True)

# ── Streamlit buttons (invisible but functional) ──────────────────────────────
col_doc, col_pat = st.columns(2)

with col_doc:
    if st.button("🩺  Accéder — Espace Médecin", use_container_width=True, key="btn_doctor"):
        st.switch_page("pages/doctor_login.py")

with col_pat:
    if st.button("👤  Accéder — Espace Patient", use_container_width=True, key="btn_patient"):
        st.switch_page("pages/patient_login.py")

# ── Button styling ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
div[data-testid="column"]:nth-child(1) [data-testid="stButton"] > button {
    background: linear-gradient(135deg, #1D6996, #155a7a) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14.5px !important;
    font-weight: 500 !important;
    letter-spacing: 0.2px !important;
    box-shadow: 0 4px 20px rgba(29,105,150,0.35) !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
    margin-top: -12px;
}
div[data-testid="column"]:nth-child(1) [data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(29,105,150,0.45) !important;
}

div[data-testid="column"]:nth-child(2) [data-testid="stButton"] > button {
    background: linear-gradient(135deg, #52B788, #3d9e70) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14.5px !important;
    font-weight: 500 !important;
    letter-spacing: 0.2px !important;
    box-shadow: 0 4px 20px rgba(82,183,136,0.32) !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
    margin-top: -12px;
}
div[data-testid="column"]:nth-child(2) [data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(82,183,136,0.42) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="home-footer">
    <strong>MediObes</strong> · Centrale Casablanca · Coding Week Mars 2026<br>
    Accès réservé au personnel médical autorisé et aux patients enregistrés
</div>
""", unsafe_allow_html=True)