import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

# ── Paramètres de la fenêtre ───────────────────────────────────────────────
ctk.set_appearance_mode("light")
app = ctk.CTk()
app.title("Pierre Feuille Ciseaux")
app.geometry("400x500")
app.configure(fg_color="#7B8B8E")

PARCHEMIN   = "#D4B13B"
BRUN_BOIS   = "#000000"
OR          = "#648195"
TEXTE_FONCE = "#2C1A0E"

# ── Image de fond ──────────────────────────────────────────────────────────
base_img = Image.open("images/image_de_base.png").resize((1000, 2000), Image.LANCZOS)
draw = ImageDraw.Draw(base_img)

try:
    font_titre = ImageFont.truetype("arial.ttf", 48)
    font_label = ImageFont.truetype("arial.ttf", 30)
except:
    font_titre = ImageFont.load_default()
    font_label = font_titre


bg_image = ctk.CTkImage(light_image=base_img, size=(500, 500))
bg_label = ctk.CTkLabel(app, image=bg_image, text="")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

icone = ctk.CTkImage(light_image=Image.open("images/bot.png"), size=(50, 50))

# ── Bouton fermer ────────────────────────────────────────────────────────
btn_bot = ctk.CTkButton(
    app,
    text="",
    font=("Melon Milk", 24, "bold"),
    text_color=BRUN_BOIS,
    width=50, height=50,
    fg_color=PARCHEMIN,
    hover_color=OR,
    corner_radius=0,
    border_width=0
)
btn_bot.place(x=350, y=0)

# ── Lancement de la fenêtre ────────────────────────────────────────────────
app.mainloop()