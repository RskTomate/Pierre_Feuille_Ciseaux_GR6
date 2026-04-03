#from random import randint
import customtkinter as ctk
import tkinter as tk
from PIL import Image , ImageTk
from random import randint
import time
import subprocess
import sys

# ── Initialisation du jeu ────────────────────────────────── 

def Init_jeu():
    Pseudo("Zuhuna", 1)
    Pseudo("HorlogeMurale", 2)
    Photo_de_profil("images/Sukuna.png", 1)
    Photo_de_profil("images/Gojo.png", 2)

# ── Affiche un pseudo de notre choix ────────────────────────────────── 

def Pseudo(name, numero):
    if numero == 1:
        canvas.itemconfig(j1, text=name)
        texte_contour(canvas, 200, 250, name, ("Lemon Milk", 40, "bold"), "red", tag="j1")
    if numero == 2:
        canvas.itemconfig(j2, text=name)
        texte_contour(canvas, 800, 250, name, ("Lemon Milk", 40, "bold"), "blue", tag="j1")

# ── Affiche une photo de notre choix ────────────────────────────────── 

def Photo_de_profil(lien, numero):
    Pdp = Image.open(lien)
    Pdp_image = ctk.CTkImage(light_image=Pdp, size=(150, 150))
    
    if numero == 1:
        label = ctk.CTkLabel(app, image=Pdp_image, text="")
        label.place(x=200, y=360, anchor="center")
        label.ctk_image = Pdp_image
    
    if numero == 2:
        label = ctk.CTkLabel(app, image=Pdp_image, text="")
        label.place(x=800, y=360, anchor="center")
        label.ctk_image = Pdp_image

# ── Faire un contour jolie au texte ──────────────────────────────────  

def texte_contour(canvas, x, y, texte, font, fill, contour="black", epaisseur=2, tag=None):
    for dx in range(-epaisseur, epaisseur+1):
        for dy in range(-epaisseur, epaisseur+1):
            if dx != 0 or dy != 0:
                canvas.create_text(x+dx, y+dy, text=texte, font=font, fill=contour, tags=tag)
    canvas.create_text(x, y, text=texte, font=font, fill=fill, tags=tag)

# ── Savoir quand les deux joueurs sont prets ──────────────────────────────────  

def toggle_pret(numero):
    global pret_j1, pret_j2
    
    if numero == 1:
        pret_j1 = not pret_j1
        if pret_j1:
            btn_Pret_J1.configure(fg_color="green")
    
    if numero == 2:
        pret_j2 = not pret_j2
        if pret_j2:
            canvas.itemconfig(btn_Pret_J2_contour, fill="green")
    
    if pret_j1 and pret_j2:
        btn_Pret_J1.destroy()
        canvas.delete(btn_Pret_J2_contour)
        canvas.delete(btn_Pret_J2)
        canvas.delete(Waiting)
        image = ctk.CTkImage(light_image=Image.open("images/point_interrogation.png"), size=(120, 100))
        labelj2 = ctk.CTkLabel(app, image=image, text="", fg_color="#0f3460")
        canvas.create_window(640, 360, anchor="center", window=labelj2)
        texte_contour(canvas, 500, 360, "VS", ("Lemon Milk", 60, "bold"), "black", tag="score")
        canvas.create_text(500, 360, text="VS", font=("Lemon Milk", 60, "bold"), fill="gold")
        Lancer_jeu()

# ── Attente des deux Participants ──────────────────────────────────  

def Wait(points=1):
    if not (pret_j1 and pret_j2):
        texte = "Waiting" + "." * points
        canvas.itemconfig(Waiting, text=texte)
        prochain = (points % 3) + 1 
        app.after(500, Wait, prochain)

# ── Lancement du jeu ──────────────────────────────────        

def Lancer_jeu():
    Init_Manche()
    Temps()

# ── Choisir Pierre / Feuille / Ciseaux ──────────────────────────────────

