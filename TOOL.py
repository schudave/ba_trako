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
     st.stop()

st.write("---")

def get_k_from_csv(lambda_k, profil):
    try:
        with open("knickbeiwerte.csv") as csv_datei:
            df = pd.read_csv(csv_datei)
            row = df[df["lambda"] == lambda_k]
            value = row.at[row.index[0], profil]
            return value
    except:
        return -1

def get_A_from_csv(zeichen_profil, profil):
    try:
        with open("A_IPE_HEB.csv") as csv_datei:
            df = pd.read_csv(csv_datei)
            row = df[df["zeichen_profil"] == zeichen_profil]
            value = row.at[row.index[0], profil]
            return value
    except:
        return -1
    

def get_i_from_csv(zeichen_profil, profil):
    try:
        with open("i_IPE_HEB.csv") as csv_datei:
            df = pd.read_csv(csv_datei)
            row = df[df["zeichen_profil"] == zeichen_profil]
            value = row.at[row.index[0], profil]
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
    material_auswahl = st.selectbox("Wähle das Material :", (["Holz", "Stahl St 37"]))
    if material_auswahl == "Holz":
            optionen = ["KVH C24", "BSH GL24"]
    else:
            optionen = ["IPE", "HEB"]
    wahl_profil = st.selectbox("Wähle ein Profil :", optionen)

with spalten[1]:
    if material_auswahl == "Holz":
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
    elif material_auswahl == "Stahl St 37":
        if wahl_profil == "IPE":
            zeichen_profil= int(st.selectbox("IPE", (["360", "330", "300", "270", "240", "220", "200", "180", "160", "140", "120", "100", "80"])))
        elif wahl_profil == "HEB":
            zeichen_profil= int(st.selectbox("HEB", (["360", "300", "240", "220", "200", "180", "160", "140", "120", "100", "80"])))

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



if material_auswahl == "Holz":
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
    k = get_k_from_csv(lambda_k, wahl_profil)
    if k == -1:
        st.error("FEHLER! Für deine Stütze existieren keine validen Ergebnisse, bitte überprüfe deine EINGABEN!")
        st.stop()
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

else:
    w_fin = round((w * 0.8) * stuetzenabstand ,2)
    Nd = F * 1.4
    Nd_round = round(Nd,2)
    min_i_s = get_i_from_csv(zeichen_profil, wahl_profil)
    A_s = get_A_from_csv(zeichen_profil, wahl_profil )
    lambda_k = (sk*CM_PER_METER)/min_i_s 
    lambda_k = lambda_k if lambda_k % 5 == 0 else lambda_k + (5 - lambda_k % 5)
    # st.write(Nd)
    # st.write(A_s)
    # st.write(min_i_s)
    # st.write(sk)
    # st.write(lambda_k)
    if lambda_k > 250 and 80 <= int(zeichen_profil) <= 360:
        st.error("Für das gewählte Profil existieren keine Knickbeiwerte! Bitte ändere deine Eingaben.")
        st.stop()
    elif lambda_k < 20 and 80 <= int(zeichen_profil) <= 360:
        st.error("Für das gewählte Profil existieren keine Knickbeiwerte! Bitte ändere deine Eingaben.")
        st.stop()

    k = get_k_from_csv(lambda_k, wahl_profil)
    if k == -1:
        st.error("FEHLER! Für deine Stütze existieren keine validen Ergebnisse, bitte überprüfe deine Eingaben!")
        st.stop()
    sigma_d = Nd/(A_s*k)
    sigma_Rd = 21.8
    sigma_d_rounded=round(sigma_d,2)

    # st.write(sigma_d)
    # st.write(sigma_Rd)
    ausnutzungsgrad_vor_s = (sigma_d/sigma_Rd) * 100
    ausnutzungsgrad_s = round(ausnutzungsgrad_vor_s, 2)
    # st.write(ausnutzungsgrad_vor_s)
    # st.write(ausnutzungsgrad_s)
    lambda_print = int(lambda_k)


