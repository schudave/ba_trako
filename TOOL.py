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



#constants
FIGURE_WIDTH = 10
FIGURE_HEIGHT = 10
CM_PER_METER = 100
#open images
icon = Image.open("page_icon.png")
logo = Image.open("LOGO_Stütze.png")
Windzonenkarte=Image.open("Windzonenkarte.png")
Tabelle=Image.open("Geschwindigkeitsdruck_Tabelle.PNG")
#page congiguration
st.set_page_config(
    page_title="Stützen-Stütze",
    layout="wide",
    page_icon=(icon),
    menu_items={
        "github repository": "https://github.com/schudave/ba_trako",
    }
)
#header
spalte_titel, spalte_logo = st.columns([2, 0.5])
with spalte_titel:
    st.title("Stützen-Stütze")
    st.write("###")
    st.subheader("Das TRAKO Tool zur Vordimensionierung von Stützenquerschnitten")
with spalte_logo:
    st.image(logo, width=180)
#Rahmenbedingungen/framework conditions
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
#images of the "Windlast"
with st.expander("Windlast"):
    col1, col2 = st.columns(2)
    with col1:
        st.image(Windzonenkarte, width=400)
    with col2:
        st.image(Tabelle, width=400)
#checking user input
if F == 0 or hoehe == 0 or stuetzenabstand == 0:
     st.error("Bitte trage zuerst die Randbedingungen deiner Stütze ein!")
     st.write("---")
     st.stop()

st.write("---")
#functions the get values from csv files
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
def get_W_from_csv(zeichen_profil, profil):
    try:
        with open("W_IPE_HEB.csv") as csv_datei:
            df = pd.read_csv(csv_datei)
            row = df[df["zeichen_profil"] == zeichen_profil]
            value = row.at[row.index[0], profil]
            return value
    except:
        return -1
#getting the values corresponding to the Eulerfall
wert = wert_zu_EF[EF]
sk = wert * hoehe
#Überschlagsrechnung zur Vordimensionierung von h
h_vor = sk / (0.289 * 100) * CM_PER_METER
#rounding h_vor to have a number that is divisible by 2
def aufrunden_auf_naechsthoehe_durch_zwei(h_vor):
    cut = math.ceil(h_vor)
    return cut if cut % 2 == 0 else cut + 1
h = aufrunden_auf_naechsthoehe_durch_zwei(h_vor)
#new variable for F
normalkraft = F
#defining all the draw_ functions
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



    for i in np.arange(-0.5, -0.45, 0.0499):
        ax.plot([i, i], [0, 1], "k-", linewidth=1)

    num_lines = 15
    for idx, i in enumerate(np.linspace(0, 1, num_lines)):
        if idx == 0 or idx == num_lines - 1:
            ax.plot([-0.5, -0.45], [i, i], "k-", linewidth=1)
        else:
            ax.arrow(-0.5, i, 0.04, 0, head_width=0.01, head_length=0.01, fc='k', ec='k')
    ax.text(-0.5, -0.1, f"w: {w_fin} kN/m", ha='center', va='center', fontsize=20)
   
    ax.arrow(0.5, 0, 0, 0.98,  head_width=0.02, head_length=0.02, fc='k', ec='k',linewidth=2)
    ax.arrow(0.5, 1, 0, -0.98,  head_width=0.02, head_length=0.02, fc='k', ec='k',linewidth=2)
    ax.text(0.5, -0.1, f"l: {hoehe} m", ha='center', va='center', fontsize=20)

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
    return fig

def zeichne_HEB(fig):
    fig, ax = plt.subplots()
    fig.set_size_inches(FIGURE_WIDTH,FIGURE_HEIGHT)

    ax.plot([0, 0], [0, 1], "k-", linewidth=15)  
    ax.plot([-0.5, 0.5], [0, 0], "k-", linewidth=20) 
    ax.plot([-0.5, 0.5], [1, 1], "k-", linewidth=20)
  

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
    ax.plot([-0.3, 0.3], [0, 0], "k-", linewidth=20) 
    ax.plot([-0.3, 0.3], [1, 1], "k-", linewidth=20)
  

    ax.axis("equal")
    ax.set_xlim([-0.8, 0.8])
    ax.set_ylim([-0.3, 1.3])  

    ax.set_xticks([])
    ax.set_yticks([])

    return fig