def Choix(x , j):  
    if j == 1:    
        global j1_a_pick , chxj1 , chxj2 ,btn_Retour, pick_j1 , imagej1 , imagej2, seconde
        if pret_j1 and pret_j2 and not j1_a_pick:
            if x == 1:
                imagej1 = ctk.CTkImage(light_image=Image.open("images/pierre.png"), size=(120, 100))
                pick_j1 = 1
            elif x == 2:
                imagej1 = ctk.CTkImage(light_image=Image.open("images/Feuille.png"), size=(120, 100))
                pick_j1 = 2
            elif x == 3:
                imagej1 = ctk.CTkImage(light_image=Image.open("images/Ciseaux.png"), size=(120, 100))
                pick_j1 = 3

            labelj1 = ctk.CTkLabel(app, image=imagej1, text="", fg_color="#0f3460")
            chxj1 = canvas.create_window(360, 360, anchor="center", window=labelj1)
            labelj1.ctk_image = imagej1
            j1_a_pick = True
            if seconde >= 3:    
                btn_Retour = ctk.CTkButton(app,text="retour",font=("Lemon Milk", 15, "bold"),text_color="black",width=70, height=30, fg_color="red", hover_color="#ff4f4f",corner_radius=0, command=Retour)
                canvas.create_window(360, 430, anchor="center", window=btn_Retour)
    if j == 2:
        if x == 1:
            imagej2 = ctk.CTkImage(light_image=Image.open("images/pierre.png"), size=(120, 100))
        elif x == 2:
            imagej2 = ctk.CTkImage(light_image=Image.open("images/Feuille.png"), size=(120, 100))
        elif x == 3:
            imagej2 = ctk.CTkImage(light_image=Image.open("images/Ciseaux.png"), size=(120, 100))
        labelj2 = ctk.CTkLabel(app, image=imagej2, text="", fg_color="#0f3460")
        chxj2 = canvas.create_window(640, 360, anchor="center", window=labelj2)


# ── Revenir Sur son choix ──────────────────────────────────

def Retour():
    if seconde >= 2:
        global j1_a_pick
        btn_Retour.destroy()
        j1_a_pick = False
        canvas.delete(chxj1)

# ── Barre de temps ──────────────────────────────────

def Temps(cpt =10,b=1.0):
    global seconde , j1_a_pick , pick_j2 , pick_j1 , imagej1 , chxj1
    if cpt >= 0:
        barre.set(b)
        canvas.itemconfig(t, text=""+str(cpt)+" s")
        seconde = cpt - 1
        app.after(1000, Temps, cpt-1, round(b-0.1, 1))
    if cpt <= 2 and j1_a_pick:
        try :
            btn_Retour.destroy()
        except:
            None
    if cpt == 0 and not j1_a_pick:
        imagej1 = ctk.CTkImage(light_image=Image.open("images/Croix_rouge.png"), size=(120, 100))
        label = ctk.CTkLabel(app, image=imagej1, text="", fg_color="#0f3460")
        chxj1 = canvas.create_window(360, 360, anchor="center", window=label)
        label.ctk_image = imagej1
        j1_a_pick = True
        pick_j1 = 4
    if cpt == 0 :
        Choix(pick_j2, 2)
        FinManche()

# ── Fin de Manche ──────────────────────────────────

def FinManche():
    global pick_j2 , pick_j1 , score_j1 , score_j2 , fin_manche
    GagneManche(pick_j1,pick_j2)
    if score_j1 == 3 or score_j2 == 3 :
        if score_j1 == 3:
            canvas.delete(Résulat)
            canvas.create_text(500, 450, text="Partie Gagne", font=("Lemon Milk", 50, "bold"), fill="green")
            app.after(3000, FinJeu)
        if score_j2 == 3:
            canvas.delete(Résulat)
            canvas.create_text(500, 450, text="Partie Perdu", font=("Lemon Milk", 50, "bold"), fill="red")
            app.after(3000, FinJeu)
    if fin_manche:
        app.after(3000, Lancer_jeu)

