#from random import randint
import customtkinter as ctk
import tkinter as tk
from PIL import Image , ImageTk

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
            btn_Pret_J2.configure(fg_color="green")
    
    if pret_j1 and pret_j2:
        btn_Pret_J1.destroy()
        btn_Pret_J2.destroy()
        canvas.delete(Waiting)
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
    texte_contour(canvas, 500, 360, "VS", ("Lemon Milk", 60, "bold"), "black", tag="score")
    canvas.create_text(500, 360, text="VS", font=("Lemon Milk", 60, "bold"), fill="gold")
    Temps()

# ── Choisir Pierre / Feuille / Ciseaux ──────────────────────────────────

def Choix(x):
    global pick_j1 , chx , btn_Retour
    if pret_j1 and pret_j2 and not pick_j1:
        if x == 1:
            image = ctk.CTkImage(light_image=Image.open("images/pierre.png"), size=(120, 100))
        elif x == 2:
            image = ctk.CTkImage(light_image=Image.open("images/Feuille.png"), size=(120, 100))
        elif x == 3:
            image = ctk.CTkImage(light_image=Image.open("images/Ciseaux.png"), size=(120, 100))

        label = ctk.CTkLabel(app, image=image, text="", fg_color="#0f3460")
        chx = canvas.create_window(360, 360, anchor="center", window=label)
        label.ctk_image = image
        pick_j1 = True
        btn_Retour = ctk.CTkButton(app,text="retour",font=("Lemon Milk", 15, "bold"),text_color="black",width=70, height=30, fg_color="red", hover_color="#ff4f4f",corner_radius=0, command=Retour)
        canvas.create_window(360, 430, anchor="center", window=btn_Retour)

# ── Revenir Sur son choix ──────────────────────────────────

def Retour():
    if seconde >= 2:
        global pick_j1
        btn_Retour.destroy()
        pick_j1 = False
        canvas.delete(chx)

# ── Barre de temps ──────────────────────────────────

def Temps(cpt =10,b=1.0):
    global seconde
    if cpt >= 0:
        barre.set(b)
        canvas.itemconfig(t, text=""+str(cpt)+" s")
        seconde = cpt - 1
        app.after(1000, Temps, cpt-1, round(b-0.1, 1))
    if cpt <= 2 and pick_j1 == True:
        btn_Retour.destroy()
    if cpt == 0 and pick_j1 == False:
        croix = ctk.CTkImage(light_image=Image.open("images/Croix_rouge.png"), size=(120, 100))
        label = ctk.CTkLabel(app, image=croix, text="", fg_color="#0f3460")
        canvas.create_window(360, 360, anchor="center", window=label)
        label.ctk_image = croix
        
# ── Création Fenetre ──────────────────────────────────

ctk.set_appearance_mode("light")
app = ctk.CTk()
app.title("Pierre Feuille Ciseaux")
app.geometry("1000x800")

# ── Image de fond avec Canvas ──────────────────────────────────
Fond = Image.open("images/Arène.png").resize((1000, 800))
fond_tk = ImageTk.PhotoImage(Fond)

canvas = tk.Canvas(app, width=1000, height=800, highlightthickness=0, bd=0)
canvas.place(x=0, y=0)
canvas.create_image(0, 0, anchor="nw", image=fond_tk)
canvas.image = fond_tk  # garder la référence

# ── Tous tes labels placés SUR le canvas ──────────────────────

texte_contour(canvas, 280, 80, "Pierre", ("Lemon Milk", 50, "bold"), "black", None)
canvas.create_text(280, 80, text="Pierre", font=("Lemon Milk", 50, "bold"), fill="grey")

texte_contour(canvas, 500, 80, "Feuille", ("Lemon Milk", 50, "bold"), "black", None)
canvas.create_text(500, 80, text="Feuille", font=("Lemon Milk", 50, "bold"), fill="white")

texte_contour(canvas, 750, 80, "Ciseaux", ("Lemon Milk", 50, "bold"), "black", None)
canvas.create_text(750, 80, text="Ciseaux", font=("Lemon Milk", 50, "bold"), fill="lightblue")

score = canvas.create_text(500, 160, text="0 : 0", font=("Lemon Milk", 50, "bold"), fill= "Black")
texte_contour(canvas, 500, 160, "0 : 0", ("Lemon Milk", 50, "bold"), "lightgrey", tag="score")

Waiting = canvas.create_text(500, 360, text="Waiting...", font=("Lemon Milk", 60, "bold"), fill="white")

j1 = canvas.create_text(200, 250, text="Joueur 1", font=("Lemon Milk", 40, "bold"), fill="black")

j2 = canvas.create_text(800, 250, text="Joueur 2", font=("Lemon Milk", 40, "bold"), fill="black")

t = canvas.create_text(500, 500, text="10 s", font=("Lemon Milk", 25 , "bold"), fill="black")

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
    command=lambda: Choix(1)
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
    command=lambda: Choix(2)
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
    command=lambda: Choix(3)
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

# ── Bouton Pret J2 ────────────────────────────────────────────────────────────────
btn_Pret_J2 = ctk.CTkButton(
    app,
    text="Pret",
    font=("Lemon Milk", 40, "bold"),
    text_color="black",
    width=150, 
    height=50, 
    fg_color="red",
    hover_color="#ff4f4f",
    corner_radius=0, 
    command=lambda: toggle_pret(2)
)
canvas.create_window(800, 465, anchor="center", window=btn_Pret_J2)

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
pick_j1 = False
Wait()

app.mainloop()



