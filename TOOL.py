import streamlit as st 
import pandas as pd
import numpy as np
import math
import random


st.set_page_config(page_title="Stützen-Stütze", layout="centered", page_icon=("🚩"))
initial_sidebar_state="expanded"



with st.container():
    st.title("Stützen-Stütze")
    st.subheader("Das TRAKO Tool zur Vordimensionierung von Stützenquerschnitten")
    st.write("##")
    st.write("Dieses Tool ist von und für Architekturstudierende, die schnell und einfach plausible Stützenquerschnitte für ihre Entwürfe benötigen.")
    st.write("Jegliche Berechnungen dienen der Vordimensionierung und sind keine vollständige Überprüfung der Statik deines Entwurfs.")
    st.write("Dieses Tool dient nur der Berechnung von Stützen von einfachen Hallentragwerken. Hierbei stehen die Stützenreihen links und rechts der Halle und werden von einem Einfeldträger überspannt. ")  

with st.container():
    st.write("---")
    st.subheader("Gib die Hardfacts deiner Stütze an:")
    spalten=st.columns(2)
    with spalten[0]:
        F = st.number_input("Gebe die auf die Stütze wirkende Normalkraft in kN ein:")
        laenge = st.number_input("Gib die Höhe der zu berechnenden Stütze in Meter ein:")
        stuetzenabstand = st.number_input("Gib den Abstand der Stützen ein:")
    with spalten[1]:
        EF = st.selectbox("Wähle den Eulerfall der Stütze aus", ["1","2","3","4"])
        b= st.number_input("Gebe die feste Breite deiner Stütze in cm ein:")

st.write("---")

with st.container():
    st.subheader("Konfiguriere deine Stütze")
    spalten=st.columns(2)
    with spalten[0]:
        material_auswahl = st.selectbox("Wähle das Material deiner Stütze:", (["Holz", "Stahl"]))
    with spalten[1]:
        if material_auswahl == "Holz":
            optionen = ["KVH","BSH"]
        else:
            optionen = ["HEB", "IPE", "Quadratrohr"]
        wahl_zweite_selectbox = st.selectbox("Wähle ein Profil", optionen)
    st.write(f"Du hast {wahl_zweite_selectbox} ausgewählt.")




st.write("---")


expander = st.expander("zusätliche Informationen zu deiner Stütze:")
expander.write("Deine Stütze benötigt ... Kubimeter ... und wiegt somit ... kg")