def zeichne_moment(fig):
    fig, ax = plt.subplots()
    fig.set_size_inches(5,5)
    if EF == "Eulerfall 1":
        y=np.linspace(0,1,100)
        x= 0.8*((0.5-0.5*y)**2)
        ax.plot(-x,y, color = "blue")
        ax.plot([-0.2, 0],[0,0],color = "blue")
        ax.text(0, -0.1, f"M(0m): {- M_round} kNm", ha='center', va='center', fontsize=10)
    elif EF == "Eulerfall 2":
        y=np.linspace(0,1,100)
        x= 0.8*((0.5-y)**2)-0.2
        ax.plot(-x,y, color = "red")
        ax.text(0, -0.1, f"M max({hoehe/2}m): {M_round} kNm", ha='center', va='center', fontsize=10)
    elif EF == "Eulerfall 3":
        y=np.linspace(0,1,100)
        x= 0.8*((0.5-y+0.125)**2)-0.12
        mask= x <= 0
        ax.plot(-x[mask],y[mask], color = "red")  
        y=np.linspace(0,1,100)
        x= 0.8*((0.5-y+0.125)**2)-0.12
        mask= x >= 0
        ax.plot(-x[mask],y[mask], color = "blue")
        ax.plot([0,-0.19],[0,0], color = "blue")
        ax.arrow(0.25, 0.625, 0, 0.365,  head_width=0.01, head_length=0.01, fc='k', ec='k',linewidth=1)
        ax.arrow(0.25, 1, 0, -0.365,  head_width=0.01, head_length=0.01, fc='k', ec='k',linewidth=1)
        ax.text(0.45, 0.5, f"M(x): {M_round} kNm", ha='center', va='center', fontsize=10)
        ax.text(0.5, 0.8, f"x: l * 0,375", ha='center', va='center', fontsize=10)
        M_EF3=round(- w_fin*(hoehe**2)/8,2)
        ax.text(0, -0.1, f"M(0m): {M_EF3} kNm", ha='center', va='center', fontsize=10)

    elif EF == "Eulerfall 4":
        y=np.linspace(0,1,100)
        x= 0.8*((0.5-y)**2)-0.1
        mask= x <= 0
        ax.plot(-x[mask],y[mask], color = "red")
        y=np.linspace(0,1,100)
        x= 0.8*((0.5-y)**2)-0.1
        mask= x >= 0
        ax.plot(-x[mask],y[mask], color = "blue")
        ax.plot([0,-0.1],[0,0], color = "blue")
        ax.plot([0,-0.1],[1,1], color = "blue")
        ax.arrow(0.25, 0, 0, 0.49,  head_width=0.01, head_length=0.01, fc='k', ec='k',linewidth=1)
        ax.arrow(0.25, 0.5, 0, -0.49,  head_width=0.01, head_length=0.01, fc='k', ec='k',linewidth=1)
        ax.text(0.5, 0.25, f"x: l * 0,5", ha='center', va='center', fontsize=10)
        ax.text(0.45, 0.6, f"M(x): {M_round} kNm", ha='center', va='center', fontsize=10)
        M_EF4=round(- w_fin*(hoehe**2)/12,2)
        ax.text(0, -0.1, f"M(0m): {M_EF4} kNm", ha='center', va='center', fontsize=10)
        ax.text(0, 1.1, f"M({hoehe}m): {M_EF4} kNm", ha='center', va='center', fontsize=10)
    
    ax.plot([0,0],[0,1],"-k",linewidth=2)
    
    ax.axis("equal")
    ax.set_xlim([-0.2, 0.2])
    ax.set_ylim([-0.2, 1.2])  

    ax.set_xticks([])
    ax.set_yticks([])
    return fig

