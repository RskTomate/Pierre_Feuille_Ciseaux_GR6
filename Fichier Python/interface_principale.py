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

    def ouvrir_classement():
        """Fenêtre classement — demande GET_LEADERBOARD au serveur."""
        win = ctk.CTkToplevel(app)
        win.title("Classement")
        win.geometry("420x520")
        win.configure(fg_color="#7B8B8E")
        win.grab_set()

        ctk.CTkLabel(win, text="🏆 Classement", font=("Arial", 22, "bold"),
                     text_color=PARCHEMIN, fg_color="transparent").pack(pady=16)

        frame = ctk.CTkScrollableFrame(win, width=380, height=380, fg_color="#4a5a5e")
        frame.pack(padx=10, pady=4)

        lbl_attente = ctk.CTkLabel(frame, text="Chargement…", font=("Arial", 14),
                                   text_color="#FFFFFF", fg_color="transparent")
        lbl_attente.pack(pady=20)

        def afficher_leaderboard(data):
            lbl_attente.destroy()
            # En-tête
            header = ctk.CTkFrame(frame, fg_color="#2a3a3e", corner_radius=6)
            header.pack(fill="x", padx=4, pady=2)
            ctk.CTkLabel(header, text="#",        width=40,  font=("Arial", 13, "bold"), text_color=PARCHEMIN).grid(row=0, column=0, padx=4)
            ctk.CTkLabel(header, text="Pseudo",   width=180, font=("Arial", 13, "bold"), text_color=PARCHEMIN).grid(row=0, column=1, padx=4)
            ctk.CTkLabel(header, text="Victoires",width=90,  font=("Arial", 13, "bold"), text_color=PARCHEMIN).grid(row=0, column=2, padx=4)
            
            medailles = ["1", "2", "3"]
            for i, entry in enumerate(data):
                bg = "#1a2a2e" if i % 2 == 0 else "#263036"
                row_frame = ctk.CTkFrame(frame, fg_color=bg, corner_radius=4)
                row_frame.pack(fill="x", padx=4, pady=1)
                rang = medailles[i] if i < 3 else str(i + 1)
                tc = "#FFD700" if i == 0 else "#C0C0C0" if i == 1 else "#CD7F32" if i == 2 else "#FFFFFF"
                ctk.CTkLabel(row_frame, text=rang,                 width=40,  font=("Arial", 13), text_color=tc).grid(row=0, column=0, padx=4, pady=3)
                ctk.CTkLabel(row_frame, text=entry["username"],    width=180, font=("Arial", 13), text_color="#FFFFFF").grid(row=0, column=1, padx=4)
                ctk.CTkLabel(row_frame, text=str(entry["wins"]),   width=90,  font=("Arial", 13, "bold"), text_color="#4CAF50").grid(row=0, column=2, padx=4)

        def on_msg_lb(msg):
            if msg.get("type") == "leaderboard":
                win.after(0, lambda: afficher_leaderboard(msg.get("data", [])))
                client.set_on_message(None)  # libérer le callback temporaire

        client.set_on_message(on_msg_lb)
        client.send({"cmd": "GET_LEADERBOARD"})

    def ouvrir_statistiques():
        """Fenêtre statistiques — demande GET_STATS au serveur."""
        win = ctk.CTkToplevel(app)
        win.title("Statistiques")
        win.geometry("360x300")
        win.configure(fg_color="#7B8B8E")
        win.grab_set()

        ctk.CTkLabel(win, text="📊 Mes Statistiques", font=("Arial", 22, "bold"),
                     text_color=PARCHEMIN, fg_color="transparent").pack(pady=20)

        frame = ctk.CTkFrame(win, fg_color="#4a5a5e", corner_radius=10)
        frame.pack(padx=24, pady=8, fill="x")

        lbl_attente = ctk.CTkLabel(frame, text="Chargement…", font=("Arial", 14),
                                   text_color="#FFFFFF", fg_color="transparent")
        lbl_attente.pack(pady=20)

        def afficher_stats(wins, losses):
            lbl_attente.destroy()
            total = wins + losses
            ratio = f"{wins/total*100:.0f}%" if total > 0 else "—"
            for label, valeur, couleur in [
                ("Victoires 🏆", str(wins),  "#4CAF50"),
                ("Défaites  💀", str(losses), "#F44336"),
                ("Parties jouées", str(total), "#FFFFFF"),
                ("Taux de victoire", ratio,    PARCHEMIN),
            ]:
                row = ctk.CTkFrame(frame, fg_color="transparent")
                row.pack(fill="x", padx=16, pady=6)
                ctk.CTkLabel(row, text=label, font=("Arial", 15), text_color="#CCCCCC",
                             fg_color="transparent").pack(side="left")
                ctk.CTkLabel(row, text=valeur, font=("Arial", 15, "bold"),
                             text_color=couleur, fg_color="transparent").pack(side="right")

        def on_msg_stats(msg):
            if msg.get("type") == "stats":
                wins   = msg.get("wins", 0)
                losses = msg.get("losses", 0)
                win.after(0, lambda: afficher_stats(wins, losses))
                client.set_on_message(None)

        client.set_on_message(on_msg_stats)
        client.send({"cmd": "GET_STATS"})

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

    # ── Boutons secondaires ───────────────────────────────────────
    ctk.CTkButton(app, text="Classement",      image=icone5, width=300, height=75,
                  command=ouvrir_classement,   **btn_style).place(x=30, y=500)
    ctk.CTkButton(app, text="Statistiques",    image=icone6, width=300, height=75,
                  command=ouvrir_statistiques, **btn_style).place(x=30, y=600)
    ctk.CTkButton(app, text="Photo de profil", image=icone7, width=300, height=75,
                  command=ouvrir_photo_profil,  **btn_style).place(x=30, y=700)

    # ── Pseudo affiché ────────────────────────────────────────────
    ctk.CTkLabel(app, text=f"Connecté : {username}",
                 font=("Arial", 14, "bold"),
                 text_color="#FFFFFF", fg_color="transparent").place(x=700, y=760)

    app.mainloop()