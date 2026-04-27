"""
interface_principale.py — Menu principal connecté au serveur.
Appelé après connexion réussie via lancer(client, username).
"""
import customtkinter as ctk
from PIL import Image
import os

PDP_PATH = "images/profil/photo_de_profil.png"


def lancer(client, username):
    ctk.set_appearance_mode("light")
    app = ctk.CTk()
    app.title("Pierre Feuille Ciseaux")
    app.geometry("1000x800")
    app.configure(fg_color="#7B8B8E")

    PARCHEMIN   = "#D4B13B"
    BRUN_BOIS   = "#000000"
    OR          = "#648195"

    # ── Fond ──────────────────────────────────────────────────────
    base_img = Image.open("images/interface_principal.png").resize((1000, 800), Image.LANCZOS)
    bg_image = ctk.CTkImage(light_image=base_img, size=(1000, 800))
    ctk.CTkLabel(app, image=bg_image, text="").place(x=0, y=0, relwidth=1, relheight=1)

    # ── Icônes ────────────────────────────────────────────────────
    icone  = ctk.CTkImage(light_image=Image.open("images/bot.png"),        size=(50, 50))
    icone2 = ctk.CTkImage(light_image=Image.open("images/ami.png"),        size=(50, 50))
    icone3 = ctk.CTkImage(light_image=Image.open("images/tournoi.png"),    size=(50, 50))
    icone4 = ctk.CTkImage(light_image=Image.open("images/ISP.png"),        size=(50, 50))
    icone5 = ctk.CTkImage(light_image=Image.open("images/Classement.png"), size=(50, 50))
    icone6 = ctk.CTkImage(light_image=Image.open("images/stats.png"),      size=(50, 50))
    icone7 = ctk.CTkImage(light_image=Image.open("images/pdp.png"),        size=(50, 50))

    # ── Mini photo de profil coin haut-droit ──────────────────────
    if os.path.exists(PDP_PATH):
        pdp_pil = Image.open(PDP_PATH).convert("RGBA")
        w, h = pdp_pil.size
        m = min(w, h)
        pdp_pil = pdp_pil.crop(((w-m)//2, (h-m)//2, (w+m)//2, (h+m)//2))
        pdp_pil = pdp_pil.resize((60, 60), Image.LANCZOS)
        pdp_ctk = ctk.CTkImage(light_image=pdp_pil, size=(60, 60))
        lbl_pdp = ctk.CTkLabel(app, image=pdp_ctk, text="")
        lbl_pdp.place(x=630, y=740)
        lbl_pdp.ctk_image = pdp_ctk

    # ── Handlers ──────────────────────────────────────────────────
    def go(mode):
        app.destroy()
        import jeu
        jeu.lancer(client, username, mode)

    def ouvrir_photo_profil():
        app.destroy()
        import interface_photo_de_profil
        interface_photo_de_profil.lancer(client, username)

    # ── Style commun des boutons ──────────────────────────────────
    btn_style = dict(
        font=("Melon Milk", 22, "bold"),
        text_color=BRUN_BOIS,
        fg_color=PARCHEMIN,
        hover_color=OR,
        corner_radius=0,
        border_width=0,
        compound="left",
    )

    # ── Boutons principaux — tous 300×200 ─────────────────────────
    ctk.CTkButton(app, text="Bot",
                  image=icone,  width=300, height=200,
                  command=lambda: go("bot"),        **btn_style).place(x=30,  y=50)

    ctk.CTkButton(app, text="1 vs 1",
                  image=icone2, width=300, height=200,
                  command=lambda: go("1v1"),        **btn_style).place(x=355, y=50)

    ctk.CTkButton(app, text="Tournoi",
                  image=icone3, width=300, height=200,
                  command=lambda: go("tournament"), **btn_style).place(x=680, y=50)

    # ── Boutons secondaires ───────────────────────────────────────
    ctk.CTkButton(app, text="Amis",            image=icone4, width=300, height=75,
                  **btn_style).place(x=30, y=400)
    ctk.CTkButton(app, text="Classement",      image=icone5, width=300, height=75,
                  **btn_style).place(x=30, y=500)
    ctk.CTkButton(app, text="Statistiques",    image=icone6, width=300, height=75,
                  **btn_style).place(x=30, y=600)
    ctk.CTkButton(app, text="Photo de profil", image=icone7, width=300, height=75,
                  command=ouvrir_photo_profil,  **btn_style).place(x=30, y=700)

    # ── Pseudo affiché ────────────────────────────────────────────
    ctk.CTkLabel(app, text=f"Connecté : {username}",
                 font=("Arial", 14, "bold"),
                 text_color="#FFFFFF", fg_color="transparent").place(x=700, y=760)

    app.mainloop()