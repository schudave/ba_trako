import streamlit as st
import pandas as pd
import numpy as np
import math
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import csv
import sys
import os
from PIL import Image



# KONSTANTEN
FIGURE_WIDTH = 10
FIGURE_HEIGHT = 10


icon = Image.open("page_icon.png")
logo = Image.open("LOGO_Stütze.png")
Windzonenkarte=Image.open("Windzonenkarte.png")
Tabelle=Image.open("Geschwindigkeitsdruck_Tabelle.PNG")

st.set_page_config(
    page_title="Stützen-Stütze",
    layout="wide",
    page_icon=(icon),
)

spalte_titel, spalte_logo = st.columns([2, 0.5])
with spalte_titel:
    st.title("Stützen-Stütze")
    st.write("###")
    st.subheader("Das TRAKO Tool zur Vordimensionierung von Stützenquerschnitten")
with spalte_logo:
    st.image(logo, width=180)


#     Rahmenbedingungen


with st.container():
    st.write("---")
    st.subheader("Gib die Randbedingungen deiner Stütze ein :")
    wert_zu_EF = {
        "Eulerfall 1": 2,
        "Eulerfall 2": 1,
        "Eulerfall 3": 0.7,
        "Eulerfall 4": 0.5,
    }
    spalten = st.columns(5)
    with spalten[0]:
        F = st.number_input("Normalkraft F in kN :",min_value=0.00)
    with spalten[1]:
        hoehe = st.number_input("Stützenhöhe in m :",min_value=0.00)
    with spalten[2]:
        stuetzenabstand = st.number_input("Stützenabstand in m :",min_value=0.00)
    with spalten[3]:
        w = st.number_input("Windlast in kN/m² :",min_value=0.00)
    with spalten[4]:
        EF = st.selectbox("Wähle den Eulerfall: ", list(wert_zu_EF.keys()))


with st.expander("Windlast"):
    col1, col2 = st.columns(2)
    with col1:
        st.image(Windzonenkarte, width=400)
    with col2:
        st.image(Tabelle, width=600)


# prüfen ob der User auch kein korrekte Werte eingegeben hat
if F == 0 or hoehe == 0 or stuetzenabstand == 0 or w == 0:
     st.error("Bitte trage zuerst die Randbedingungen deiner Stütze ein!")
     st.write("---")

st.write("---")

def get_value_from_csv(lambda_k, holzprofil):
    try:
        with open("knickbeiwerte.csv") as csv_datei:
            df = pd.read_csv(csv_datei)
            row = df[df["lambda"] == lambda_k]
            value = row.at[row.index[0], holzprofil]
            return value
    except:
        return -1


wert = wert_zu_EF[EF]
sk = wert * hoehe
CM_PER_METER = 100
h_vor = sk / (0.289 * 100) * CM_PER_METER

def aufrunden_auf_naechsthoehe_durch_zwei(h_vor):
    cut = math.ceil(h_vor)
    return cut if cut % 2 == 0 else cut + 1
h = aufrunden_auf_naechsthoehe_durch_zwei(h_vor)

st.subheader("Konfiguriere deine Stütze :")
spalten = st.columns(5)
with spalten[0]:
    material_auswahl = st.selectbox("Wähle das Material :", (["Holz", "Stahl"]))
    if material_auswahl == "Holz":
            optionen = ["KVH C24", "BSH GL24"]
    else:
            optionen = ["HEB", "IPE", "Quadratrohr"]
    wahl_profil = st.selectbox("Wähle ein Profil :", optionen)

with spalten[1]:
    default_value=h
    h = st.select_slider(
    'Gib h an :',
    options=list(range(2, 101, 2)),  
    value=default_value 
    )
    b = st.select_slider(
    'Gib b an :',
    options=list(range(2, 101, 2)),  
    value=default_value 
    )