with spalten[3]:
    if material_auswahl == "Holz":
     if ausnutzungsgrad > 100 :
        st.write("Der gewählte Querschnitt erfüllt den Knicknachweis nicht, bitte ändere die Werte für b und h!")
     else:
        st.write(f"Der Ausnutzungsgrad ( η ) deiner Stütze beträgt :")
        st.success(f"{ausnutzungsgrad} %")
        st.write(f"Die Schlankheit der Stütze beträgt :")
        st.success(f"{lambda_print}")
    else:
        if sigma_d > sigma_Rd :
            st.write("Das gewählte Profil erfüllt den Knicknachweis nicht, bitte wähle ein größeres Profil.")
        else:
            st.write(f"Der Ausnutzungsgrad ( η ) deiner Stütze beträgt : ")
            st.success(f"{ausnutzungsgrad_s} %")
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

def zeichne_HEB(fig):
    fig, ax = plt.subplots()
    fig.set_size_inches(FIGURE_WIDTH,FIGURE_HEIGHT)

    ax.plot([0, 0], [0, 1], "k-", linewidth=15)  
    ax.plot([-0.5, 0.5], [0, 0], "k-", linewidth=15) 
    ax.plot([-0.5, 0.5], [1, 1], "k-", linewidth=15)
  

    ax.axis("equal")
    ax.set_xlim([-0.8, 0.8])
    ax.set_ylim([-0.3, 1.3])  

    ax.set_xticks([])
    ax.set_yticks([])

    return fig

def zeichne_IPE(fig):
        
    fig, ax = plt.subplots()
    fig.set_size_inches(FIGURE_WIDTH,FIGURE_HEIGHT)

    ax.plot([0, 0], [0, 1], "k-", linewidth=10)  
    ax.plot([-0.3, 0.3], [0, 0], "k-", linewidth=15) 
    ax.plot([-0.3, 0.3], [1, 1], "k-", linewidth=15)
  

    ax.axis("equal")
    ax.set_xlim([-0.8, 0.8])
    ax.set_ylim([-0.3, 1.3])  

    ax.set_xticks([])
    ax.set_yticks([])

    return fig

normalkraft = F


with spalten[2]:
    if material_auswahl == "Holz":
         draw_rectangle(b,h)
    elif material_auswahl == "Stahl St 37":
        if wahl_profil == "IPE":
            st.pyplot(zeichne_IPE(fig=0))
        else:
            st.pyplot(zeichne_HEB(fig=0))
       

with spalten[4]:
    st.pyplot(zeichne_stuetze(EF, normalkraft))


st.write("---")

with st.expander("Knicknachweis anzeigen :"):
    col1, col2, col3, col4 = st.columns(4)
    if material_auswahl == "Holz":
    
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
    else: 
        with col1:
            st.latex(rf"A = {A_s} \, cm^2")
            st.latex(rf"i = {min_i_s} \, cm")
            st.latex(rf"k = {k}")
            st.latex(rf"\text{{bei }} \lambda = {lambda_print}")
            st.latex(rf"N_d = F \times 1.4 = {Nd_round} \, \text{{kN}}")

        with col2:
            st.write("###")
            st.write("###")
            st.latex(rf"\sigma_d = {sigma_d_rounded} \, kN/cm^2")
            st.write("###")
            st.write("###")
            st.latex(rf"\sigma_Rd = {sigma_Rd} \, kN/cm²")

        with col3:
            st.write("###")
            st.write("###")
            st.write("###")
            st.latex(r"\sigma_d = \frac{N_d}{A \cdot k} < \sigma_{Rd}")
            
        with col4:
          if sigma_d < sigma_Rd:
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
            
            








##### ALTER CODE #####

# # Einleitung

# with st.container():
#     st.title("Stützen-Stütze")
#     st.subheader("Das TRAKO Tool zur Vordimensionierung von Stützenquerschnitten")


# #     Rahmenbedingungen


