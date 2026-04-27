"""
fenetre_inscription.py — Fenêtre de création de compte connectée au serveur.
"""
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
from network_client import GameClient

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
ROUGE       = "#8B1A1A"
VERT        = "#2A6B3A"

# ── Client réseau ──────────────────────────────────────────────────────────
client = GameClient(host="127.0.0.1", port=5000)

try:
    client.connect()
except Exception:
    pass  # Le message d'erreur s'affichera via le label_statut

# ── Image de fond ──────────────────────────────────────────────────────────
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

draw_text_shadow(draw, (60, 40),  "Créer un compte",     font_titre)
draw_text_shadow(draw, (40, 120), "Pseudo",               font_label)
draw_text_shadow(draw, (40, 210), "Mot de passe",         font_label)
draw_text_shadow(draw, (40, 300), "Valider mot de passe", font_label)

bg_image = ctk.CTkImage(light_image=base_img, size=(400, 500))
bg_label = ctk.CTkLabel(app, image=bg_image, text="")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# ── Champs de saisie ──────────────────────────────────────────────────────
entry_pseudo = ctk.CTkEntry(
    app, width=200, height=35,
    fg_color=PARCHEMIN, border_color=BRUN_BOIS,
    border_width=2, text_color=TEXTE_FONCE, corner_radius=6
)
entry_pseudo.place(x=40, y=155)

entry_mdp = ctk.CTkEntry(
    app, width=300, height=35,
    fg_color=PARCHEMIN, border_color=BRUN_BOIS,
    border_width=2, text_color=TEXTE_FONCE, corner_radius=6, show="*"
)
entry_mdp.place(x=40, y=245)

entry_mdp2 = ctk.CTkEntry(
    app, width=300, height=35,
    fg_color=PARCHEMIN, border_color=BRUN_BOIS,
    border_width=2, text_color=TEXTE_FONCE, corner_radius=6, show="*"
)
entry_mdp2.place(x=40, y=335)

# ── Label de statut ────────────────────────────────────────────────────────
label_statut = ctk.CTkLabel(
    app, text="", font=("Arial", 12, "bold"),
    fg_color="transparent", text_color=ROUGE
)
label_statut.place(x=40, y=395)

# ── Logique d'inscription ──────────────────────────────────────────────────
def on_message_serveur(msg):
    """Appelé depuis le thread réseau — on utilise app.after() pour toucher l'UI."""
    def update():
        t = msg.get("type", "")
        texte = msg.get("msg", "")
        if t == "ok":
            label_statut.configure(text=f"✓ {texte}", text_color=VERT)
            # Ouvrir la fenêtre de connexion après 1,5 s
            app.after(1500, ouvrir_connexion)
        elif t == "error":
            label_statut.configure(text=f"✗ {texte}", text_color=ROUGE)
    app.after(0, update)

client.set_on_message(on_message_serveur)

def valider_inscription():
    pseudo = entry_pseudo.get().strip()
    mdp    = entry_mdp.get()
    mdp2   = entry_mdp2.get()

    # Vérifications locales
    if not pseudo:
        label_statut.configure(text="✗ Le pseudo est vide.", text_color=ROUGE)
        return
    if len(pseudo) < 3:
        label_statut.configure(text="✗ Pseudo trop court (min. 3 caractères).", text_color=ROUGE)
        return
    if len(mdp) < 4:
        label_statut.configure(text="✗ Mot de passe trop court (min. 4 caractères).", text_color=ROUGE)
        return
    if mdp != mdp2:
        label_statut.configure(text="✗ Les mots de passe ne correspondent pas.", text_color=ROUGE)
        return

    if not client.connected:
        label_statut.configure(text="✗ Impossible de joindre le serveur.", text_color=ROUGE)
        return

    label_statut.configure(text="Envoi en cours…", text_color=TEXTE_FONCE)
    client.register(pseudo, mdp)

def ouvrir_connexion():
    app.destroy()
    import Interface_Connexion  # noqa: F401 — lance la fenêtre de connexion

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
    command=valider_inscription
)
btn_valider.place(x=40, y=420)

btn_connexion = ctk.CTkButton(
    app,
    text="Se connecter",
    font=("Arial", 13),
    text_color=BRUN_BOIS,
    width=50, height=10,
    fg_color=PARCHEMIN,
    hover_color=OR,
    corner_radius=6,
    border_width=0,
    command=ouvrir_connexion
)
btn_connexion.place(x=250, y=455)

# ── Lancement ──────────────────────────────────────────────────────────────
app.mainloop()