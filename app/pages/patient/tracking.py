import panda as pd 
import plotly.express as px
import streamlit as st
from datetime import date

SUIVI_FILE = "suivi.csv"

# --- Saisie du poids ---
def saisir_poids(patient_id: str, poids: float):
    new_row = pd.DataFrame([{
        "patient_id": patient_id,
        "date": date.today(),
        "poids": poids
    }])
    try:
        df = pd.read_csv(SUIVI_FILE)
        df = pd.concat([df, new_row], ignore_index=True)
    except FileNotFoundError:
        df = new_row
    df.to_csv(SUIVI_FILE, index=False)

# --- Charger l'historique d'un patient ---
def charger_suivi(patient_id: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(SUIVI_FILE)
        df = df[df["patient_id"] == patient_id].copy()
        df["date"] = pd.to_datetime(df["date"])
        return df.sort_values("date")
    except FileNotFoundError:
        return pd.DataFrame(columns=["patient_id", "date", "poids"])

# --- Graphique d'évolution ---
def afficher_graphique(df: pd.DataFrame):
    fig = px.line(df, x="date", y="poids", markers=True,
                  title="Évolution du poids",
                  labels={"poids": "Poids (kg)", "date": "Date"})
    st.plotly_chart(fig)

# --- Logique des alertes ---
def verifier_alertes(df: pd.DataFrame, imc: float) -> str:
    if len(df) < 2:
        return None

    poids = df["poids"].tolist()
    derniers = poids[-2:]  # 2 dernières semaines

    # Poids en hausse 2 semaines consécutives
    if len(derniers) == 2 and derniers[-1] > derniers[-2]:
        return "⚠️ Votre poids augmente depuis 2 semaines. Consultez votre médecin."

    # Poids stable (variation < 0.5 kg sur 3 semaines)
    if len(poids) >= 3:
        variation = max(poids[-3:]) - min(poids[-3:])
        if variation < 0.5:
            return "💪 Votre poids est stable. Continuez vos efforts !"

    # IMC critique après 1 mois (4 entrées)
    if len(df) >= 4 and imc >= 30:
        return "🚨 Alerte : IMC toujours critique après 1 mois. Consultez en urgence."

    # Baisse régulière
    if all(poids[i] > poids[i+1] for i in range(-3, -1)):
        return "✅ Bravo ! Votre poids est en baisse régulière. Continuez ainsi !"

    return None

# --- Page Streamlit complète ---
def page_suivi(patient_id: str, imc: float):
    st.title("📊 Fiche de Suivi Hebdomadaire")

    # Saisie
    st.subheader("Saisir mon poids cette semaine")
    poids = st.number_input("Poids (kg)", min_value=30.0, max_value=300.0, step=0.1)
    if st.button("Enregistrer"):
        saisir_poids(patient_id, poids)
        st.success("Poids enregistré !")

    # Historique
    df = charger_suivi(patient_id)
    if df.empty:
        st.info("Aucune donnée de suivi pour l'instant.")
        return

    # Graphique
    afficher_graphique(df)

    # Alertes
    alerte = verifier_alertes(df, imc)
    if alerte:
        st.warning(alerte)