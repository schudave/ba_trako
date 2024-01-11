import streamlit as st 
import pandas as pd
import numpy as np
import math
import random

st.set_page_config(page_title="Stützen-Stütze", layout="centered", page_icon=("🚩"))
initial_sidebar_state="expanded"

st.write(
    """
    <script>
        // Funktion, um zur oberen Position der Seite zu scrollen
        function scrollToTop() {
            window.scrollTo(0, 0);
        }

        // Warte, bis die Seite vollständig geladen ist, und rufe dann die Funktion auf
        window.onload = scrollToTop;
    </script>
    """,
    unsafe_allow_html=True
)






# Einleitung

with st.container():
    st.title("Stützen-Stütze")
    st.subheader("Das TRAKO Tool zur Vordimensionierung von Stützenquerschnitten")
    st.write("##")
    st.write("Dieses Tool ist von und für Architekturstudierende, die schnell und einfach plausible Stützenquerschnitte für ihre Entwürfe benötigen.")
    st.write("Dieses Tool dient nur der Berechnung von Stützen von einfachen Hallentragwerken. Hierbei stehen die Stützenreihen links und rechts der Halle und werden von einem Einfeldträger überspannt.")
 



#     Hardfacts
    

with st.container():
    st.write("---")
    st.subheader("Gib die Hardfacts deiner Stütze an:")
    wert_zu_EF = {
    "1":2,
    "2":1,
    "3":0.7,
    "4":0.5
    }
    spalten=st.columns(2)
    with spalten[0]:
        F = st.number_input("Gebe die auf die Stütze wirkende Normalkraft in kN ein:")
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
            optionen = ["KVH","BSH"]
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
            st.write("- Die über die Schlankheit vordimensionierte Höhe beträgt " + str(h_vor) + " cm")
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



# Hier der Auswahl von Eulerfällen ein Wert zuteilen um damit dann damit sk berechnet werden kann  


# Höhe über die Schlankheit vordimensinoieren und Zahl auf die nächshöhere durch zwei teilbare Zahl aufrunden --> h
    
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
                            
