import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

# ── Paramètres de la fenêtre ───────────────────────────────────────────────
ctk.set_appearance_mode("light")
app = ctk.CTk()
app.title("Pierre Feuille Ciseaux")
app.geometry("1000x800")
app.configure(fg_color="#7B8B8E")

PARCHEMIN   = "#D4B13B"
BRUN_BOIS   = "#000000"
OR          = "#648195"
TEXTE_FONCE = "#2C1A0E"

# ── Image de fond ──────────────────────────────────────────────────────────
base_img = Image.open("images/interface_principal.png").resize((1000, 800), Image.LANCZOS)
draw = ImageDraw.Draw(base_img)

try:
    font_titre = ImageFont.truetype("arial.ttf", 48)
    font_label = ImageFont.truetype("arial.ttf", 30)
except:
    font_titre = ImageFont.load_default()
    font_label = font_titre


bg_image = ctk.CTkImage(light_image=base_img, size=(1000, 800))
bg_label = ctk.CTkLabel(app, image=bg_image, text="")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

icone = ctk.CTkImage(light_image=Image.open("images/bot.png"), size=(50, 50))
icone2 = ctk.CTkImage(light_image=Image.open("images/ami.png"), size=(50, 50))
icone3 = ctk.CTkImage(light_image=Image.open("images/tournoi.png"), size=(50, 50))
icone4 = ctk.CTkImage(light_image=Image.open("images/ISP.png"), size=(50, 50))
icone5 = ctk.CTkImage(light_image=Image.open("images/Classement.png"), size=(50, 50))
icone6 = ctk.CTkImage(light_image=Image.open("images/stats.png"), size=(50, 50))
icone7 = ctk.CTkImage(light_image=Image.open("images/pdp.png"), size=(50, 50))

# ── Bouton Jouer contre un bot ────────────────────────────────────────────────────────
btn_bot = ctk.CTkButton(
    app,
    text="Jouer contre un bot",
    font=("Melon Milk", 24, "bold"),
    text_color=BRUN_BOIS,
    width=300, height=200,
    fg_color=PARCHEMIN,
    hover_color=OR,
    corner_radius=0,
    border_width=0,
    image=icone,
    compound="left", 
)
btn_bot.place(x=30, y=50)

# ── Bouton Jouer contre un ami ───────────────────────────────────────────────────
btn_ami = ctk.CTkButton(
    app,
    text="Jouer contre un ami",
    font=("Melon Milk", 24, "bold"),
    text_color=BRUN_BOIS,
    width=300, height=200,
    fg_color=PARCHEMIN,
    hover_color=OR,
    corner_radius=0,
    border_width=0,
    image=icone2,
    compound="left",
)
btn_ami.place(x=355, y=50)

# ── Bouton tournoi ───────────────────────────────────────────────────
btn_tournoi = ctk.CTkButton(
    app,
    text="Tournoi",
    font=("Melon Milk", 24, "bold"),
    text_color=BRUN_BOIS,
    width=300, height=200,
    fg_color=PARCHEMIN,
    hover_color=OR,
    corner_radius=0,
    border_width=0,
    image=icone3,
    compound="left",
)
btn_tournoi.place(x=680, y=50)

# ── Bouton Amis ───────────────────────────────────────────────────
btn_amis = ctk.CTkButton(
    app,
    text="Amis",
    font=("Melon Milk", 24, "bold"),
    text_color=BRUN_BOIS,
    width=300, height=75,
    fg_color=PARCHEMIN,
    hover_color=OR,
    corner_radius=0,
    border_width=0,
    image=icone4,
    compound="left",
)
btn_amis.place(x=30, y=400)

# ── Bouton Classement ───────────────────────────────────────────────────
btn_Classement = ctk.CTkButton(
    app,
    text="Classement",
    font=("Melon Milk", 24, "bold"),
    text_color=BRUN_BOIS,
    width=300, height=75,
    fg_color=PARCHEMIN,
    hover_color=OR,
    corner_radius=0,
    border_width=0,
    image=icone5,
    compound="left",
)
btn_Classement.place(x=30, y=500)

# ── Bouton Statistiques ───────────────────────────────────────────────────
btn_stats = ctk.CTkButton(
    app,
    text="Statistiques",
    font=("Melon Milk", 24, "bold"),
    text_color=BRUN_BOIS,
    width=300, height=75,
    fg_color=PARCHEMIN,
    hover_color=OR,
    corner_radius=0,
    border_width=0,
    image=icone6,
    compound="left",
)
btn_stats.place(x=30, y=600)

# ── Bouton photo de profil ───────────────────────────────────────────────────
btn_photoprofil = ctk.CTkButton(
    app,
    text="Photo de profil",
    font=("Melon Milk", 24, "bold"),
    text_color=BRUN_BOIS,
    width=300, height=75,
    fg_color=PARCHEMIN,
    hover_color=OR,
    corner_radius=0,
    border_width=0,
    image=icone7,
    compound="left",
)
btn_photoprofil.place(x=30, y=700)

# ── Lancement de la fenêtre ────────────────────────────────────────────────
app.mainloop()