def draw_rectangle(width, height, linewidth = 5.0):
    # Erstelle die Darstellungsoberfläche mit Streamlit
    fig, ax = plt.subplots()
    fig.set_size_inches(FIGURE_WIDTH,FIGURE_HEIGHT)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    def get_center(length):
        return 0.5 - length / 2

    rectangle = Rectangle((1,1), 0, 0, edgecolor='black', facecolor='none', linewidth = linewidth)
    # Berechne die Position des Rechtecks, um es in der Mitte zu platzieren
    if height <= width:
        width_fix=0.4
        seitenverhaeltnis= height/width
        x_center = get_center(width_fix)
        y_center = get_center(seitenverhaeltnis*width_fix)

        rectangle.set_xy((x_center,y_center))
        rectangle.set_width(width_fix)
        rectangle.set_height(seitenverhaeltnis * width_fix)
    else:
        height_fix = 0.4
        seitenverhaeltnis = width/height
        x_center = get_center(seitenverhaeltnis*height_fix)
        y_center = get_center(height_fix)

        rectangle.set_width(seitenverhaeltnis*height_fix)
        rectangle.set_height(height_fix)
        rectangle.set_xy((x_center,y_center))
    
    ax.set_xticks([])
    ax.set_yticks([])
    
    ax.add_patch(rectangle)
    
    ax.text(0.5, 0.1, f"b = {width} cm", ha='center', va='center', fontsize=20)
    ax.text(0.15, 0.5, f"h = {height} cm", ha='center', va='center', fontsize=20)

    st.pyplot(fig)


A = b * h
Wy = (b * (h**2)) / 6
min_i = 0.289 * h
w_fin = round((w * 0.8) * stuetzenabstand ,2)
M = (w_fin * (hoehe**2)) / 8
M_round=round(M, 2)
Md = (M * 1.4)*CM_PER_METER
Md_round=round(Md, 2)
Nd = F * 1.4
Nd_round = round(Nd,2)
lambda_k = sk * 100 / min_i
lambda_k = lambda_k if lambda_k % 5 == 0 else lambda_k + (5 - lambda_k % 5)
k = get_value_from_csv(lambda_k, wahl_profil)
if k == -1:
    st.error("FEHLER! Für deine Stütze existieren keine validen Ergebnisse, bitte überprüfe deine EINGABEN!")
if wahl_profil == "KVH C24" :
    sigma_c = 1.3
else:
    sigma_c = 1.5
sigma_m = 1.5 
ergebnis = (Nd / (A * k)) / sigma_c + (Md / Wy) / sigma_m
ergebnis_round=round(ergebnis, 3)
Wy_round= round(Wy, 2)
ausnutzungsgrad_vor= ergebnis * 100
ausnutzungsgrad = round (ausnutzungsgrad_vor, 2)
lambda_print = int(lambda_k)


with spalten[3]:
     if ausnutzungsgrad > 100 :
        st.write("Der gewählte Querschnitt erfüllt den Knicknachweis nicht, bitte ändere die Werte für b und h!")
     else:
        st.write(f"Der Ausnutzungsgrad ( η ) deiner Stütze beträgt :")
        st.success(f"{ausnutzungsgrad} %")
        st.write(f"Die Schlankheit der Stütze beträgt :")
        st.success(f"{lambda_print}")