# ── Gagne Manche ──────────────────────────────────
    
def GagneManche(j1 , j2):
    global score_j1 , score_j2 , Résulat , fin_manche
    if j1 == 4:
        Résulat = canvas.create_text(500, 450, text="L'adversaire Gagne", font=("Lemon Milk", 30, "bold"), fill="red")
        MiseAJourScore(2)
        fin_manche = True
    if j2 == 4:
        Résulat = canvas.create_text(500, 450, text="Vous Gagnez", font=("Lemon Milk", 30, "bold"), fill="green")
        MiseAJourScore(1)
        fin_manche = True
    if j1 == 1 and j2 == 3 or j1 == 2 and j2 == 1 or j1 == 3 and j2 == 2:
        Résulat = canvas.create_text(500, 450, text="Vous Gagnez", font=("Lemon Milk", 30, "bold"), fill="green")
        MiseAJourScore(1)
        fin_manche = True
    if j1 == 3 and j2 == 1 or j1 == 1 and j2 == 2 or j1 == 2 and j2 == 3:
        Résulat = canvas.create_text(500, 450, text="L'adversaire Gagne", font=("Lemon Milk", 30, "bold"), fill="red")
        MiseAJourScore(2)
        fin_manche = True
    if j1 == 1 and j2 == 1 or j1 == 2 and j2 == 2 or j1 == 3 and j2 == 3:
        Résulat = canvas.create_text(500, 450, text="égalité", font=("Lemon Milk", 30, "bold"), fill="grey")
        fin_manche = True

# ── Mise à jour Score ──────────────────────────────────

def MiseAJourScore(j):
    global score_j1, score_j2 , score
    if j == 1 :
        score_j1 += 1
        canvas.delete(score)
        score = canvas.create_text(500, 160, text=""+str(score_j1)+" : "+str(score_j2)+"", font=("Lemon Milk", 50, "bold"), fill= "Black")
    if j == 2 :
        score_j2 += 1
        canvas.delete(score)
        score = canvas.create_text(500, 160, text=""+str(score_j1)+" : "+str(score_j2)+"", font=("Lemon Milk", 50, "bold"), fill= "Black")
        
# ── init Manche ──────────────────────────────────
def Init_Manche():
    global j1_a_pick , pick_j2 , fin_manche , chxj1 , chxj2
    j1_a_pick = False
    fin_manche = False
    pick_j2 = randint(1,3)
    try:
        canvas.delete(Résulat)
        canvas.delete(chxj1)
        canvas.delete(chxj2)
    except:
        None

def FinJeu():
    app.quit()
    app.destroy()
    subprocess.Popen([sys.executable, r"C:\Users\thomas.hervouet\Documents\GitHub\Pierre_Feuille_Ciseaux_GR6\Fichier Python\Pierre-Feuille-Ciseaux"])
    


# ── Création Fenetre ──────────────────────────────────

ctk.set_appearance_mode("light")
app = ctk.CTk()
app.title("Pierre Feuille Ciseaux")
app.geometry("1000x800")

# ── Image de fond avec Canvas ──────────────────────────────────
Fond = Image.open("images\Arène.png").resize((1000, 800))
fond_tk = ImageTk.PhotoImage(Fond)

canvas = tk.Canvas(app, width=1000, height=800, highlightthickness=0, bd=0)
canvas.place(x=0, y=0)
canvas.create_image(0, 0, anchor="nw", image=fond_tk)

# ── Tous tes labels placés SUR le canvas ──────────────────────

texte_contour(canvas, 280, 80, "Pierre", ("Lemon Milk", 50, "bold"), "black", None)
canvas.create_text(280, 80, text="Pierre", font=("Lemon Milk", 50, "bold"), fill="grey")

texte_contour(canvas, 500, 80, "Feuille", ("Lemon Milk", 50, "bold"), "black", None)
canvas.create_text(500, 80, text="Feuille", font=("Lemon Milk", 50, "bold"), fill="white")

