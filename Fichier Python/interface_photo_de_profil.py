import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import shutil
import os
from tkinter import filedialog
 
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
 
# ── Chemin de sauvegarde de la photo de profil ────────────────────────────
PDP_PATH = "images/profil/photo_de_profil.png"
os.makedirs("images/profil", exist_ok=True)
 
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
 
def ouvrir_interface():
    app.destroy()
    import interface_principale
# ── Bouton fermer ─────────────────────────────────────────────────────────
btn_fermer = ctk.CTkButton(
    app,
    text="✘",
    font=("Melon Milk", 24, "bold"),
    text_color=BRUN_BOIS,
    width=50, height=50,
    fg_color=PARCHEMIN,
    hover_color=OR,
    corner_radius=0,
    border_width=0,
    command=ouvrir_interface
)
btn_fermer.place(x=350, y=0)
 
# ── Cadre central parchemin ───────────────────────────────────────────────
frame = ctk.CTkFrame(
    app,
    width=300, height=380,
    fg_color=OR,
    corner_radius=12,
    border_width=3,
    border_color=TEXTE_FONCE
)
frame.place(x=50, y=60)
frame.pack_propagate(False)
 
# ── Titre ─────────────────────────────────────────────────────────────────
lbl_titre = ctk.CTkLabel(
    frame,
    text="⚔  Photo de profil  ⚔",
    font=("Georgia", 15, "bold"),
    text_color=TEXTE_FONCE,
    fg_color="transparent"
)
lbl_titre.pack(pady=(14, 4))
 
sep = ctk.CTkFrame(frame, height=2, fg_color=TEXTE_FONCE, corner_radius=0)
sep.pack(fill="x", padx=20, pady=(0, 16))
 
# ── Chargement / affichage de la PDP ─────────────────────────────────────
PDP_SIZE = 140
pdp_ctk_image = None  # référence gardée en mémoire
 
