import streamlit as st 
import pandas as pd
import numpy as np
import math
import random
import matplotlib.pyplot as plt
import csv
import sys
import os

st.set_page_config(page_title="Stützen-Stütze", layout="centered", page_icon=("🚩"))
initial_sidebar_state="expanded"


# Einleitung

with st.container():
    st.title("Stützen-Stütze")
    st.subheader("Das TRAKO Tool zur Vordimensionierung von Stützenquerschnitten")
 


#     Rahmenbedingungen
    

with st.container():
    st.write("---")
    st.subheader("Gib die Randbedingungen deiner Stütze an:")
    wert_zu_EF = {
    "Eulerfall 1":2,
    "Eulerfall 2":1,
    "Eulerfall 3":0.7,
    "Eulerfall 4":0.5
    }
    spalten=st.columns(2)
    with spalten[0]:
        F = st.number_input("Gebe die auf die Stütze wirkende Kraft F in kN ein:")
        hoehe = st.number_input("Gib die Höhe der zu berechnenden Stütze in Meter ein:")
        stuetzenabstand = st.number_input("Gib den Abstand der Stützen ein:")
    with spalten[1]:
        EF = st.selectbox("Wähle den Eulerfall der Stütze aus", list(wert_zu_EF.keys()))
        b= st.number_input("Gebe eine feste Breite deiner Stütze in cm ein:")
        w= st.number_input("Gebe die Windlast in kN/m² an:")
    expander = st.expander("Sieh dir die Eulerfälle und Windzonenkarte an")
    expander.write("Abbildung der vier Eulerfälle ")
    expander.write("Abbildung der Windzonenkarte und zugehöriger Windgeschwindigkeitstabelle")

# prüfen ob der User auch kein Scheiß eingegeben hat .. ! 
if F == 0 or hoehe == 0 or stuetzenabstand == 0 or w == 0 :
    st.write("Bitte trage zuerst die Randbedingungen deiner Stütze ein.")
    st.write("---")
    sys.exit()

st.write("---")

def get_value_from_csv (lambda_k, holzprofil):
    with open("C:\\Users\\lorda\\UNI\\BA\\VSC\\ba_trako\\knickbeiwerte.csv") as csv_datei: 
        df = pd.read_csv (csv_datei)
        row = df[df["lambda"] == lambda_k]
        value =row.at[row.index[0], holzprofil]
        return value 


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

wert= wert_zu_EF[EF]
sk= wert * hoehe

CM_PER_METER = 100

h_vor= sk / (0.289 * 100) * CM_PER_METER
def aufrunden_auf_naechsthoehe_durch_zwei(h_vor):
    cut = math.ceil(h_vor)
    return cut if cut % 2 == 0 else cut + 1

# Aufrunden auf nächsthöhere durch zwei teilbare Zahl
h = aufrunden_auf_naechsthoehe_durch_zwei(h_vor)

# Anzeige der Ergebnisse
st.write(f"Ursprüngliche Zahl: {h_vor}")
st.write(f"Gerundete Zahl (nächstgrößere durch zwei teilbare Zahl): {h}")

b = 12  

# Querschnittfläche A berechnen 
A = b * h 
Wy = (b * (h**2))/6 
min_i = 0.289 * h
w_fin = (w * 0.8)*stuetzenabstand
M= (w_fin*(hoehe**2))/8 
Md= M * 1.4
Nd= F * 1.4
lambda_k= sk*100/ min_i 
lambda_k=lambda_k if lambda_k % 5 == 0 else lambda_k + (5-lambda_k % 5)
k = get_value_from_csv(lambda_k, wahl_profil) 

ergebnis= (Nd/(A*k))/1.5 + ((Md*100)/Wy)/1.5


st.write(w_fin)
st.write(M)

st.write(Nd)
st.write(A)
st.write(k)
st.write(Md)
st.write(Wy)
st.write(ergebnis)


### BREITE Schätzen -----> wie????

# A = hoehe * breite 
# min_i = 0,289 * hoehe 
# Wy = (breite * hoehe²)/6 
# w1 = w * 0.8 
# w2 = w1 * stuetzenabstand 
# lamda = sk / min_i ---> auf nächtgrößere durch 5 teilbare Zahl aufrunden --> DATENBANK lamda --> Wert auswählen 
# Nd = F * 1.4#
# Md = 1.4 * ((w2*laenge²)/8) 





#    Materialauswahl








#     Ausgabe des Stützenquerschnitts


with st.container():
    st.subheader("Querschnitt deiner Stütze")
if button_gedrueckt:
    spalten=st.columns(2)
    with spalten[1]:
        if material_auswahl == "Holz":
            st.write("- Die über die Schlankheit vordimensionierte Höhe beträgt " + str(h) + " cm")
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



def zeichne_stuetze(EF, normalkraft=0):
    # Erstelle eine Linienzeichnung der Stütze
    fig, ax = plt.subplots()

    # Abhängig vom gewählten Eulerfall die Stütze zeichnen
    if EF == "Eulerfall 1":
        # Eulerfall 1: Obere Stütze ist fest eingespannt
        ax.plot([0, 0], [0, 1], 'k-', linewidth=2)  # Vertikale Linie
        ax.plot([-0.05, 0.05], [1, 1], 'k-', linewidth=2)  # Horizontale Linie oben (Festlager)
    elif EF == "Eulerfall 2":
        # Eulerfall 2: Untere Stütze ist fest eingespannt
        ax.plot([0, 0], [0, 1], 'k-', linewidth=2)  # Vertikale Linie
        ax.plot([-0.05, 0.05], [0, 0], 'k-', linewidth=2)  # Horizontale Linie unten (Festlager)
    elif EF == "Eulerfall 3":
        # Eulerfall 3: Beide Stützen sind gelenkig gelagert
        ax.plot([0, 0], [0, 1], 'k-', linewidth=2)  # Vertikale Linie
        ax.plot([-0.05, 0.05], [1, 1], 'k--', linewidth=2)  # Horizontale gestrichelte Linie oben (Loslager)
        ax.plot([-0.05, 0.05], [0, 0], 'k--', linewidth=2)  # Horizontale gestrichelte Linie unten (Loslager)
    elif EF == "Eulerfall 4":
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


# Benutzereingabe für die Normalkraft
normalkraft = F

# Zeichne die Stütze mit dem vergrößerten Pfeil und zeige sie in der Streamlit-App an
st.pyplot(zeichne_stuetze(EF, normalkraft), use_container_width=True)


