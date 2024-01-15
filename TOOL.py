import streamlit as st 
import pandas as pd
import numpy as np
import math
import random
import matplotlib.pyplot as plt

st.set_page_config(page_title="Stützen-Stütze", layout="centered", page_icon=("🚩"))
initial_sidebar_state="expanded"


# Einleitung

with st.container():
    st.title("Stützen-Stütze")
    st.subheader("Das TRAKO Tool zur Vordimensionierung von Stützenquerschnitten")
 



#     Hardfacts
    

with st.container():
    st.write("---")
    st.subheader("Gib die Randbedingungen deiner Stütze an:")
    wert_zu_EF = {
    "1":2,
    "2":1,
    "3":0.7,
    "4":0.5
    }
    spalten=st.columns(2)
    with spalten[0]:
        F = st.number_input("Gebe die auf die Stütze wirkende Kraft F in kN ein:")
        laenge = st.number_input("Gib die Höhe der zu berechnenden Stütze in Meter ein:")
        stuetzenabstand = st.number_input("Gib den Abstand der Stützen ein:")
    with spalten[1]:
        EF = st.selectbox("Wähle den Eulerfall der Stütze aus", list(wert_zu_EF.keys()))
        b= st.number_input("Gebe eine feste Breite deiner Stütze in cm ein:")
        w= st.number_input("Gebe die Windlast in kN/m² an:")
    expander = st.expander("Sieh dir die Eulerfälle und Windzonenkarte an")
    expander.write("Abbildung der vier Eulerfälle ")
    expander.write("Abbildung der Windzonenkarte und zugehöriger Windgeschwindigkeitstabelle")



st.write("---")

#    Materialauswahl


with st.container():
    st.subheader("Konfiguriere deine Stütze")
    spalten=st.columns(2)
    with spalten[0]:
        material_auswahl = st.selectbox("Wähle das Material deiner Stütze:", (["Holz", "Stahl"]))
    with spalten[1]:
        if material_auswahl == "Holz":
            optionen = ["KVH C24","BSH GL24"]
        else:
            optionen = ["HEB", "IPE", "Quadratrohr"]
        wahl_profil = st.selectbox("Wähle ein Profil", optionen)
    st.write(f"Du hast {wahl_profil} ausgewählt.")
    button_gedrueckt= st.button("Stützquerschnitt dimensionieren")


st.write("---")

# Rechenoperationen

with st.container():
    wert= wert_zu_EF[EF]
    sk= wert * laenge
    h_vor= round( sk / (0.289 * 100),2)


#     Ausgabe des Stützenquerschnitts


with st.container():
    st.subheader("Querschnitt deiner Stütze")
if button_gedrueckt:
    spalten=st.columns(2)
    with spalten[1]:
        if material_auswahl == "Holz":
            st.write("- Die über die Schlankheit vordimensionierte Höhe beträgt " + str(h_vor) + " m")
            st.write("- Deine Stütze aus KVH/BSH hat eine Höhe von ... cm und eine Breite von ...")
            st.write("- Der Ausnutzungsgrad deiner Stütze beträgt ... % ")
        else:   
            st.write("- Deine Stütze aus Stahl wird ein HEB/IPE/Quadratrohr ... zb 140") 
            st.write("- Der Ausnutzungsgrad deiner Stütze beträgt ... % ")
    with spalten[0]:
        st.write("Der Querschnitt deiner Stütze sieht so aus: Abbildung des Stützenquerschnittes")

expander = st.expander("zusätliche Informationen zu deiner Stütze:")
expander.write("Deine Stütze benötigt ... Kubimeter ... und wiegt somit ... kg")
st.write("---")
             
expander = st.expander("vorherige Ergebnisse anzeigen")
expander.write("Abbildung der vorherigen Ergebnisse für die Stützenquerschnitte in den gewählten Materialien und Profilen und den dazugehörigen Werten für b, h und den Ausnutzungsgrad")






with st.container():
    spalten = st.columns(3)
    spalten[1].button("Nachweise pdf drucken")