# with st.container():
#     st.write("---")
#     st.subheader("Gib die Randbedingungen deiner Stütze ein :")
#     wert_zu_EF = {
#         "Eulerfall 1": 2,
#         "Eulerfall 2": 1,
#         "Eulerfall 3": 0.7,
#         "Eulerfall 4": 0.5,
#     }
#     spalten = st.columns(2)
#     with spalten[0]:
#         F = st.number_input("Normalkraft F in kN :")
#         hoehe = st.number_input("Stützenhöhe in m :")
#         stuetzenabstand = st.number_input("Stützenabstand in m :")
#     with spalten[1]:
#         EF = st.selectbox("Wähle den Eulerfall: ", list(wert_zu_EF.keys()))
#         b = st.number_input("Gebe eine feste Breite deiner Stütze in cm ein :")
#         w = st.number_input("Windlast in kN/m² :")
#     expander = st.expander("Sieh dir die Eulerfälle und Windzonenkarte an")
#     expander.write("Abbildung der vier Eulerfälle ")
#     expander.write(
#         "Abbildung der Windzonenkarte und zugehöriger Windgeschwindigkeitstabelle"
#     )

# # prüfen ob der User auch kein Scheiß eingegeben hat .. !
# if F == 0 or hoehe == 0 or stuetzenabstand == 0 or w == 0:
#     st.write("Bitte trage zuerst die Randbedingungen deiner Stütze ein!")
#     st.write("---")
#     sys.exit()

# st.write("---")


# def get_value_from_csv(lambda_k, holzprofil):
#     with open(
#         "C:\\Users\\lorda\\UNI\\BA\\VSC\\ba_trako\\knickbeiwerte.csv"
#     ) as csv_datei:
#         df = pd.read_csv(csv_datei)
#         row = df[df["lambda"] == lambda_k]
#         value = row.at[row.index[0], holzprofil]
#         return value


# with st.container():
#     st.subheader("Konfiguriere deine Stütze :")
#     spalten = st.columns(2)
#     with spalten[0]:
#         material_auswahl = st.selectbox("Wähle das Material :", (["Holz", "Stahl"]))
#     with spalten[1]:
#         if material_auswahl == "Holz":
#             optionen = ["KVH C24", "BSH GL24"]
#         else:
#             optionen = ["HEB", "IPE", "Quadratrohr"]
#         wahl_profil = st.selectbox("Wähle ein Profil :", optionen)
#     st.write(f"Du hast {wahl_profil} ausgewählt.")
#     button_gedrueckt = st.button("Stützquerschnitt dimensionieren")

# st.write("---")


# # Rechenoperationen

# wert = wert_zu_EF[EF]
# sk = wert * hoehe

# CM_PER_METER = 100

# h_vor = sk / (0.289 * 100) * CM_PER_METER


# def aufrunden_auf_naechsthoehe_durch_zwei(h_vor):
#     cut = math.ceil(h_vor)
#     return cut if cut % 2 == 0 else cut + 1


# # Aufrunden auf nächsthöhere durch zwei teilbare Zahl
# h = aufrunden_auf_naechsthoehe_durch_zwei(h_vor)

# # Anzeige der Ergebnisse
# st.write(f"Ursprüngliche Zahl: {h_vor}")
# st.write(f"Gerundete Zahl (nächstgrößere durch zwei teilbare Zahl): {h}")

# b = h - 4


# def ergebnis_berechnen(b, h):
#     A = b * h
#     Wy = (b * (h**2)) / 6
#     min_i = 0.289 * h
#     w_fin = (w * 0.8) * stuetzenabstand
#     M = (w_fin * (hoehe**2)) / 8
#     Md = M * 1.4
#     Nd = F * 1.4
#     lambda_k = sk * 100 / min_i
#     lambda_k = lambda_k if lambda_k % 5 == 0 else lambda_k + (5 - lambda_k % 5)
#     st.write(lambda_k)
#     k = get_value_from_csv(lambda_k, wahl_profil)
#     ergebnis = (Nd / (A * k)) / 1.5 + ((Md * 100) / Wy) / 1.5
#     return b, h, ergebnis



