import streamlit as st 
import pandas as pd
import numpy as np
import math
import random
import matplotlib.pyplot as plt

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

def zeichne_stuetze():
    # Erstelle eine einfache Linienzeichnung der Stütze
    fig, ax = plt.subplots()
    
    # Linienzeichnung für die Stütze
    ax.plot([0, 0], [0, 1], 'k-', linewidth=2)  # Vertikale Linie
    ax.plot([-0.1, 0.1], [1, 1], 'k-', linewidth=2)  # Horizontale Linie oben
    ax.plot([-0.1, 0.1], [0, 0], 'k-', linewidth=2)  # Horizontale Linie unten

    # Anpassung der Achsen und Begrenzungen
    ax.axis('equal')
    ax.set_xlim([-0.2, 0.2])
    ax.set_ylim([0, 1.2])

    # Ausblenden der Achsenbeschriftungen
    ax.set_xticks([])
    ax.set_yticks([])

    return fig

# Streamlit-App
st.title("Stützenzeichnung")

# Zeichne die Stütze und zeige sie in der Streamlit-App an
st.pyplot(zeichne_stuetze())


expander = st.expander("zusätliche Informationen zu deiner Stütze:")
expander.write("Deine Stütze benötigt ... Kubimeter ... und wiegt somit ... kg")