def zeichne_stuetze(EF, normalkraft=0):
    
    fig, ax = plt.subplots()
    fig.set_size_inches(FIGURE_WIDTH,FIGURE_HEIGHT)

    if EF == "Eulerfall 1":
        ax.plot([0, 0], [0, 1], "k-", linewidth=4)  
        ax.plot([-0.1, 0.1], [0, 0], "k-", linewidth=4) 
        ax.plot([-0.1, -0.05],[0,-0.05], "k-", linewidth=2,)
        ax.plot([-0.05, 0],[0,-0.05], "k-", linewidth=2,)
        ax.plot([0, 0.05],[0,-0.05], "k-", linewidth=2,)
        ax.plot([0.05, 0.1],[0,-0.05], "k-", linewidth=2,)
        ax.plot([0.1, 0.15],[0,-0.05], "k-", linewidth=2,)

    elif EF == "Eulerfall 2":
        ax.plot([0, 0], [0, 1], "k-", linewidth=4) 
        
        ax.add_patch(plt.Circle((0, 0), 0.015, color='black'))
        x_triangle = [-0.05, 0, 0.05, -0.05]  
        y_triangle = [-0.05, 0, -0.05, -0.05]
        ax.plot(x_triangle, y_triangle, "k-", linewidth=2)
    
        ax.add_patch(plt.Circle((0, 1), 0.015, color='black'))
        x_triangle = [0, 0.05, 0.05, 0]  
        y_triangle = [1, 1.05, 0.95, 1]
        ax.plot(x_triangle, y_triangle, "k-", linewidth=2)
        ax.plot([0.07,0.07],[0.95,1.05],"k-", linewidth=2)

        ax.plot([-0.05,-0.025],[-0.05,-0.075],"k-", linewidth=2)
        ax.plot([-0.025,0],[-0.05,-0.075],"k-", linewidth=2)
        ax.plot([0,0.025],[-0.05,-0.075],"k-", linewidth=2)
        ax.plot([0.025,0.05],[-0.05,-0.075],"k-", linewidth=2)
        ax.plot([0.05,0.075],[-0.05,-0.075],"k-", linewidth=2)

    elif EF == "Eulerfall 3":
        ax.plot([0, 0], [0, 1], "k-", linewidth=4) 
        ax.plot([0.07,0.07],[0.95,1.05],"k-", linewidth=2)
        ax.plot([-0.1, 0.1], [0, 0], "k-", linewidth=4) 
        ax.plot([-0.1, -0.05],[0,-0.05], "k-", linewidth=2,)
        ax.plot([-0.05, 0],[0,-0.05], "k-", linewidth=2,)
        ax.plot([0, 0.05],[0,-0.05], "k-", linewidth=2,)
        ax.plot([0.05, 0.1],[0,-0.05], "k-", linewidth=2,)
        ax.plot([0.1, 0.15],[0,-0.05], "k-", linewidth=2,)
        ax.add_patch(plt.Circle((0, 1), 0.015, color='black'))
        x_triangle = [0, 0.05, 0.05, 0]  
        y_triangle = [1, 1.05, 0.95, 1]
        ax.plot(x_triangle, y_triangle, "k-", linewidth=2)

    elif EF == "Eulerfall 4":
        ax.plot([0, 0], [0, 1], "k-", linewidth=4)  
        ax.plot([-0.1, 0.1], [0, 0], "k-", linewidth=4) 
        ax.plot([-0.1, -0.05],[0,-0.05], "k-", linewidth=2,)
        ax.plot([-0.05, 0],[0,-0.05], "k-", linewidth=2,)
        ax.plot([0, 0.05],[0,-0.05], "k-", linewidth=2,)
        ax.plot([0.05, 0.1],[0,-0.05], "k-", linewidth=2,)
        ax.plot([0.1, 0.15],[0,-0.05], "k-", linewidth=2,)

        ax.plot([-0.1, 0.1], [1, 1], "k-", linewidth=4) 
        ax.plot([-0.1, -0.15],[1,1.05], "k-", linewidth=2,)
        ax.plot([-0.05, -0.1],[1,1.05], "k-", linewidth=2,)
        ax.plot([0, -0.05],[1,1.05], "k-", linewidth=2,)
        ax.plot([0.05, 0],[1,1.05], "k-", linewidth=2,)
        ax.plot([0.1, 0.05],[1,1.05], "k-", linewidth=2,)



    for i in np.arange(-0.65, -0.6, 0.0499):
        ax.plot([i, i], [0, 1], "k-", linewidth=1)

    num_lines = 15
    for idx, i in enumerate(np.linspace(0, 1, num_lines)):
        if idx == 0 or idx == num_lines - 1:
            ax.plot([-0.65, -0.6], [i, i], "k-", linewidth=1)
        else:
            ax.arrow(-0.65, i, 0.04, 0, head_width=0.01, head_length=0.01, fc='k', ec='k')
    ax.text(-0.65, -0.1, f"w: {w_fin} kN/m", ha='center', va='center', fontsize=20)
   
    ax.arrow(-0.25, 0, 0, 0.98,  head_width=0.02, head_length=0.02, fc='k', ec='k',linewidth=2)
    ax.arrow(-0.25, 1, 0, -0.98,  head_width=0.02, head_length=0.02, fc='k', ec='k',linewidth=2)
    ax.text(-0.41, 0.5, f"l: {hoehe} m", ha='center', va='center', fontsize=20)

    ax.axis("equal")
    ax.set_xlim([-0.2, 0.2])
    ax.set_ylim([-0.2, 1.7])  

    ax.set_xticks([])
    ax.set_yticks([])

    ax.annotate(
        f"F: {normalkraft} kN",
        xy=(0, 1.1),
        xycoords="data",
        xytext=(0, 1.5),
        textcoords="data",
        arrowprops=dict(
            arrowstyle="->", connectionstyle="arc3", linewidth=2, shrinkA=0, shrinkB=10
        ),
        fontsize=20,
        ha="center",
        va="center",
    )
    ### PARABEL für Moment max
    y=np.linspace(0,1,100)
    x= ((0.5-y)**2) - 0.6
    plt.plot(-x,y)
    ax.plot([0.35,0.35],[0,1],"-k",linewidth=2)
    M_max = (w_fin*(hoehe**2))/8
    M_max_fin=round(M_max,2)
    ax.text(0.55, -0.1, f"M max: {M_max_fin} kNm", ha='center', va='center', fontsize=20)
    ax.arrow(0.35, 0.5, 0.23, 0,  head_width=0.02, head_length=0.02, fc='k', ec='k',linewidth=1)
    ax.arrow(0.6, 0.5, -0.23, 0,  head_width=0.02, head_length=0.02, fc='k', ec='k',linewidth=1)

    return fig