def zeichne_quer(fig):
    fig, ax = plt.subplots()
    fig.set_size_inches(5,5)
    if EF == "Eulerfall 1":
        ax.plot([0.2, 0],[0,0],color = "red")  
        ax.plot([0.2, 0],[0,1],color = "red")    
        ax.text(0, -0.1, f"Q(0m): {w_fin * hoehe} kN", ha='center', va='center', fontsize=10)    
    elif EF == "Eulerfall 2":
        ax.plot([0.15, 0],[0,0],color = "red")  
        ax.plot([0.15, 0],[0,0.5],color = "red") 
        ax.plot([-0.15, 0],[1,1],color = "blue")  
        ax.plot([-0.15, 0],[1,0.5],color = "blue") 
        ax.text(0, -0.1, f"Q(0m): {round((w_fin * hoehe)/2,2)} kN", ha='center', va='center', fontsize=10)
        ax.text(0, 1.1, f"Q({hoehe}m): -{round((w_fin * hoehe)/2,2)} kN", ha='center', va='center', fontsize=10)
    elif EF == "Eulerfall 3":
        ax.plot([0.3125, 0],[0,0],color = "red")  
        ax.plot([0.3125, 0],[0,0.625],color = "red") 
        ax.plot([-0.1875, 0],[1,1],color = "blue")  
        ax.plot([-0.1875, 0],[1,0.625],color = "blue") 
        ax.text(0, -0.1, f"Q(0m): {round(5/8*(w_fin * hoehe),2)} kN", ha='center', va='center', fontsize=10)
        ax.text(0, 1.1, f"Q({hoehe}m): -{round(3/8*(w_fin * hoehe),2)} kN", ha='center', va='center', fontsize=10)  
    elif EF == "Eulerfall 4":
        ax.plot([0.15, 0],[0,0],color = "red")  
        ax.plot([0.15, 0],[0,0.5],color = "red") 
        ax.plot([-0.15, 0],[1,1],color = "blue")  
        ax.plot([-0.15, 0],[1,0.5],color = "blue") 
        ax.text(0, -0.1, f"Q(0m): {round((w_fin * hoehe)/2,2)} kN", ha='center', va='center', fontsize=10)
        ax.text(0, 1.1, f"Q({hoehe}m): -{round((w_fin * hoehe)/2,2)} kN", ha='center', va='center', fontsize=10)

    ax.plot([0,0],[0,1],"-k",linewidth=2)
    ax.axis("equal")
    ax.set_xlim([-0.2, 0.2])
    ax.set_ylim([-0.2, 1.2])  

    ax.set_xticks([])
    ax.set_yticks([])
    return fig
def zeichne_normal(fig):
    fig, ax = plt.subplots()
    fig.set_size_inches(5,5)
    ax.plot([0,-0.2],[0,0],color = "blue") 
    ax.plot([0,-0.2],[1,1],color = "blue") 
    ax.plot([-0.2,-0.2],[0,1],color = "blue")        
    ax.plot([0,0],[0,1],"-k",linewidth=2)
    ax.text(0, -0.1, f"N(x): -{(round(F,2))} kN ", ha='center', va='center', fontsize=10)
    ax.axis("equal")
    ax.set_xlim([-0.2, 0.2])
    ax.set_ylim([-0.2, 1.2])  
    ax.set_xticks([])
    ax.set_yticks([])
    return fig


#configuring the pillar
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
            zeichen_profil= int(st.selectbox("HEB", (["360", "300", "240", "220", "200", "180", "160", "140", "120", "100"])))

