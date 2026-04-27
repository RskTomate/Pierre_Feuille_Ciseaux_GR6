"""
jeu.py — Écran de jeu Pierre Feuille Ciseaux.
Appelé via lancer(client, username, mode) depuis interface_principale.
Modes : "bot", "1v1", "tournament"

Synchronisation complète en 1v1 :
  - opponent_found  → affiche le nom de l'adversaire, attend que les deux cliquent Prêt
  - READY           → envoyé au serveur quand le joueur clique Prêt
  - opponent_ready  → l'adversaire a cliqué Prêt (info visuelle)
  - round_start     → les deux sont prêts, on lance le timer
  - round_result    → résultat de la manche venant du serveur
  - next_round      → nouvelle manche, re-cliquer Prêt
  - game_over       → fin de la partie
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

    is_bot = (mode == "bot")

    s = dict(
        game_id=None,
        adversaire_nom=None,
        pret_j1=False,
        pret_j2=False,
        btn_pret_j1=None,
        btn_pret_j2_rect=None,
        btn_pret_j2_txt=None,
        j1_a_pick=False,
        fin_manche=False,
        lock=False,
        pick_j1=0,
        pick_j2=0,
        score_j1=0,
        score_j2=0,
        chxj1=None,
        chxj2=None,
        point_interrogation=None,
        Resultat=None,
        t_item=None,
        barre=None,
        score_item=None,
        waiting_item=None,
        nom_j2_item=None,
        adv_pret_item=None,
        vs_item=None,
        boutons_pfc_crees=False,
    )

    ctk.set_appearance_mode("light")
    app = ctk.CTk()
    app.title("Pierre Feuille Ciseaux")
    app.geometry("1000x800")

    fond_pil = Image.open("images/Arène.png").resize((1000, 800))
    fond_tk  = ImageTk.PhotoImage(fond_pil)
    app._fond_tk = fond_tk

    canvas = tk.Canvas(app, width=1000, height=800, highlightthickness=0, bd=0)
    canvas.place(x=0, y=0)
    canvas.create_image(0, 0, anchor="nw", image=fond_tk)

    def texte_contour(x, y, texte, font, fill, contour="black", ep=2):
        for dx in range(-ep, ep+1):
            for dy in range(-ep, ep+1):
                if dx or dy:
                    canvas.create_text(x+dx, y+dy, text=texte, font=font, fill=contour)
        return canvas.create_text(x, y, text=texte, font=font, fill=fill)

    texte_contour(280, 80,  "Pierre",  ("Lemon Milk", 50, "bold"), "grey")
    texte_contour(500, 80,  "Feuille", ("Lemon Milk", 50, "bold"), "white")
    texte_contour(750, 80,  "Ciseaux", ("Lemon Milk", 50, "bold"), "lightblue")

    s["score_item"] = canvas.create_text(500, 160, text="0 : 0",
                                          font=("Lemon Milk", 50, "bold"), fill="Black")

    texte_contour(200, 250, username, ("Lemon Milk", 30, "bold"), "red")
    s["nom_j2_item"] = texte_contour(800, 250,
                                      ROBOT_NOM if is_bot else "Recherche…",
                                      ("Lemon Milk", 30, "bold"), "blue")

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

    if not is_bot:
        s["waiting_item"] = canvas.create_text(
            500, 560, text="Recherche d'un adversaire…",
            font=("Lemon Milk", 24, "bold"), fill="white"
        )

    s["btn_pret_j2_rect"] = canvas.create_rectangle(725, 439, 875, 491, fill="red", outline="")
    s["btn_pret_j2_txt"]  = canvas.create_text(800, 465, text="Pret",
                                                 font=("Lemon Milk", 30, "bold"), fill="black")

    def _creer_btn_pret_j1(command):
        btn = ctk.CTkButton(
            app, text="Pret",
            font=("Lemon Milk", 40, "bold"), text_color="black",
            width=150, height=50,
            fg_color="red", hover_color="#ff4f4f",
            corner_radius=0,
            command=command
        )
        canvas.create_window(200, 465, anchor="center", window=btn)
        return btn

    # ── Callback : clic Prêt (mode réseau) ───────────────────────
    def on_clic_pret_reseau():
        if s["pret_j1"]:
            return
        s["pret_j1"] = True
        if s["btn_pret_j1"] and s["btn_pret_j1"].winfo_exists():
            s["btn_pret_j1"].configure(fg_color="green", state="disabled")
        if s["game_id"]:
            client.send({"cmd": "READY", "game_id": s["game_id"]})

    # ── Callback : clic Prêt (mode bot) ──────────────────────────
    def on_clic_pret_bot():
        if s["pret_j1"]:
            return
        s["pret_j1"] = True
        if s["btn_pret_j1"] and s["btn_pret_j1"].winfo_exists():
            s["btn_pret_j1"].configure(fg_color="green", state="disabled")
        if s["pret_j2"]:
            _demarrer_partie_bot()

    # ── Callback réseau ───────────────────────────────────────────
    def on_server_message(msg):
        t = msg.get("type", "")
        if t == "opponent_found":
            app.after(0, lambda: _on_opponent_found(msg))
        elif t == "opponent_ready":
            app.after(0, _on_opponent_ready)
        elif t == "round_start":
            app.after(0, _on_round_start)
        elif t == "round_result":
            app.after(0, lambda: _on_round_result(msg))
        elif t == "next_round":
            app.after(0, lambda: _on_next_round(msg))
        elif t == "game_over":
            app.after(0, lambda: _on_game_over(msg))
        elif t == "game_start":
            app.after(0, lambda: _on_game_start_bot(msg))

    client.set_on_message(on_server_message)

    def _on_opponent_found(msg):
        s["game_id"] = msg["game_id"]
        adv = msg.get("adversaire", "?")
        s["adversaire_nom"] = adv
        if s["waiting_item"]:
            canvas.delete(s["waiting_item"])
            s["waiting_item"] = None
        canvas.delete(s["nom_j2_item"])
        s["nom_j2_item"] = texte_contour(800, 250, adv, ("Lemon Milk", 30, "bold"), "blue")
        canvas.itemconfig(s["btn_pret_j2_rect"], fill="red")
        canvas.itemconfig(s["btn_pret_j2_txt"],  text="Pret")

    def _on_opponent_ready():
        s["pret_j2"] = True
        canvas.itemconfig(s["btn_pret_j2_rect"], fill="green")
        if s["adv_pret_item"]:
            canvas.delete(s["adv_pret_item"])
        s["adv_pret_item"] = canvas.create_text(
            800, 510, text="✔ Prêt !",
            font=("Lemon Milk", 18, "bold"), fill="green"
        )

    def _on_round_start():
        if s["btn_pret_j1"] and s["btn_pret_j1"].winfo_exists():
            s["btn_pret_j1"].destroy()
            s["btn_pret_j1"] = None
        canvas.delete(s["btn_pret_j2_rect"])
        canvas.delete(s["btn_pret_j2_txt"])
        if s["adv_pret_item"]:
            canvas.delete(s["adv_pret_item"])
            s["adv_pret_item"] = None
        _afficher_vs_et_boutons_pfc()
        Init_Manche()
        Temps_reseau()

    def _on_game_start_bot(msg):
        s["game_id"] = msg["game_id"]
        s["pret_j2"] = True
        canvas.itemconfig(s["btn_pret_j2_rect"], fill="green")
        if s["pret_j1"]:
            _demarrer_partie_bot()

    def _on_round_result(msg):
        scores  = msg.get("scores", {})
        keys    = list(scores.keys())
        is_j1   = (len(keys) >= 1 and keys[0] == username)
        c1_srv  = msg.get("choice_p1", 4)
        c2_srv  = msg.get("choice_p2", 4)
        c_advers = c2_srv if is_j1 else c1_srv

        sc_nous = scores.get(username, s["score_j1"])
        sc_adv  = scores.get(s["adversaire_nom"], s["score_j2"])

        s["lock"] = True
        _afficher_choix_j2(c_advers)

        s["score_j1"] = sc_nous
        s["score_j2"] = sc_adv
        canvas.delete(s["score_item"])
        s["score_item"] = canvas.create_text(500, 160,
            text=f"{sc_nous} : {sc_adv}",
            font=("Lemon Milk", 50, "bold"), fill="Black")

        winner_round = msg.get("winner_round")
        if s["Resultat"]:
            canvas.delete(s["Resultat"])
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

    def _on_next_round(msg):
        app.after(3000, _preparer_nouvelle_manche)

    def _preparer_nouvelle_manche():
        if s["Resultat"]:
            canvas.delete(s["Resultat"])
            s["Resultat"] = None
        for key in ("chxj1", "chxj2", "point_interrogation"):
            if s[key]:
                canvas.delete(s[key])
                s[key] = None
        s["pret_j1"] = False
        s["pret_j2"] = False
        s["j1_a_pick"] = False
        s["fin_manche"] = False
        s["lock"] = False
        s["boutons_pfc_crees"] = False
        if s["adv_pret_item"]:
            canvas.delete(s["adv_pret_item"])
            s["adv_pret_item"] = None
        # Remettre les boutons Prêt
        s["btn_pret_j2_rect"] = canvas.create_rectangle(725, 439, 875, 491, fill="red", outline="")
        s["btn_pret_j2_txt"]  = canvas.create_text(800, 465, text="Pret",
                                                     font=("Lemon Milk", 30, "bold"), fill="black")
        s["btn_pret_j1"] = _creer_btn_pret_j1(on_clic_pret_reseau)

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

    def _afficher_vs_et_boutons_pfc():
        if s["boutons_pfc_crees"]:
            return
        s["boutons_pfc_crees"] = True
        if s["vs_item"]:
            canvas.delete(s["vs_item"])
        s["vs_item"] = texte_contour(500, 360, "VS", ("Lemon Milk", 60, "bold"), "gold")

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

        s["t_item"] = canvas.create_text(500, 500, text="10 s",
                                          font=("Lemon Milk", 25, "bold"), fill="black")
        s["barre"] = ctk.CTkProgressBar(app, width=600, height=10,
                                         progress_color="green", corner_radius=0, fg_color="red")
        s["barre"].set(1.0)
        canvas.create_window(500, 530, anchor="center", window=s["barre"])

    def _demarrer_partie_bot():
        if s["btn_pret_j1"] and s["btn_pret_j1"].winfo_exists():
            s["btn_pret_j1"].destroy()
            s["btn_pret_j1"] = None
        canvas.delete(s["btn_pret_j2_rect"])
        canvas.delete(s["btn_pret_j2_txt"])
        _afficher_vs_et_boutons_pfc()
        Lancer_jeu_bot()

    def Choix(x):
        if not s["lock"] and s["boutons_pfc_crees"]:
            noms = {1: "images/pierre.png", 2: "images/Feuille.png", 3: "images/Ciseaux.png"}
            try:
                img = Image.open(noms[x]).convert("RGBA").resize((120, 100))
            except Exception:
                return
            tk_img = ImageTk.PhotoImage(img)
            canvas.j1_img = tk_img
            if s["chxj1"]:
                canvas.delete(s["chxj1"])
            s["chxj1"] = canvas.create_image(360, 360, anchor="center", image=tk_img)
            s["pick_j1"] = x
            s["j1_a_pick"] = True
            if not is_bot and s["game_id"]:
                client.action(x)

    def _afficher_choix_j2(x):
        if x not in (1, 2, 3):
            return
        noms = {1: "images/pierre.png", 2: "images/Feuille.png", 3: "images/Ciseaux.png"}
        try:
            img = Image.open(noms[x]).convert("RGBA").resize((120, 100))
        except Exception:
            return
        tk_img = ImageTk.PhotoImage(img)
        canvas.j2_img = tk_img
        if s["chxj2"]:
            canvas.delete(s["chxj2"])
        s["chxj2"] = canvas.create_image(640, 360, anchor="center", image=tk_img)
        if s["point_interrogation"]:
            canvas.delete(s["point_interrogation"])

    def Init_Manche():
        s["j1_a_pick"] = False
        s["fin_manche"] = False
        s["lock"] = False
        s["pick_j2"] = randint(1, 3) if is_bot else 0
        try:
            img = Image.open("images/point_interrogation.png").convert("RGBA").resize((120, 100))
            tk_img = ImageTk.PhotoImage(img)
            canvas.j2_pi = tk_img
            s["point_interrogation"] = canvas.create_image(640, 360, anchor="center", image=tk_img)
        except Exception:
            pass
        for key in ("Resultat", "chxj1", "chxj2"):
            if s[key]:
                try:
                    canvas.delete(s[key])
                except Exception:
                    pass
                s[key] = None

    # ── Mode BOT ──────────────────────────────────────────────────
    def Lancer_jeu_bot():
        Init_Manche()
        Temps_bot()

    def Temps_bot(cpt=10, b=1.0):
        if cpt >= 0:
            if s["barre"]:
                s["barre"].set(b)
            if s["t_item"]:
                canvas.itemconfig(s["t_item"], text=f"{cpt} s")
            app.after(1000, Temps_bot, cpt-1, round(b-0.1, 1))
        if cpt == 0 and not s["j1_a_pick"]:
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
        if cpt == 0:
            s["lock"] = True
            _afficher_choix_j2(s["pick_j2"])
            FinManche_bot()

    def MiseAJourScore_bot(j):
        if j == 1:
            s["score_j1"] += 1
        else:
            s["score_j2"] += 1
        canvas.delete(s["score_item"])
        s["score_item"] = canvas.create_text(500, 160,
            text=f"{s['score_j1']} : {s['score_j2']}",
            font=("Lemon Milk", 50, "bold"), fill="Black")

    def GagneManche_bot(p1, p2):
        gagne   = (p1==1 and p2==3) or (p1==2 and p2==1) or (p1==3 and p2==2)
        perdu   = (p1==3 and p2==1) or (p1==1 and p2==2) or (p1==2 and p2==3)
        egalite = (p1 == p2 and p1 != 4)
        if p1 == 4:
            s["Resultat"] = canvas.create_text(500, 450, text="L'adversaire Gagne",
                                                font=("Lemon Milk", 30, "bold"), fill="red")
            MiseAJourScore_bot(2)
        elif p2 == 4 or gagne:
            s["Resultat"] = canvas.create_text(500, 450, text="Vous Gagnez",
                                                font=("Lemon Milk", 30, "bold"), fill="green")
            MiseAJourScore_bot(1)
        elif perdu:
            s["Resultat"] = canvas.create_text(500, 450, text="L'adversaire Gagne",
                                                font=("Lemon Milk", 30, "bold"), fill="red")
            MiseAJourScore_bot(2)
        elif egalite:
            s["Resultat"] = canvas.create_text(500, 450, text="Égalité",
                                                font=("Lemon Milk", 30, "bold"), fill="grey")
        s["fin_manche"] = True

    def FinManche_bot():
        GagneManche_bot(s["pick_j1"], s["pick_j2"])
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
            app.after(3000, Lancer_jeu_bot)

    # ── Mode RÉSEAU ───────────────────────────────────────────────
    def Temps_reseau(cpt=10, b=1.0):
        if s["fin_manche"]:
            return
        if cpt >= 0:
            if s["barre"]:
                s["barre"].set(b)
            if s["t_item"]:
                canvas.itemconfig(s["t_item"], text=f"{cpt} s")
            app.after(1000, Temps_reseau, cpt-1, round(b-0.1, 1))
        if cpt == 0 and not s["j1_a_pick"]:
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
        if cpt == 0:
            s["lock"] = True

    def FinJeu():
        app.destroy()
        import interface_principale
        interface_principale.lancer(client, username)

    def anim_recherche(points=1):
        if s["waiting_item"]:
            try:
                canvas.itemconfig(s["waiting_item"],
                                  text=f"Recherche d'un adversaire{'.' * points}")
                app.after(500, anim_recherche, (points % 3) + 1)
            except Exception:
                pass

    # ── Démarrage ─────────────────────────────────────────────────
    if is_bot:
        s["btn_pret_j1"] = _creer_btn_pret_j1(on_clic_pret_bot)
        client.play_bot()
        # Le serveur répondra game_start → _on_game_start_bot → toggle J2 vert
    else:
        s["btn_pret_j1"] = _creer_btn_pret_j1(on_clic_pret_reseau)
        # Cacher les boutons Prêt jusqu'à ce qu'un adversaire soit trouvé
        canvas.itemconfig(s["btn_pret_j2_rect"], state="hidden")
        canvas.itemconfig(s["btn_pret_j2_txt"],  state="hidden")
        s["btn_pret_j1"].configure(state="disabled")
        anim_recherche()
        client.play_1v1()

    app.mainloop()