texte_contour(canvas, 750, 80, "Ciseaux", ("Lemon Milk", 50, "bold"), "black", None)
canvas.create_text(750, 80, text="Ciseaux", font=("Lemon Milk", 50, "bold"), fill="lightblue")

score = canvas.create_text(500, 160, text="0 : 0", font=("Lemon Milk", 50, "bold"), fill= "Black")

Waiting = canvas.create_text(500, 360, text="Waiting...", font=("Lemon Milk", 60, "bold"), fill="white")

j1 = canvas.create_text(200, 250, text="Joueur 1", font=("Lemon Milk", 40, "bold"), fill="black")

j2 = canvas.create_text(800, 250, text="Joueur 2", font=("Lemon Milk", 40, "bold"), fill="black")

t = canvas.create_text(500, 500, text="10 s", font=("Lemon Milk", 25 , "bold"), fill="black")

btn_Pret_J2_contour = canvas.create_rectangle(725, 439, 875, 491, fill="red", outline="")
btn_Pret_J2 = canvas.create_text(800, 465,text="Pret",font=("Lemon Milk", 30, "bold"), fill="black")


# ── Bouton Pierre ───────────────────────────────────────────────────────────────
pierre = ctk.CTkImage(light_image=Image.open("images/pierre.png"), size=(80, 80))

btn_pierre = ctk.CTkButton(
    app, 
    image = pierre,
    text="", 
    width=120, 
    height=100, 
    fg_color="#0f3460",
    hover_color="#1a4a80", 
    corner_radius=0,
    command=lambda: Choix(1 , 1)
)
canvas.create_window(310, 660, anchor="center", window=btn_pierre)

# ── Bouton Feuille ───────────────────────────────────────────────────────────────
feuille = ctk.CTkImage(light_image=Image.open("images/feuille.png"), size=(80, 80))

btn_feuille = ctk.CTkButton(
    app, 
    image = feuille,
    text="", 
    width=120, 
    height=100, 
    fg_color="#0f3460",
    hover_color="#1a4a80", 
    corner_radius=0, 
    command=lambda: Choix(2 , 1)
)
canvas.create_window(500, 660, anchor="center", window=btn_feuille)

# ── Bouton Ciseaux ────────────────────────────────────────────────────────────────
ciseaux = ctk.CTkImage(light_image=Image.open("images/ciseaux.png"), size=(80, 80))

btn_ciseaux = ctk.CTkButton(
    app,
    image = ciseaux, 
    text="", 
    width=120, 
    height=100, 
    fg_color="#0f3460",
    hover_color="#1a4a80", 
    corner_radius=0, 
    command=lambda: Choix(3 , 1)
)
canvas.create_window(690, 660, anchor="center", window=btn_ciseaux)

# ── Bouton Pret J1 ────────────────────────────────────────────────────────────────
btn_Pret_J1 = ctk.CTkButton(
    app,
    text="Pret", 
    font=("Lemon Milk", 40, "bold"),
    text_color="black",
    width=150, 
    height=50, 
    fg_color="red", 
    hover_color="#ff4f4f",
    corner_radius=0, 
    command=lambda: toggle_pret(1)
)
canvas.create_window(200, 465, anchor="center", window=btn_Pret_J1)

# ── Barre de temps ────────────────────────────────────────────────────────────────
barre = ctk.CTkProgressBar(
    app, 
    width=600, 
    height=10, 
    progress_color="green",
    corner_radius=0, 
    fg_color="red",
)
barre.set(1.0)
canvas.create_window(500, 530, anchor="center", window=barre)

# ── Lancement de la fenêtre ────────────────────────────────────────────────

Init_jeu()
jpret = 0
pret_j1 = False
pret_j2 = False
score_j1 = 0
score_j2 = 0
toggle_pret(2)
Wait()
app.mainloop()



