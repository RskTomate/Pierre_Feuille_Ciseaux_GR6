"""
fenetre_connexion.py — Fenêtre de connexion. Lance interface_principale après login.
"""
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
from network_client import GameClient

ctk.set_appearance_mode("light")
app = ctk.CTk()
app.title("Pierre Feuille Ciseaux")
app.geometry("400x500")
app.configure(fg_color="#7B8B8E")

PARCHEMIN   = "#F5E6C8"
BRUN_BOIS   = "#6B3A2A"
OR          = "#C8942A"
TEXTE_FONCE = "#2C1A0E"
ROUGE       = "#8B1A1A"
VERT        = "#2A6B3A"

client = GameClient(host="192.168.1.14", port=5000)
try:
    client.connect()
except Exception:
    pass

base_img = Image.open("images/porte.png").resize((400, 500), Image.LANCZOS)
draw = ImageDraw.Draw(base_img)
try:
    font_titre = ImageFont.truetype("arial.ttf", 36)
    font_label = ImageFont.truetype("arial.ttf", 26)
except Exception:
    font_titre = ImageFont.load_default()
    font_label = font_titre

def shadow(draw, pos, text, font, color="#F5E6C8", sh="#2C1A0E"):
    draw.text((pos[0]+2, pos[1]+2), text, font=font, fill=sh)
    draw.text(pos, text, font=font, fill=color)

shadow(draw, (50, 55),  "Se connecter", font_titre)
shadow(draw, (50, 135), "Pseudo",        font_label)
shadow(draw, (50, 245), "Mot de passe",  font_label)

bg_image = ctk.CTkImage(light_image=base_img, size=(400, 500))
ctk.CTkLabel(app, image=bg_image, text="").place(x=0, y=0, relwidth=1, relheight=1)

entry_style = dict(fg_color=PARCHEMIN, border_color=BRUN_BOIS,
                   border_width=2, text_color=TEXTE_FONCE, corner_radius=6)

textbox_pseudo = ctk.CTkEntry(app, width=200, height=35, **entry_style)
textbox_pseudo.place(x=50, y=175)

textbox_mdp = ctk.CTkEntry(app, width=300, height=35, show="*", **entry_style)
textbox_mdp.place(x=50, y=285)

label_statut = ctk.CTkLabel(app, text="", font=("Arial", 12, "bold"),
                             fg_color="transparent", text_color=ROUGE)
label_statut.place(x=50, y=330)

_username_en_cours = None

def on_message(msg):
    def update():
        t = msg.get("type", "")
        if t == "ok":
            label_statut.configure(text=f"✓ {msg.get('msg','')}", text_color=VERT)
            app.after(800, ouvrir_menu)
        elif t == "error":
            label_statut.configure(text=f"✗ {msg.get('msg','')}", text_color=ROUGE)
    app.after(0, update)

client.set_on_message(on_message)

def valider():
    global _username_en_cours
    pseudo = textbox_pseudo.get().strip()
    mdp    = textbox_mdp.get()
    if not pseudo or not mdp:
        label_statut.configure(text="✗ Remplis tous les champs.", text_color=ROUGE)
        return
    if not client.connected:
        label_statut.configure(text="✗ Serveur inaccessible.", text_color=ROUGE)
        return
    _username_en_cours = pseudo
    label_statut.configure(text="Connexion…", text_color=TEXTE_FONCE)
    client.login(pseudo, mdp)

def ouvrir_menu():
    app.destroy()
    import interface_principale
    interface_principale.lancer(client, _username_en_cours)

def ouvrir_inscription():
    app.destroy()
    import interface_créersoncompte  # noqa

ctk.CTkButton(app, text="Valider", font=("Arial", 22, "bold"),
              text_color=PARCHEMIN, width=160, height=40,
              fg_color=BRUN_BOIS, hover_color=OR, corner_radius=8,
              command=valider).place(x=120, y=365)

ctk.CTkButton(app, text="Pas de compte ?", font=("Arial", 13),
              text_color=BRUN_BOIS, width=50, height=10,
              fg_color=PARCHEMIN, hover_color=OR, corner_radius=6,
              command=ouvrir_inscription).place(x=220, y=455)

app.mainloop()