#calculations wood
if material_auswahl == "Holz":
    A = b * h
    Wy = (b * (h**2)) / 6
    min_i = 0.289 * h
    w_fin = round((w * 0.8) * stuetzenabstand ,2)
    if EF == "Eulerfall 1":
        M = (w_fin * (hoehe**2))/2
    elif EF == "Eulerfall 2":
        M = (w_fin * (hoehe**2)) / 8
    elif EF == "Eulerfall 3":
        M = 9/128*(w_fin * (hoehe**2))
    elif EF == "Eulerfall 4":
        M = (w_fin * (hoehe**2)) / 24
    M_round=round(M, 2)
    Md = (M * 1.4)*CM_PER_METER
    Md_round=round(Md, 2)
    Md_round_kNm=round(Md_round/CM_PER_METER, 2)
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
#calculations steel
else:
    w_fin = round((w * 0.8) * stuetzenabstand ,2)
    if EF == "Eulerfall 1":
        M = (w_fin * (hoehe**2))/2
    elif EF == "Eulerfall 2":
        M = (w_fin * (hoehe**2)) / 8
    elif EF == "Eulerfall 3":
        M = 9/128*(w_fin * (hoehe**2))
    elif EF == "Eulerfall 4":
        M = (w_fin * (hoehe**2)) / 24
    M_round=round(M, 2)
    Md = (M * 1.4)*CM_PER_METER
    Md_round=round(Md, 2)
    Md_round_kNm=round(Md_round/CM_PER_METER, 2)
    Nd = F * 1.4
    Nd_round = round(Nd,2)
    min_i_s = get_i_from_csv(zeichen_profil, wahl_profil)
    A_s = get_A_from_csv(zeichen_profil, wahl_profil )
    lambda_k = (sk*CM_PER_METER)/min_i_s 
    lambda_k = lambda_k if lambda_k % 5 == 0 else lambda_k + (5 - lambda_k % 5)
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
    W = get_W_from_csv(zeichen_profil, wahl_profil)

    sigma_d = Nd/(A_s*k)+(Md/W) 
    sigma_Rd = 21.8
    sigma_d_rounded=round(sigma_d,2)

    # st.write(sigma_d)
    # st.write(sigma_Rd)
    ausnutzungsgrad_vor_s = (sigma_d/sigma_Rd) * 100
    ausnutzungsgrad_s = round(ausnutzungsgrad_vor_s, 2)
    # st.write(ausnutzungsgrad_vor_s)
    # st.write(ausnutzungsgrad_s)
    lambda_print = int(lambda_k)

with spalten[2]:
    if material_auswahl == "Holz":
         draw_rectangle(b,h)
    elif material_auswahl == "Stahl St 37":
        if wahl_profil == "IPE":
            st.pyplot(zeichne_IPE(fig=0))
        else:
            st.pyplot(zeichne_HEB(fig=0))
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
with spalten[4]:
    st.pyplot(zeichne_stuetze(EF, normalkraft))
st.write("---")
with st.expander("Schnittgrößen anzeigen:"):
    col1, col2, col3, col4, col5, col6, col7 = st.columns([1,2,1,2,1,2,1])
    with col2:
        st.write("Momentenverlauf")
        if w_fin != 0:
            st.pyplot(zeichne_moment(fig=0))
        else: st.write("Ohne eine Windlast entsteht kein Momentenverlauf.")
    with col4:
        st.write("Querkraftverlauf")
        if w_fin != 0:
            st.pyplot(zeichne_quer(fig=0))
        else: st.write("Ohne eine Windlast entsteht kein Querkraftverlauf.")
    with col6:
        st.write("Normalkraftverlauf")
        st.pyplot(zeichne_normal(fig=0))