def zeichne_stuetze(eulerfall, normalkraft=0):
    # Erstelle eine Linienzeichnung der Stütze
    fig, ax = plt.subplots()

    # Abhängig vom gewählten Eulerfall die Stütze zeichnen
    if eulerfall == "Eulerfall 1":
        # Eulerfall 1: Obere Stütze ist fest eingespannt
        ax.plot([0, 0], [0, 1], 'k-', linewidth=2)  # Vertikale Linie
        ax.plot([-0.05, 0.05], [1, 1], 'k-', linewidth=2)  # Horizontale Linie oben (Festlager)
    elif eulerfall == "Eulerfall 2":
        # Eulerfall 2: Untere Stütze ist fest eingespannt
        ax.plot([0, 0], [0, 1], 'k-', linewidth=2)  # Vertikale Linie
        ax.plot([-0.05, 0.05], [0, 0], 'k-', linewidth=2)  # Horizontale Linie unten (Festlager)
    elif eulerfall == "Eulerfall 3":
        # Eulerfall 3: Beide Stützen sind gelenkig gelagert
        ax.plot([0, 0], [0, 1], 'k-', linewidth=2)  # Vertikale Linie
        ax.plot([-0.05, 0.05], [1, 1], 'k--', linewidth=2)  # Horizontale gestrichelte Linie oben (Loslager)
        ax.plot([-0.05, 0.05], [0, 0], 'k--', linewidth=2)  # Horizontale gestrichelte Linie unten (Loslager)
    elif eulerfall == "Eulerfall 4":
        # Eulerfall 4: Obere Stütze ist gelenkig, untere Stütze ist fest eingespannt
        ax.plot([0, 0], [0, 1], 'k-', linewidth=2)  # Vertikale Linie
        ax.plot([-0.05, 0.05], [1, 1], 'k--', linewidth=2)  # Horizontale gestrichelte Linie oben (Loslager)
        ax.plot([-0.05, 0.05], [0, 0], 'k-', linewidth=2)  # Horizontale Linie unten (Festlager)

    # Anpassung der Achsen und Begrenzungen
    ax.axis('equal')
    ax.set_xlim([-0.2, 0.2])
    ax.set_ylim([-0.2, 1.7])  # Erweitert den Bereich für den Pfeil


    # Ausblenden der Achsenbeschriftungen
    ax.set_xticks([])
    ax.set_yticks([])

    # Zeichne den vergrößerten Pfeil für die Normalkraft
    ax.annotate(
        f'F: {normalkraft} kN',
        xy=(0, 1), xycoords='data',
        xytext=(0, 1.3), textcoords='data',
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3", linewidth=2, shrinkA=0, shrinkB=10),
        fontsize=12, ha="center", va="center"
    )

    # Rückgabe der Figur, um sie in Streamlit anzuzeigen
    return fig

# Streamlit-App
st.title("Stützenzeichnung mit Eulerfall")

# Benutzereingabe für den Eulerfall
eulerfall = st.selectbox("Wähle den Eulerfall der Stütze aus", ["Eulerfall 1", "Eulerfall 2", "Eulerfall 3", "Eulerfall 4"])

# Benutzereingabe für die Normalkraft
normalkraft = st.number_input("Trage die Normalkraft (kN) ein:", min_value=0, value=0)

# Zeichne die Stütze mit dem vergrößerten Pfeil und zeige sie in der Streamlit-App an
st.pyplot(zeichne_stuetze(eulerfall, normalkraft), use_container_width=True)
    
# BREITE SCHÄTZEN --> welche py Operation???        
    
# A = b * h     
# min_i = 0,289 * h 
# Wy (b*h^2)/6 
# wind = 0,65*0,8 = 0,52*stuetzenabstand = w
# lambda = sk/min_i --> auf nächsthöheren durch 5 teilbaren Wert runden --> Tabelle, Datenbank, --> Wert für k
# Nd
# Md
# wenn (Md/Wy)/sigma_m + (Nd/A*k)/sigma_cII <=1 dann passen b und h
# iterativ wiederholen, bis das Ergebnis so nah wie möglich an 1 ist


# "Der Querschnitt der Stütze ist b= , h= "        
                            
