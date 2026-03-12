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