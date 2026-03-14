import streamlit as st
import json, os

def init_data_files():
    os.makedirs("data/records", exist_ok=True)
    os.makedirs("data/tracking", exist_ok=True)

    if not os.path.exists("data/doctors.json"):
        with open("data/doctors.json", "w") as f:
            json.dump({
                "dr.martin": {"password": "medic123", "name": "Dr. Sophie Martin"},
                "dr.hassan": {"password": "medic456", "name": "Dr. Karim Hassan"},
            }, f, indent=2, ensure_ascii=False)

    if not os.path.exists("data/patients.json"):
        with open("data/patients.json", "w") as f:
            json.dump({}, f, indent=2)

init_data_files()
st.switch_page("pages/home.py")
st.markdown("""
<style>
/* Texte visible dans tous les inputs */
input, textarea {
    color: #FFFFFF !important;
    caret-color: #FFFFFF !important;
    background-color: #1A2B40 !important;
}

input::placeholder, textarea::placeholder {
    color: #8AA4BF !important;
}

/* Fix autofill Mac/Safari */
input:-webkit-autofill {
    -webkit-text-fill-color: #FFFFFF !important;
    -webkit-box-shadow: 0 0 0px 1000px #1A2B40 inset !important;
}

/* Selectbox */
[data-testid="stSelectbox"] div {
    color: #FFFFFF !important;
    background-color: #1A2B40 !important;
}

/* Labels */
label {
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

init_data_files()
st.switch_page("pages/home.py")