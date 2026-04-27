"""
jeu.py — Écran de jeu Pierre Feuille Ciseaux.
Appelé via lancer(client, username, mode) depuis interface_principale.
Modes : "bot", "1v1", "tournament"
"""
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont
from random import randint
import os

PDP_PATH  = "images/profil/photo_de_profil.png"
BOT_PATH  = "images/bot.png"
ROBOT_NOM = "ROBOT"


# ── Chargement des images PIL ─────────────────────────────────────────────

def _photo_carree(img_pil, size):
    w, h = img_pil.size
    m = min(w, h)
    img_pil = img_pil.crop(((w-m)//2, (h-m)//2, (w+m)//2, (h+m)//2))
    return img_pil.resize((size, size), Image.LANCZOS).convert("RGBA")


def _charger_pdp_joueur(size=150):
    if os.path.exists(PDP_PATH):
        img = Image.open(PDP_PATH).convert("RGBA")
    else:
        img = Image.new("RGBA", (size, size), "#C9A227")
        d = ImageDraw.Draw(img)
        d.ellipse([4, 4, size-4, size-4], fill="#D4B13B", outline="#2C1A0E", width=3)
        try:
            fnt = ImageFont.truetype("arial.ttf", 14)
        except Exception:
            fnt = ImageFont.load_default()
        bb = d.textbbox((0, 0), "Vous", font=fnt)
        d.text(((size-(bb[2]-bb[0]))//2, (size-(bb[3]-bb[1]))//2), "Vous", font=fnt, fill="#2C1A0E")
    return _photo_carree(img, size)


def _charger_pdp_robot(size=150):
    if os.path.exists(BOT_PATH):
        img = Image.open(BOT_PATH).convert("RGBA")
    else:
        img = Image.new("RGBA", (size, size), "#1E1E3C")
        d = ImageDraw.Draw(img)
        d.rectangle([8, 8, size-8, size-8], fill="#3A3A6C", outline="#8888FF", width=3)
        try:
            fnt = ImageFont.truetype("arial.ttf", 18)
        except Exception:
            fnt = ImageFont.load_default()
        bb = d.textbbox((0, 0), "BOT", font=fnt)
        d.text(((size-(bb[2]-bb[0]))//2, (size-(bb[3]-bb[1]))//2), "BOT", font=fnt, fill="#FFFFFF")
    return _photo_carree(img, size)


def _charger_pdp_adversaire(size=150):
    img = Image.new("RGBA", (size, size), "#2A4A6A")
    d = ImageDraw.Draw(img)
    d.ellipse([4, 4, size-4, size-4], fill="#3A6A9A", outline="#AADDFF", width=3)
    try:
        fnt = ImageFont.truetype("arial.ttf", 30)
    except Exception:
        fnt = ImageFont.load_default()
    bb = d.textbbox((0, 0), "?", font=fnt)
    d.text(((size-(bb[2]-bb[0]))//2, (size-(bb[3]-bb[1]))//2), "?", font=fnt, fill="#FFFFFF")
    return _photo_carree(img, size)


# ── Point d'entrée ────────────────────────────────────────────────────────

def lancer(client, username, mode="bot"):

    s = dict(
        # ── état commun ──────────────────────────────────────
        pret_j1=False, pret_j2=False,
        j1_a_pick=False, fin_manche=False, lock=False,
        pick_j1=0, pick_j2=0,
        score_j1=0, score_j2=0,
        chxj1=None, chxj2=None,
        point_interrogation=None,
        Resultat=None,
        t=None, barre=None,
        score_item=None,
        btn_Pret_J1=None,
        # ── état réseau 1v1 ──────────────────────────────────
        game_id=None,           # ID de la partie renvoyé par le serveur
        adversaire_nom=None,    # pseudo de l'adversaire (renseigné au game_start)
        en_attente=True,        # True tant que le serveur n'a pas envoyé game_start
        waiting_item=None,      # item canvas "Recherche adversaire…"
        nom_j2_item=None,       # item canvas du nom de l'adversaire (mis à jour)
    )

    # ── mode bot : J2 est le serveur, pas besoin d'attendre ───────────────
    is_bot = (mode == "bot")

    ctk.set_appearance_mode("light")
    app = ctk.CTk()
    app.title("Pierre Feuille Ciseaux")
    app.geometry("1000x800")

    # ── Canvas fond ───────────────────────────────────────────────
    fond_pil = Image.open("images/Arène.png").resize((1000, 800))
    fond_tk  = ImageTk.PhotoImage(fond_pil)
    app._fond_tk = fond_tk

    canvas = tk.Canvas(app, width=1000, height=800, highlightthickness=0, bd=0)
    canvas.place(x=0, y=0)
    canvas.create_image(0, 0, anchor="nw", image=fond_tk)

    # ── Texte avec contour ────────────────────────────────────────
    def texte_contour(x, y, texte, font, fill, contour="black", ep=2, tag=None):
        for dx in range(-ep, ep+1):
            for dy in range(-ep, ep+1):
                if dx or dy:
                    canvas.create_text(x+dx, y+dy, text=texte, font=font, fill=contour, tags=tag)
        return canvas.create_text(x, y, text=texte, font=font, fill=fill, tags=tag)

    # ── Textes fixes ──────────────────────────────────────────────
    texte_contour(280, 80, "Pierre",  ("Lemon Milk", 50, "bold"), "grey")
    texte_contour(500, 80, "Feuille", ("Lemon Milk", 50, "bold"), "white")
    texte_contour(750, 80, "Ciseaux", ("Lemon Milk", 50, "bold"), "lightblue")

    s["score_item"] = canvas.create_text(500, 160, text="0 : 0",
                                          font=("Lemon Milk", 50, "bold"), fill="Black")

    # ── Noms ──────────────────────────────────────────────────────
    texte_contour(200, 250, username, ("Lemon Milk", 30, "bold"), "red")

    nom_j2_initial = ROBOT_NOM if is_bot else "Recherche…"
    s["nom_j2_item"] = texte_contour(800, 250, nom_j2_initial, ("Lemon Milk", 30, "bold"), "blue")

    # ── Photos de profil ──────────────────────────────────────────
    pdp_j1_pil = _charger_pdp_joueur(150)
    pdp_j1_ctk = ctk.CTkImage(light_image=pdp_j1_pil, size=(150, 150))
    lbl_j1 = ctk.CTkLabel(app, image=pdp_j1_ctk, text="")
    lbl_j1.ctk_image = pdp_j1_ctk
    canvas.create_window(200, 360, anchor="center", window=lbl_j1)

    pdp_j2_pil = _charger_pdp_robot(150) if is_bot else _charger_pdp_adversaire(150)
    pdp_j2_ctk = ctk.CTkImage(light_image=pdp_j2_pil, size=(150, 150))
    lbl_j2 = ctk.CTkLabel(app, image=pdp_j2_ctk, text="")
    lbl_j2.ctk_image = pdp_j2_ctk
    canvas.create_window(800, 360, anchor="center", window=lbl_j2)

    # ── Zone "En attente" (1v1 uniquement) ───────────────────────
    if not is_bot:
        s["waiting_item"] = canvas.create_text(
            500, 360, text="Recherche d'un adversaire…",
            font=("Lemon Milk", 28, "bold"), fill="white"
        )

    # ── Bouton Prêt J2 (canvas) — utilisé en mode bot ─────────────
    btn_J2_rect = canvas.create_rectangle(725, 439, 875, 491, fill="red", outline="")
    btn_J2_txt  = canvas.create_text(800, 465, text="Pret",
                                      font=("Lemon Milk", 30, "bold"), fill="black")

    # ── Bouton Prêt J1 (via canvas.create_window) ─────────────────
    s["btn_Pret_J1"] = ctk.CTkButton(
        app, text="Pret",
        font=("Lemon Milk", 40, "bold"), text_color="black",
        width=150, height=50,
        fg_color="red", hover_color="#ff4f4f",
        corner_radius=0,
        command=lambda: toggle_pret(1)
    )
    canvas.create_window(200, 465, anchor="center", window=s["btn_Pret_J1"])

    # ── Callback réseau ───────────────────────────────────────────

    def on_server_message(msg):
        """Reçu depuis le thread réseau — utiliser app.after() pour l'UI."""
        t = msg.get("type", "")

        if t == "game_start":
            # La partie est prête : on connaît l'adversaire
            players = msg.get("players", [])
            adv = next((p for p in players if p != username), "?")
            app.after(0, lambda: _on_game_start(msg["game_id"], adv))

        elif t == "round_result":
            c2 = msg.get("choice_p2") if msg.get("players", [None])[0] == username else msg.get("choice_p1")
            # Plus robuste : on cherche le choix de l'adversaire
            players = msg.get("scores", {})  # scores est un dict {pseudo: score}
            app.after(0, lambda: _on_round_result(msg))

        elif t == "game_over":
            app.after(0, lambda: _on_game_over(msg))

        elif t == "info":
            pass  # messages informatifs (en attente…)

    def _on_game_start(game_id, adv_nom):
        s["game_id"] = game_id
        s["adversaire_nom"] = adv_nom
        s["en_attente"] = False

        # Mettre à jour le nom de l'adversaire à l'écran
        canvas.delete(s["nom_j2_item"])
        s["nom_j2_item"] = texte_contour(800, 250, adv_nom, ("Lemon Milk", 30, "bold"), "blue")

        # Supprimer le texte "Recherche…"
        if s["waiting_item"]:
            canvas.delete(s["waiting_item"])
            s["waiting_item"] = None

        # L'adversaire est prêt (côté serveur la partie est lancée)
        toggle_pret(2)

    def _on_round_result(msg):
        """Le serveur nous donne les deux choix et les scores."""
        if s["fin_manche"]:
            return  # déjà traité localement (mode bot), ignorer

        players_list  = list(msg.get("scores", {}).keys())
        # Identifier quel indice est J1 (nous) et J2
        if len(players_list) >= 2:
            p1_srv = players_list[0]
            is_j1  = (p1_srv == username)
            c1_srv = msg.get("choice_p1", 4)
            c2_srv = msg.get("choice_p2", 4)
            c_nous   = c1_srv if is_j1 else c2_srv
            c_advers = c2_srv if is_j1 else c1_srv
            sc_nous  = msg["scores"].get(username, 0)
            sc_adv   = msg["scores"].get(s["adversaire_nom"], 0)

            s["pick_j2"] = c_advers
            _afficher_choix_j2(c_advers)
            s["lock"] = True

            # Mise à jour score
            s["score_j1"] = sc_nous
            s["score_j2"] = sc_adv
            canvas.delete(s["score_item"])
            s["score_item"] = canvas.create_text(500, 160,
                text=f"{sc_nous} : {sc_adv}",
                font=("Lemon Milk", 50, "bold"), fill="Black")

            winner_round = msg.get("winner_round")
            if winner_round == username:
                s["Resultat"] = canvas.create_text(500, 450, text="Vous Gagnez",
                    font=("Lemon Milk", 30, "bold"), fill="green")
            elif winner_round is None:
                s["Resultat"] = canvas.create_text(500, 450, text="Égalité",
                    font=("Lemon Milk", 30, "bold"), fill="grey")
            else:
                s["Resultat"] = canvas.create_text(500, 450, text="L'adversaire Gagne",
                    font=("Lemon Milk", 30, "bold"), fill="red")

            s["fin_manche"] = True

            # Nouvelle manche ou fin ?
            if sc_nous >= 3 or sc_adv >= 3:
                pass  # game_over va arriver
            else:
                app.after(3000, Lancer_jeu)

    def _on_game_over(msg):
        winner = msg.get("winner")
        if s["Resultat"]:
            canvas.delete(s["Resultat"])
        if winner == username:
            canvas.create_text(500, 450, text="Partie Gagnée",
                               font=("Lemon Milk", 50, "bold"), fill="green")
        elif winner is None:
            canvas.create_text(500, 450, text="Partie abandonnée",
                               font=("Lemon Milk", 40, "bold"), fill="orange")
        else:
            canvas.create_text(500, 450, text="Partie Perdue",
                               font=("Lemon Milk", 50, "bold"), fill="red")
        client.ack_game_over()
        app.after(3000, FinJeu)

    # Brancher le callback réseau
    client.set_on_message(on_server_message)

    # ── Demander une partie au serveur ────────────────────────────
    if is_bot:
        client.play_bot()
    else:
        client.play_1v1()

    # ── Logique locale (identique à l'original pour le mode bot) ──

    def toggle_pret(numero):
        if numero == 1:
            s["pret_j1"] = not s["pret_j1"]
            if s["pret_j1"]:
                s["btn_Pret_J1"].configure(fg_color="green")
        if numero == 2:
            s["pret_j2"] = not s["pret_j2"]
            if s["pret_j2"]:
                canvas.itemconfig(btn_J2_rect, fill="green")

        if s["pret_j1"] and s["pret_j2"]:
            s["btn_Pret_J1"].destroy()
            canvas.delete(btn_J2_rect)
            canvas.delete(btn_J2_txt)

            img_pierre  = ctk.CTkImage(light_image=Image.open("images/pierre.png"),  size=(80, 80))
            img_feuille = ctk.CTkImage(light_image=Image.open("images/feuille.png"), size=(80, 80))
            img_ciseaux = ctk.CTkImage(light_image=Image.open("images/ciseaux.png"), size=(80, 80))
            app._pfc_imgs = (img_pierre, img_feuille, img_ciseaux)

            btn_kw = dict(text="", width=120, height=100,
                          fg_color="#0f3460", hover_color="#1a4a80", corner_radius=0)
            canvas.create_window(310, 660, anchor="center",
                                 window=ctk.CTkButton(app, image=img_pierre,  command=lambda: Choix(1), **btn_kw))
            canvas.create_window(500, 660, anchor="center",
                                 window=ctk.CTkButton(app, image=img_feuille, command=lambda: Choix(2), **btn_kw))
            canvas.create_window(690, 660, anchor="center",
                                 window=ctk.CTkButton(app, image=img_ciseaux, command=lambda: Choix(3), **btn_kw))

            s["t"] = canvas.create_text(500, 500, text="10 s",
                                         font=("Lemon Milk", 25, "bold"), fill="black")
            s["barre"] = ctk.CTkProgressBar(app, width=600, height=10,
                                             progress_color="green", corner_radius=0, fg_color="red")
            s["barre"].set(1.0)
            canvas.create_window(500, 530, anchor="center", window=s["barre"])

            texte_contour(500, 360, "VS", ("Lemon Milk", 60, "bold"), "gold")
            Lancer_jeu()

    def Wait(points=1):
        if not (s["pret_j1"] and s["pret_j2"]):
            if s["waiting_item"]:
                dots = "." * points
                canvas.itemconfig(s["waiting_item"], text=f"Recherche d'un adversaire{dots}")
            app.after(500, Wait, (points % 3) + 1)

    def Lancer_jeu():
        Init_Manche()
        if is_bot:
            Temps()
        else:
            Temps_reseau()

    def Choix(x):
        if s["pret_j1"] and s["pret_j2"] and not s["lock"]:
            noms = {1: "images/pierre.png", 2: "images/Feuille.png", 3: "images/Ciseaux.png"}
            img = Image.open(noms[x]).convert("RGBA").resize((120, 100))
            tk_img = ImageTk.PhotoImage(img)
            canvas.j1_img = tk_img
            if s["chxj1"]:
                canvas.delete(s["chxj1"])
            s["chxj1"] = canvas.create_image(360, 360, anchor="center", image=tk_img)
            s["pick_j1"] = x
            s["j1_a_pick"] = True

            # En mode réseau : envoyer le choix au serveur
            if not is_bot and s["game_id"]:
                client.action(x)

    def _afficher_choix_j2(x):
        if x == 4:
            return  # pas de choix
        noms = {1: "images/pierre.png", 2: "images/Feuille.png", 3: "images/Ciseaux.png"}
        img = Image.open(noms[x]).convert("RGBA").resize((120, 100))
        tk_img = ImageTk.PhotoImage(img)
        canvas.j2_img = tk_img
        if s["chxj2"]:
            canvas.delete(s["chxj2"])
        s["chxj2"] = canvas.create_image(640, 360, anchor="center", image=tk_img)
        if s["point_interrogation"]:
            canvas.delete(s["point_interrogation"])

    # ── Timer mode BOT (résolution locale) ───────────────────────
    def Temps(cpt=10, b=1.0):
        if cpt >= 0:
            s["barre"].set(b)
            canvas.itemconfig(s["t"], text=f"{cpt} s")
            app.after(1000, Temps, cpt-1, round(b-0.1, 1))
        if cpt == 0 and not s["j1_a_pick"]:
            img = Image.open("images/Croix_rouge.png").convert("RGBA").resize((120, 100))
            tk_img = ImageTk.PhotoImage(img)
            canvas.j1_img = tk_img
            if s["chxj1"]:
                canvas.delete(s["chxj1"])
            s["chxj1"] = canvas.create_image(360, 360, anchor="center", image=tk_img)
            s["j1_a_pick"] = True
            s["pick_j1"] = 4
            # Informer le serveur qu'on n'a pas joué (timeout)
            if not is_bot and s["game_id"]:
                client.action(4)  # le serveur traitera 4 comme un timeout
        if cpt == 0:
            s["lock"] = True
            _afficher_choix_j2(s["pick_j2"])
            FinManche()

    # ── Timer mode RÉSEAU (on attend la réponse du serveur) ───────
    def Temps_reseau(cpt=10, b=1.0):
        """Décompte affiché, mais la résolution vient du serveur."""
        if s["fin_manche"]:
            return  # le serveur a déjà résolu, on arrête le timer

        if cpt >= 0:
            if s["barre"]:
                s["barre"].set(b)
            if s["t"]:
                canvas.itemconfig(s["t"], text=f"{cpt} s")
            app.after(1000, Temps_reseau, cpt-1, round(b-0.1, 1))

        if cpt == 0 and not s["j1_a_pick"]:
            # Timeout : afficher croix et envoyer "pas de choix" au serveur
            try:
                img = Image.open("images/Croix_rouge.png").convert("RGBA").resize((120, 100))
                tk_img = ImageTk.PhotoImage(img)
                canvas.j1_img = tk_img
                if s["chxj1"]:
                    canvas.delete(s["chxj1"])
                s["chxj1"] = canvas.create_image(360, 360, anchor="center", image=tk_img)
            except Exception:
                pass
            s["j1_a_pick"] = True
            s["pick_j1"] = 4
            # Le serveur résoudra quand l'adversaire jouera (ou timeout côté serveur)

        if cpt == 0:
            s["lock"] = True
            # La résolution arrive via _on_round_result (callback réseau)

    def Init_Manche():
        s["j1_a_pick"] = False
        s["fin_manche"] = False
        s["lock"] = False
        s["pick_j2"] = randint(1, 3) if is_bot else 0  # en réseau, on attend le serveur
        img = Image.open("images/point_interrogation.png").convert("RGBA").resize((120, 100))
        tk_img = ImageTk.PhotoImage(img)
        canvas.j2_pi = tk_img
        s["point_interrogation"] = canvas.create_image(640, 360, anchor="center", image=tk_img)
        for key in ("Resultat", "chxj1", "chxj2"):
            if s[key]:
                try:
                    canvas.delete(s[key])
                except Exception:
                    pass
                s[key] = None

    def MiseAJourScore(j):
        if j == 1:
            s["score_j1"] += 1
        else:
            s["score_j2"] += 1
        canvas.delete(s["score_item"])
        s["score_item"] = canvas.create_text(500, 160,
            text=f"{s['score_j1']} : {s['score_j2']}",
            font=("Lemon Milk", 50, "bold"), fill="Black")

    def GagneManche(p1, p2):
        gagne   = (p1==1 and p2==3) or (p1==2 and p2==1) or (p1==3 and p2==2)
        perdu   = (p1==3 and p2==1) or (p1==1 and p2==2) or (p1==2 and p2==3)
        egalite = (p1 == p2 and p1 != 4)
        if p1 == 4:
            s["Resultat"] = canvas.create_text(500, 450, text="L'adversaire Gagne",
                                                font=("Lemon Milk", 30, "bold"), fill="red")
            MiseAJourScore(2)
        elif p2 == 4 or gagne:
            s["Resultat"] = canvas.create_text(500, 450, text="Vous Gagnez",
                                                font=("Lemon Milk", 30, "bold"), fill="green")
            MiseAJourScore(1)
        elif perdu:
            s["Resultat"] = canvas.create_text(500, 450, text="L'adversaire Gagne",
                                                font=("Lemon Milk", 30, "bold"), fill="red")
            MiseAJourScore(2)
        elif egalite:
            s["Resultat"] = canvas.create_text(500, 450, text="Égalité",
                                                font=("Lemon Milk", 30, "bold"), fill="grey")
        s["fin_manche"] = True

    def FinManche():
        """Utilisé uniquement en mode bot (résolution locale)."""
        GagneManche(s["pick_j1"], s["pick_j2"])
        if s["score_j1"] == 3:
            canvas.delete(s["Resultat"])
            canvas.create_text(500, 450, text="Partie Gagnée",
                               font=("Lemon Milk", 50, "bold"), fill="green")
            client.ack_game_over()
            app.after(3000, FinJeu)
            return
        if s["score_j2"] == 3:
            canvas.delete(s["Resultat"])
            canvas.create_text(500, 450, text="Partie Perdue",
                               font=("Lemon Milk", 50, "bold"), fill="red")
            client.ack_game_over()
            app.after(3000, FinJeu)
            return
        if s["fin_manche"]:
            app.after(3000, Lancer_jeu)

    def FinJeu():
        app.destroy()
        import interface_principale
        interface_principale.lancer(client, username)

    # ── Démarrage ─────────────────────────────────────────────────
    if is_bot:
        # Mode bot : J2 prêt immédiatement, J1 clique sur "Pret"
        toggle_pret(2)
    else:
        # Mode réseau : on attend game_start du serveur avant toggle_pret(2)
        Wait()

    app.mainloop()