import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

# ── Paramètres de la fenêtre ───────────────────────────────────────────────
ctk.set_appearance_mode("light")
app = ctk.CTk()
app.title("Pierre Feuille Ciseaux")
app.geometry("400x500")
app.configure(fg_color="#7B8B8E")

PARCHEMIN   = "#F5E6C8"
BRUN_BOIS   = "#6B3A2A"
OR          = "#9E7D3B"
TEXTE_FONCE = "#2C1A0E"

# ── Image de fond avec texte dessiné dessus ────────────────────────────────
base_img = Image.open("images/interieur_chateau.png").resize((400, 500), Image.LANCZOS)
draw = ImageDraw.Draw(base_img)

try:
    font_titre = ImageFont.truetype("arial.ttf", 32)
    font_label = ImageFont.truetype("arial.ttf", 24)
except:
    font_titre = ImageFont.load_default()
    font_label = font_titre

def draw_text_shadow(draw, pos, text, font, color="#FFFCF6", shadow="#2C1A0E"):
    draw.text((pos[0]+2, pos[1]+2), text, font=font, fill=shadow)
    draw.text(pos, text, font=font, fill=color)

draw_text_shadow(draw, (60, 40),  "Créer un compte",    font_titre)
draw_text_shadow(draw, (40, 120), "Pseudo",              font_label)
draw_text_shadow(draw, (40, 210), "Mot de passe",        font_label)
draw_text_shadow(draw, (40, 300), "Valider mot de passe", font_label)

bg_image = ctk.CTkImage(light_image=base_img, size=(400, 500))
bg_label = ctk.CTkLabel(app, image=bg_image, text="")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# ── Champ pseudo ──────────────────────────────────────────────────────────
entry_pseudo = ctk.CTkEntry(
    app,
    width=200, height=35,
    fg_color=PARCHEMIN,
    border_color=BRUN_BOIS,
    border_width=2,
    text_color=TEXTE_FONCE,
    corner_radius=6
)
entry_pseudo.place(x=40, y=155)

# ── Champ mot de passe ────────────────────────────────────────────────────
entry_mdp = ctk.CTkEntry(
    app,
    width=300, height=35,
    fg_color=PARCHEMIN,
    border_color=BRUN_BOIS,
    border_width=2,
    text_color=TEXTE_FONCE,
    corner_radius=6,
    show="*"
)
entry_mdp.place(x=40, y=245)

# ── Champ valider mot de passe ────────────────────────────────────────────
entry_mdp2 = ctk.CTkEntry(
    app,
    width=300, height=35,
    fg_color=PARCHEMIN,
    border_color=BRUN_BOIS,
    border_width=2,
    text_color=TEXTE_FONCE,
    corner_radius=6,
    show="*"
)
entry_mdp2.place(x=40, y=335)

# ── Bouton Valider ────────────────────────────────────────────────────────
btn_valider = ctk.CTkButton(
    app,
    text="Valider",
    font=("Arial", 22, "bold"),
    text_color=PARCHEMIN,
    width=160, height=40,
    fg_color=BRUN_BOIS,
    hover_color=OR,
    corner_radius=8,
    border_width=0
)
btn_valider.place(x=40, y=420)

# ── Bouton Se connecter ───────────────────────────────────────────────────
btn_connexion = ctk.CTkButton(
    app,
    text="Se connecter",
    font=("Arial", 13),
    text_color=BRUN_BOIS,
    width=50, height=10,
    fg_color=PARCHEMIN,
    hover_color=OR,
    corner_radius=6,
    border_width=0
)
btn_connexion.place(x=250, y=455)

# ── Lancement de la fenêtre ────────────────────────────────────────────────
app.mainloop()