from random import randint
import time
import customtkinter as ctk
import tkinter as tk
from PIL import Image

def Init_jeu():
    Pseudo("Zuhuna", 1)
    Pseudo("HorlogeMurale", 2)
    Image(1)
    
def Pseudo(name, numero):
    if numero == 1:
        pseudo_joueur1_var.set(name)
        print("1")
    if numero == 2:
        pseudo_joueur2_var.set(name)
        print("2")

def Image(numero):
    pil_image = Image.open("img/R.jpg")
    


def Jouer():
    None


# def Jeu():
#     while Scorej1 < 2 and Scorej2 < 2 :
#         if (Joueur1 == 1 and Joueur2 == 1 or Joueur1 == 2 and Joueur2 == 2 or Joueur1 == 2 and Joueur2 == 2): #egaliter
#             time.sleep(2)
#         if (Joueur1 == 1 and Joueur2 == 3 or Joueur1 == 2 and Joueur2 == 1 or Joueur1 == 3 and Joueur2 == 2): #j1 gagne
#             Scorej1 += 1
#             label_score.set(""+str(Scorej1)+" : 0")
#             time.sleep(2)
#         if (Joueur2 == 1 and Joueur1 == 3 or Joueur2 == 2 and Joueur1 == 1 or Joueur2 == 3 and Joueur1 == 2): #j2 gagne
#             Scorej2 += 1
#             label_score.set("0 : "+str(Scorej2)+"")
#             time.sleep(2)
#     if Scorej2 == 2:
#         None
#     if Scorej1 == 2:
#         None
# 
# def Jouer(x):
#     t = 10
#     while t != 0:
#         choix = x
#         time.sleep(1)
#         t -= 1
#         label_timer.set(""+str(t)+" s")
#     joueur1 = choix

# ── Paramètres de la fenêtre ───────────────────────────────────────────────
app = ctk.CTk()
app.title("Pierre Feuille Ciseaux")
app.geometry("1000x800")
app.configure(fg_color="white")  # couleur de fond
 
# ── Titre principal ────────────────────────────────────────────────────────
titre = ctk.CTkLabel(
    app,
    text="Pierre Feuille Ciseaux",
    font=("Courier", 32, "bold"),
    text_color="black"
)
titre.place(x=500, y=80, anchor="center")  # centré, en haut
 
# ── Score ──────────────────────────────────────────────────────────────────
score = ctk.CTkLabel(
    app,
    text="0 : 0",
    font=("Courier", 28, "bold"),
    text_color="#e94560"  # rouge/rose
)
score.place(x=500, y=160, anchor="center")  # centré, sous le titre
 
# ── Pseudo joueur (à gauche) ───────────────────────────────────────────────
pseudo_joueur1_var = tk.StringVar(value="Texte initial")

pseudo_joueur1 = ctk.CTkLabel(
    app,
    textvariable=pseudo_joueur1_var,
    font=("Courier", 16),
    text_color="grey"
)
pseudo_joueur1.place(x=200, y=250, anchor="center")
 
# ── Emoji choix du joueur ──────────────────────────────────────────────────
image_joueur1 = ctk.CTkImage(
    app,
    size=(40, 40)
)
image_joueur1.place(x=200, y=360, anchor="center")
 
# ── VS au milieu ───────────────────────────────────────────────────────────
vs = ctk.CTkLabel(
    app,
    text="VS",
    font=("Courier", 36, "bold"),
    text_color="red"
)
vs.place(x=500, y=360, anchor="center")
 
# ── Emoji choix du CPU ─────────────────────────────────────────────────────
image_joueur2 = ctk.CTkLabel(
    app,
    text="❓",
    font=("Segoe UI Emoji", 80)
)
image_joueur2.place(x=800, y=360, anchor="center")
 
# ── Pseudo CPU (à droite) ──────────────────────────────────────────────────
pseudo_joueur2_var = tk.StringVar(value="Texte initial")

pseudo_joueur2 = ctk.CTkLabel(
    app,
    textvariable=pseudo_joueur2_var,
    font=("Courier", 16),
    text_color="grey"
)
pseudo_joueur2.place(x=800, y=250, anchor="center")
 
# ── Timer ──────────────────────────────────────────────────────────────────
timer = ctk.CTkLabel(
    app,
    text="10 s",
    font=("Courier", 20),
    text_color="#ffffff"
)
timer.place(x=500, y=500, anchor="center")
 
# ── Barre de progression du timer ─────────────────────────────────────────
barre = ctk.CTkProgressBar(app, width=600, height=10, progress_color="#e94560")
barre.set(1.0)  # 1.0 = pleine, 0.0 = vide
barre.place(x=500, y=530, anchor="center")
 
# ── Boutons pierre / feuille / ciseaux ────────────────────────────────────
btn_pierre = ctk.CTkButton(
    app,
    text="🪨\npierre",
    font=("Segoe UI Emoji", 24),
    width=120, height=100,
    fg_color="#0f3460",
    hover_color="#1a4a80",
    corner_radius=12,
    command=Jouer()
)
btn_pierre.place(x=310, y=660, anchor="center")
 
btn_feuille = ctk.CTkButton(
    app,
    text="📄\nfeuille",
    font=("Segoe UI Emoji", 24),
    width=120, height=100,
    fg_color="#0f3460",
    hover_color="#1a4a80",
    corner_radius=12,
    command=Jouer()
)
btn_feuille.place(x=500, y=660, anchor="center")
 
btn_ciseaux = ctk.CTkButton(
    app,
    text="✂️\nciseaux",
    font=("Segoe UI Emoji", 24),
    width=120, height=100,
    fg_color="#0f3460",
    hover_color="#1a4a80",
    corner_radius=12,
    command=Jouer()
)
btn_ciseaux.place(x=690, y=660, anchor="center")
 
# ── Message résultat ───────────────────────────────────────────────────────
resultat = ctk.CTkLabel(
    app,
    text="",  # vide au départ, on le remplira plus tard
    font=("Courier", 22, "bold"),
    text_color="#4ade80"
)
resultat.place(x=500, y=750, anchor="center")
 
# ── Lancement de la fenêtre ────────────────────────────────────────────────

Init_jeu()
app.mainloop()