def charger_pdp() -> ctk.CTkImage:
    """Charge la PDP sauvegardée, ou crée un placeholder si absente."""
    if os.path.exists(PDP_PATH):
        img = Image.open(PDP_PATH).convert("RGBA")
    else:
        img = Image.new("RGBA", (PDP_SIZE, PDP_SIZE), "#8B7355")
        d = ImageDraw.Draw(img)
        d.ellipse([6, 6, PDP_SIZE - 6, PDP_SIZE - 6], fill="#C9A227", outline=TEXTE_FONCE, width=3)
        try:
            fnt = ImageFont.truetype("arial.ttf", 14)
        except:
            fnt = ImageFont.load_default()
        txt = "Aucune photo"
        bbox = d.textbbox((0, 0), txt, font=fnt)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text(((PDP_SIZE - tw) // 2, (PDP_SIZE - th) // 2), txt, font=fnt, fill=TEXTE_FONCE)
 
    # recadrage carré centré
    w, h = img.size
    m = min(w, h)
    img = img.crop(((w - m) // 2, (h - m) // 2, (w + m) // 2, (h + m) // 2))
    img = img.resize((PDP_SIZE, PDP_SIZE), Image.LANCZOS)
    return ctk.CTkImage(light_image=img, size=(PDP_SIZE, PDP_SIZE))
 
pdp_ctk_image = charger_pdp()
 
lbl_pdp = ctk.CTkLabel(
    frame,
    image=pdp_ctk_image,
    text="",
    fg_color="transparent"
)
lbl_pdp.pack(pady=(0, 14))
 
# ── Bouton : changer la photo ─────────────────────────────────────────────
def changer_photo():
    global pdp_ctk_image
    chemin = filedialog.askopenfilename(
        title="Choisir une photo de profil",
        filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp")]
    )
    if not chemin:
        return  # annulé
 
    # Sauvegarde en PNG dans le dossier du jeu
    img = Image.open(chemin).convert("RGBA")
    w, h = img.size
    m = min(w, h)
    img = img.crop(((w - m) // 2, (h - m) // 2, (w + m) // 2, (h + m) // 2))
    img.save(PDP_PATH)
 
    # Mise à jour de l'affichage
    pdp_ctk_image = charger_pdp()
    lbl_pdp.configure(image=pdp_ctk_image)
    lbl_statut.configure(text="✔ Photo mise à jour !", text_color="#1A4A1A")
 
btn_changer = ctk.CTkButton(
    frame,
    text="📁  Choisir une image",
    font=("Georgia", 13, "bold"),
    text_color=TEXTE_FONCE,
    width=200, height=38,
    fg_color="#C9A227",
    hover_color=OR,
    corner_radius=8,
    border_width=2,
    border_color=TEXTE_FONCE,
    command=changer_photo
)
btn_changer.pack(pady=(0, 8))
 
# ── Bouton : supprimer la photo ───────────────────────────────────────────
def supprimer_photo():
    global pdp_ctk_image
    if os.path.exists(PDP_PATH):
        os.remove(PDP_PATH)
    pdp_ctk_image = charger_pdp()
    lbl_pdp.configure(image=pdp_ctk_image)
    lbl_statut.configure(text="Photo supprimée.", text_color="#6B3A2A")
 
btn_supprimer = ctk.CTkButton(
    frame,
    text="🗑  Supprimer",
    font=("Georgia", 12),
    text_color=TEXTE_FONCE,
    width=200, height=32,
    fg_color="#A89050",
    hover_color="#8B3A2A",
    corner_radius=8,
    border_width=2,
    border_color=TEXTE_FONCE,
    command=supprimer_photo
)
btn_supprimer.pack(pady=(0, 6))
 
# ── Label de statut ───────────────────────────────────────────────────────
lbl_statut = ctk.CTkLabel(
    frame,
    text="",
    font=("Georgia", 11, "italic"),
    text_color="#1A4A1A",
    fg_color="transparent"
)
lbl_statut.pack()
 
# ── Lancement de la fenêtre ────────────────────────────────────────────────
app.mainloop()
# import customtkinter as ctk
# from PIL import Image, ImageDraw, ImageFont

# # ── Paramètres de la fenêtre ───────────────────────────────────────────────
# ctk.set_appearance_mode("light")
# app = ctk.CTk()
# app.title("Pierre Feuille Ciseaux")
# app.geometry("400x500")
# app.configure(fg_color="#7B8B8E")

# PARCHEMIN   = "#D4B13B"
# BRUN_BOIS   = "#000000"
# OR          = "#648195"
# TEXTE_FONCE = "#2C1A0E"

# # ── Image de fond ──────────────────────────────────────────────────────────
# base_img = Image.open("images/image_de_base.png").resize((1000, 2000), Image.LANCZOS)
# draw = ImageDraw.Draw(base_img)

# try:
#     font_titre = ImageFont.truetype("arial.ttf", 48)
#     font_label = ImageFont.truetype("arial.ttf", 30)
# except:
#     font_titre = ImageFont.load_default()
#     font_label = font_titre


# bg_image = ctk.CTkImage(light_image=base_img, size=(500, 500))
# bg_label = ctk.CTkLabel(app, image=bg_image, text="")
# bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# def ouvrir_interface():
#     app.destroy()
#     import interface_principal

# # ── Bouton fermer ────────────────────────────────────────────────────────
# btn_bot = ctk.CTkButton(
#     app,
#     text="✘",
#     font=("Melon Milk", 24, "bold"),
#     text_color=BRUN_BOIS,
#     width=50, height=50,
#     fg_color=PARCHEMIN,
#     hover_color=OR,
#     corner_radius=0,
#     border_width=0,
#     command=ouvrir_interface
# )
# btn_bot.place(x=350, y=0)

# # ── Lancement de la fenêtre ────────────────────────────────────────────────
# app.mainloop()