# # Funktion zum Überprüfen, ob eine Zahl gerade ist
# def ist_gerade(zahl):
#     return zahl % 2 == 0


# def finde_optimale_werte(b, h):
#     aktuelles_b = b
#     aktuelles_h = h
#     i = 0
#     while True:
#         # Berechne das aktuelle Ergebnis
#         b_neu, h_neu, erg_neu = ergebnis_berechnen(
#             aufrunden_auf_naechsthoehe_durch_zwei(aktuelles_b),
#             aufrunden_auf_naechsthoehe_durch_zwei(aktuelles_h),
#         )
#         st.write(b_neu,h_neu, erg_neu)

#         if erg_neu > 1 and i == 0:
#             aktuelles_b += 2
#         elif  erg_neu > 1:
#             aktuelles_b += 2
#             aktuelles_h += 2
#         elif erg_neu <= 1:
#             b_next, h_next, erg_next = ergebnis_berechnen(
#                 aufrunden_auf_naechsthoehe_durch_zwei(b_neu- 2),
#                 aufrunden_auf_naechsthoehe_durch_zwei(h_neu - 2),
#             )

#             if erg_next > 1:
#                 return b_neu, h_neu, erg_neu
            
#             aktuelles_b-=2
#             aktuelles_h-=2
        




# # Beispielaufruf
# start_b = 1
# start_h = 1
# optimales_b, optimales_h, bestes_ergebnis = finde_optimale_werte(start_b, start_h)

# st.write(f"Optimales b: {optimales_b}")
# st.write(f"Optimales h: {optimales_h}")
# st.write(f"Bestes Ergebnis: {bestes_ergebnis}")


# # A = b * h
# # Wy = (b * (h**2)) / 6
# # min_i = 0.289 * h
# # w_fin = (w * 0.8) * stuetzenabstand
# # M = (w_fin * (hoehe**2)) / 8
# # Md = M * 1.4
# # Nd = F * 1.4
# # lambda_k = sk * 100 / min_i
# # lambda_k = lambda_k if lambda_k % 5 == 0 else lambda_k + (5 - lambda_k % 5)
# # k = get_value_from_csv(lambda_k, wahl_profil)

# # ergebnis = (Nd / (A * k)) / 1.5 + ((Md * 100) / Wy) / 1.5

# # st.write(sk, min_i)
# # st.write(lambda_k)
# # st.write(k)
# # st.write("---")
# # st.write(w_fin)
# # st.write(M)
# # st.write("---")
# # st.write(Nd)
# # st.write(A)
# # st.write(k)
# # st.write(Md)
# # st.write(Wy)
# # st.write(ergebnis)


# #     Ausgabe des Stützenquerschnitts


# with st.container():
#     st.subheader("Querschnitt deiner Stütze :")
# if button_gedrueckt:
#     spalten = st.columns(2)
#     with spalten[1]:
#         if material_auswahl == "Holz":
#             st.write(
#                 "- Die über die Schlankheit vordimensionierte Höhe beträgt "
#                 + str(h)
#                 + " cm"
#             )
#             st.write(
#                 "- Deine Stütze aus KVH/BSH hat eine Höhe von ... cm und eine Breite von ..."
#             )
#             st.write("- Der Ausnutzungsgrad deiner Stütze beträgt ... % ")
#         else:
#             st.write("- Deine Stütze aus Stahl wird ein HEB/IPE/Quadratrohr ... zb 140")
#             st.write("- Der Ausnutzungsgrad deiner Stütze beträgt ... % ")
#     with spalten[0]:
#         st.write(
#             "Der Querschnitt deiner Stütze sieht so aus: Abbildung des Stützenquerschnittes"
#         )

