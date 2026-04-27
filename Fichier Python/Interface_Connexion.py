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
OR          = "#C8942A"
TEXTE_FONCE = "#2C1A0E"

# ── Image de fond avec texte dessiné dessus ────────────────────────────────
base_img = Image.open("images/porte.png").resize((400, 500), Image.LANCZOS)
draw = ImageDraw.Draw(base_img)

try:
    font_titre = ImageFont.truetype("arial.ttf", 36)
    font_label = ImageFont.truetype("arial.ttf", 26)
except:
    font_titre = ImageFont.load_default()
    font_label = font_titre

def draw_text_shadow(draw, pos, text, font, color="#F5E6C8", shadow="#2C1A0E"):
    draw.text((pos[0]+2, pos[1]+2), text, font=font, fill=shadow)
    draw.text(pos, text, font=font, fill=color)

draw_text_shadow(draw, (50, 55),  "Se connecter", font_titre)
draw_text_shadow(draw, (50, 135), "Pseudo",        font_label)
draw_text_shadow(draw, (50, 245), "Mot de passe",  font_label)

bg_image = ctk.CTkImage(light_image=base_img, size=(400, 500))
bg_label = ctk.CTkLabel(app, image=bg_image, text="")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

def ouvrir_inscription():
    app.destroy()
    import interface_créersoncompte

def ouvrir_interface():
    app.destroy()
    import interface_principal

# ── Champs de saisie ───────────────────────────────────────────────────────
textbox_pseudo = ctk.CTkEntry(
    app,
    width=200, height=35,
    fg_color=PARCHEMIN,
    border_color=BRUN_BOIS,
    border_width=2,
    text_color=TEXTE_FONCE,
    corner_radius=6
)
textbox_pseudo.place(x=50, y=175)

textbox_mdp = ctk.CTkEntry(
    app,
    width=300, height=35,
    fg_color=PARCHEMIN,
    border_color=BRUN_BOIS,
    border_width=2,
    text_color=TEXTE_FONCE,
    corner_radius=6,
    show="*"
)
textbox_mdp.place(x=50, y=285)

# ── Boutons ────────────────────────────────────────────────────────────────
btn_valider = ctk.CTkButton(
    app,
    text="Valider",
    font=("Arial", 22, "bold"),
    text_color=PARCHEMIN,
    width=160, height=40,
    fg_color=BRUN_BOIS,
    hover_color=OR,
    corner_radius=8,
    border_width=0,
    command=ouvrir_interface
)
btn_valider.place(x=120, y=350)

btn_compte = ctk.CTkButton(
    app,
    text="Pas de compte ?",
    font=("Arial", 13),
    text_color=BRUN_BOIS,
    width=50, height=10,
    fg_color=PARCHEMIN,
    hover_color=OR,
    corner_radius=6,
    border_width=0,
    command=ouvrir_inscription
)
btn_compte.place(x=220, y=455)

# ── Lancement de la fenêtre ────────────────────────────────────────────────
app.mainloop()