normalkraft = F

with spalten[2]:
   draw_rectangle(b,h)

with spalten[4]:
    st.pyplot(zeichne_stuetze(EF, normalkraft))

st.write("---")

with st.expander("Knicknachweis anzeigen :"):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.latex(rf"A = {A} \, cm^2")
        st.latex(rf"k = {k}")
        st.latex(rf"\text{{bei }} \lambda = {lambda_print}")
        st.latex(rf"\sigma_{{cII}} = {sigma_c} \, \text{{kN/cm}}^2")
        st.latex(rf"N_d = F \times 1.4 = {Nd_round} \, \text{{kN}}")
        

    with col2:
        st.latex(rf"w = ({w} \,kN/m^2 \times 0.8) \times {stuetzenabstand} \,m = {w_fin} \,kN/m")
        st.latex(rf"M = ({w_fin} \, kN/m \times {hoehe}^2) / 8 = {M_round} \,kNm")
        st.latex(rf"M_d = M \times 1.4 = {Md_round} \,kNcm")
        st.latex(rf"W_y = (b \times h^2) / 6 = {Wy_round} \, cm^3")
        st.latex(rf"\sigma_m = {sigma_m} \, kN/cm^2")

    with col3:
        st.write("###")
        equation_latex = r"\frac{\frac{Nd}{{A \cdot k}}}{{\sigma_c}} \;+\; \frac{\frac{Md}{Wy}}{{\sigma_m}} \;\leq\; 1"
        st.latex(equation_latex)
        st.write("###")
        st.write("###")
        equation_latex_werte = r"\frac{\frac{" + str(Nd_round) + " kN" + "}{" + str(A)+"cm²" + r" \cdot " + str(k) + r"}}{" + str(sigma_c)+"kN/cm²" + r"} \;+\; \frac{\frac{" + str(Md_round)+"kNcm" + "}{" + str(Wy_round)+"cm³" + r"}}{" + str(sigma_m)+"kN/cm²" + r"}  \;=\; " + str(ergebnis_round)
        st.latex(equation_latex_werte)

    with col4:
        if ergebnis <= 1:
            st.write("###")
            st.write("###")
            st.write("###")
            st.write("###")
            st.write("Das gewählte Stützenprofil erfüllt den Knicknachweis.")
        else:
            st.write("###")
            st.write("###")
            st.write("###")
            st.write("###")
            st.write("Das Stützenprofil erfüllt den Knicknachweis NICHT!")