# expander = st.expander("zusätliche Informationen zu deiner Stütze:")
# expander.write("Deine Stütze benötigt ... Kubimeter ... und wiegt somit ... kg")
# st.write("---")

# expander = st.expander("vorherige Ergebnisse anzeigen")
# expander.write(
#     "Abbildung der vorherigen Ergebnisse für die Stützenquerschnitte in den gewählten Materialien und Profilen und den dazugehörigen Werten für b, h und den Ausnutzungsgrad"
# )


# with st.container():
#     spalten = st.columns(3)
#     spalten[1].button("Nachweise pdf drucken")


# def zeichne_stuetze(EF, normalkraft=0):
#     # Erstelle eine Linienzeichnung der Stütze
#     fig, ax = plt.subplots()

#     # Abhängig vom gewählten Eulerfall die Stütze zeichnen
#     if EF == "Eulerfall 1":
#         # Eulerfall 1: Obere Stütze ist fest eingespannt
#         ax.plot([0, 0], [0, 1], "k-", linewidth=2)  # Vertikale Linie
#         ax.plot(
#             [-0.05, 0.05], [1, 1], "k-", linewidth=2
#         )  # Horizontale Linie oben (Festlager)
#     elif EF == "Eulerfall 2":
#         # Eulerfall 2: Untere Stütze ist fest eingespannt
#         ax.plot([0, 0], [0, 1], "k-", linewidth=2)  # Vertikale Linie
#         ax.plot(
#             [-0.05, 0.05], [0, 0], "k-", linewidth=2
#         )  # Horizontale Linie unten (Festlager)
#     elif EF == "Eulerfall 3":
#         # Eulerfall 3: Beide Stützen sind gelenkig gelagert
#         ax.plot([0, 0], [0, 1], "k-", linewidth=2)  # Vertikale Linie
#         ax.plot(
#             [-0.05, 0.05], [1, 1], "k--", linewidth=2
#         )  # Horizontale gestrichelte Linie oben (Loslager)
#         ax.plot(
#             [-0.05, 0.05], [0, 0], "k--", linewidth=2
#         )  # Horizontale gestrichelte Linie unten (Loslager)
#     elif EF == "Eulerfall 4":
#         # Eulerfall 4: Obere Stütze ist gelenkig, untere Stütze ist fest eingespannt
#         ax.plot([0, 0], [0, 1], "k-", linewidth=2)  # Vertikale Linie
#         ax.plot(
#             [-0.05, 0.05], [1, 1], "k--", linewidth=2
#         )  # Horizontale gestrichelte Linie oben (Loslager)
#         ax.plot(
#             [-0.05, 0.05], [0, 0], "k-", linewidth=2
#         )  # Horizontale Linie unten (Festlager)

#     # Anpassung der Achsen und Begrenzungen
#     ax.axis("equal")
#     ax.set_xlim([-0.2, 0.2])
#     ax.set_ylim([-0.2, 1.7])  # Erweitert den Bereich für den Pfeil

#     # Ausblenden der Achsenbeschriftungen
#     ax.set_xticks([])
#     ax.set_yticks([])

#     # Zeichne den vergrößerten Pfeil für die Normalkraft
#     ax.annotate(
#         f"F: {normalkraft} kN",
#         xy=(0, 1),
#         xycoords="data",
#         xytext=(0, 1.3),
#         textcoords="data",
#         arrowprops=dict(
#             arrowstyle="->", connectionstyle="arc3", linewidth=2, shrinkA=0, shrinkB=10
#         ),
#         fontsize=12,
#         ha="center",
#         va="center",
#     )

#     # Rückgabe der Figur, um sie in Streamlit anzuzeigen
#     return fig


# # Streamlit-App
# st.title("Stützenzeichnung mit Eulerfall")


# # Benutzereingabe für die Normalkraft
# normalkraft = F

# # Zeichne die Stütze mit dem vergrößerten Pfeil und zeige sie in der Streamlit-App an
# st.pyplot(zeichne_stuetze(EF, normalkraft))