st.write("---")
with st.expander("Knicknachweis anzeigen :"):
    col1, col2, col3, col4 = st.columns([2,2,1,4])
    if material_auswahl == "Holz":
    
        with col1:
            st.latex(rf"A = {A} \, cm^2")
            st.latex(rf"k = {k}")
            st.latex(rf"\text{{bei }} \lambda = {lambda_print}")
            st.latex(rf"\sigma_{{cII}} = {sigma_c} \, \text{{kN/cm}}^2")
            st.latex(rf"N_d = F \times 1.4 = {Nd_round} \, \text{{kN}}")
            

        with col2:
            st.latex(rf"w = ({w} \,kN/m^2 \times 0.8) \times {stuetzenabstand} \,m = {w_fin} \,kN/m")
            if EF == "Eulerfall 1":
                 st.latex(rf"M = ({w_fin} \, kN/m \times {hoehe}^2) / 2 = {M_round} \,kNm")    
            elif EF == "Eulerfall 2":
                st.latex(rf"M = ({w_fin} \, kN/m \times {hoehe}^2) / 8 = {M_round} \,kNm")
            elif EF == "Eulerfall 3":
                st.latex(rf"M =  9 / 128 \times ({w_fin} \, kN/m \times {hoehe}^2) = {M_round} \,kNm")
            elif EF == "Eulerfall 4":
                st.latex(rf"M = ({w_fin} \, kN/m \times {hoehe}^2) / 24 = {M_round} \,kNm")
            st.latex(rf"M_d = M \times 1.4 = {Md_round} \,kNcm")
            st.latex(rf"W_y = (b \times h^2) / 6 = {Wy_round} \, cm^3")
            st.latex(rf"\sigma_m = {sigma_m} \, kN/cm^2")

        with col4:
            st.write("###")
            equation_latex = r"\frac{\frac{Nd}{{A \cdot k}}}{{\sigma_{{CII}}}} \;+\; \frac{\frac{Md}{Wy}}{{\sigma_m}} \;\leq\; 1"
            st.latex(equation_latex)
            st.write("###")
            st.write("###")
            equation_latex_werte = r"\frac{\frac{" + str(Nd_round) + "\ kN" + "}{" + str(A)+"\ cm²" + r" \cdot " + str(k) + r"}}{" + str(sigma_c)+"\ kN/cm²" + r"} \;+\; \frac{\frac{" + str(Md_round)+"\ kNcm" + "}{" + str(Wy_round)+"\ cm³" + r"}}{" + str(sigma_m)+"\ kN/cm²" + r"}  \;=\; " + str(ergebnis_round)
            st.latex(equation_latex_werte)

        with col3:
            st.write("###")

        if ergebnis > 1 :
            st.error("Die Stütze erfüllt den Knicknachweis nicht!")
        elif ergebnis <= 1:
            st.success("Die Stütze erfüllt den Knicknachweis")


    else: 
        with col1:
            st.latex(rf"A = {A_s} \, cm^2")
            st.latex(rf"i = {min_i_s} \, cm")
            st.latex(rf"k = {k}")
            st.latex(rf"\text{{bei }} \lambda = {lambda_print}")
            

        with col2:
            st.latex(rf"W = {W} \, cm^2")
            st.latex(rf"N_d = F \times 1.4 = {Nd_round} \, \text{{kN}}")
            st.latex(rf"M_d = F \times 1.4 = {Md_round} \, \text{{kN}}")
            

        with col4:
            st.latex(rf"\sigma_{{Rd}} = {sigma_Rd} \, kN/cm²")
            st.write("###")
            st.latex(r"\sigma_d = \frac{N_d}{A \cdot k} + \frac{M_d}{W} < \sigma_{Rd}")
            st.write("###")
            st.latex(fr"\sigma_d = \frac{{{Nd}\, \text{{kN}}}}{{{A_s}\text{{\ cm²}} \cdot {k}}} + \frac{{{Md_round}\, \text{{kNcm}}}}{{{W}\text{{\ cm²}}}}= {sigma_d_rounded} \, \text{{\ kN/cm²}}")
            
        with col3:
            st.write("###")

        if sigma_d > sigma_Rd:
            st.error("Die Stütze erfüllt den Knicknachweis nicht!")
        elif sigma_d < sigma_Rd:
            st.success("Die Stütze erfüllt den Knicknachweis!")



