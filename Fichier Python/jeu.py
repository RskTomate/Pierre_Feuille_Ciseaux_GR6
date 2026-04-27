"""
jeu.py — Fenêtre de jeu Pierre-Feuille-Ciseaux (bot / 1v1 / tournoi).
Appelé depuis interface_principale.py via lancer(client, username, mode).
  mode : "bot" | "1v1" | "tournament"
"""
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import subprocess
import sys


# ── Constantes ────────────────────────────────────────────────────────────
CHOIX_NOM  = {1: "Pierre", 2: "Feuille", 3: "Ciseaux", 4: "—"}
CHOIX_IMG  = {
    1: "images/pierre.png",
    2: "images/feuille.png",
    3: "images/ciseaux.png",
    4: "images/Croix_rouge.png",
}

# ─────────────────────────────────────────────────────────────────────────
def lancer(client, username, mode="bot"):
    """Point d'entrée. mode ∈ {'bot','1v1','tournament'}"""

    # ── Fenêtre ────────────────────────────────────────────────────────────
    app = ctk.CTk()
    app.title("Pierre Feuille Ciseaux")
    app.geometry("1000x800")

    fond_raw = Image.open("images/Arène.png").resize((1000, 800))
    fond_tk  = ImageTk.PhotoImage(fond_raw)

    canvas = tk.Canvas(app, width=1000, height=800, highlightthickness=0, bd=0)
    canvas.place(x=0, y=0)
    canvas.create_image(0, 0, anchor="nw", image=fond_tk)

    # ── État local ─────────────────────────────────────────────────────────
    state = {
        "game_id":    None,
        "opponent":   "BOT" if mode == "bot" else "...",
        "score_me":   0,
        "score_opp":  0,
        "lock":       False,      # plus de clic pendant résolution
        "timer_id":   None,
        "seconds":    10,
        "barre":      None,
        # tournoi
        "tournament_bracket": None,
        "tournament_phase":   None,   # 'semi' | 'final'
    }

    # ── Helpers texte ──────────────────────────────────────────────────────
    def texte_contour(x, y, texte, font, fill, contour="black", ep=2, tag=None):
        for dx in range(-ep, ep+1):
            for dy in range(-ep, ep+1):
                if dx or dy:
                    canvas.create_text(x+dx, y+dy, text=texte, font=font,
                                       fill=contour, tags=tag)
        canvas.create_text(x, y, text=texte, font=font, fill=fill, tags=tag)

    # ── En-têtes fixes ─────────────────────────────────────────────────────
    texte_contour(280, 80, "Pierre",  ("Lemon Milk", 50, "bold"), "grey")
    texte_contour(500, 80, "Feuille", ("Lemon Milk", 50, "bold"), "white")
    texte_contour(750, 80, "Ciseaux", ("Lemon Milk", 50, "bold"), "lightblue")

    # ── Noms joueurs ───────────────────────────────────────────────────────
    id_nom_moi  = canvas.create_text(200,  250, text=username,
                                     font=("Lemon Milk", 30, "bold"), fill="red")
    id_nom_opp  = canvas.create_text(800,  250, text=state["opponent"],
                                     font=("Lemon Milk", 30, "bold"), fill="blue")
    id_score    = canvas.create_text(500,  160, text="0 : 0",
                                     font=("Lemon Milk", 50, "bold"), fill="black")
    id_statut   = canvas.create_text(500,  420, text="",
                                     font=("Lemon Milk", 22, "bold"), fill="white")
    id_timer    = None   # créé après game_start
    id_img_moi  = None
    id_img_opp  = None
    id_img_opp_ph = None   # point d'interrogation

    # Garde les refs PhotoImage pour éviter le GC
    _photos = {}

    # ── Barre de progression ───────────────────────────────────────────────
    barre_widget = ctk.CTkProgressBar(app, width=600, height=10,
                                       progress_color="green",
                                       corner_radius=0, fg_color="red")
    barre_window = None   # canvas.create_window id

    # ── Boutons de choix ───────────────────────────────────────────────────
    btn_windows = []   # ids canvas pour les masquer / afficher

    def charger_img(path, size=(80, 80)):
        img = Image.open(path).convert("RGBA").resize(size)
        return ImageTk.PhotoImage(img)

    def afficher_boutons():
        for bw in btn_windows:
            canvas.itemconfigure(bw, state="normal")

    def masquer_boutons():
        for bw in btn_windows:
            canvas.itemconfigure(bw, state="hidden")

    def on_choix(c):
        if state["lock"] or state["game_id"] is None:
            return
        state["lock"] = True
        masquer_boutons()
        # Afficher notre image
        nonlocal id_img_moi
        ph = charger_img(CHOIX_IMG[c], (120, 100))
        _photos["moi"] = ph
        if id_img_moi:
            canvas.delete(id_img_moi)
        id_img_moi = canvas.create_image(360, 360, anchor="center", image=ph)
        # Envoyer au serveur
        client.action(c)
        canvas.itemconfig(id_statut, text="En attente de l'adversaire…")

    # Créer les 3 boutons
    for i, (nom, c) in enumerate([("pierre", 1), ("feuille", 2), ("ciseaux", 3)]):
        ph = ctk.CTkImage(light_image=Image.open(f"images/{nom}.png"), size=(80, 80))
        _photos[f"btn_{nom}"] = ph
        btn = ctk.CTkButton(app, image=ph, text="", width=120, height=100,
                            fg_color="#0f3460", hover_color="#1a4a80",
                            corner_radius=0,
                            command=lambda ch=c: on_choix(ch))
        bw = canvas.create_window(310 + i * 190, 660, anchor="center", window=btn,
                                  state="hidden")
        btn_windows.append(bw)

    # ── Timer ──────────────────────────────────────────────────────────────
    def stopper_timer():
        if state["timer_id"]:
            app.after_cancel(state["timer_id"])
            state["timer_id"] = None

    def tick_timer(cpt=10, b=1.0):
        nonlocal id_timer
        if id_timer is None:
            return
        canvas.itemconfig(id_timer, text=f"{cpt} s")
        if state["barre"]:
            state["barre"].set(b)
        if cpt > 0:
            state["timer_id"] = app.after(1000, tick_timer, cpt - 1, round(b - 0.1, 1))
        else:
            # Timeout : si on n'a pas encore joué, envoyer choix invalide (4)
            if not state["lock"]:
                state["lock"] = True
                masquer_boutons()
                client.action(4)   # le serveur traitera 4 comme "n'a pas joué"
                canvas.itemconfig(id_statut, text="Temps écoulé !")

    # ── Afficher le VS et lancer la manche ─────────────────────────────────
    def init_manche():
        nonlocal id_timer, id_img_moi, id_img_opp, id_img_opp_ph, barre_window
        state["lock"] = False

        # Nettoyer images précédentes
        for iid in [id_img_moi, id_img_opp, id_img_opp_ph]:
            if iid:
                canvas.delete(iid)
        id_img_moi = id_img_opp = None

        # Point d'interrogation adversaire
        ph = charger_img("images/point_interrogation.png", (120, 100))
        _photos["opp_ph"] = ph
        id_img_opp_ph = canvas.create_image(640, 360, anchor="center", image=ph)

        canvas.itemconfig(id_statut, text="")
        afficher_boutons()

        # Timer
        if id_timer is None:
            id_timer = canvas.create_text(500, 500, text="10 s",
                                          font=("Lemon Milk", 25, "bold"), fill="black")
        else:
            canvas.itemconfig(id_timer, text="10 s")

        # Barre
        if state["barre"] is None:
            state["barre"] = ctk.CTkProgressBar(app, width=600, height=10,
                                                  progress_color="green",
                                                  corner_radius=0, fg_color="red")
            state["barre"].set(1.0)
            barre_window = canvas.create_window(500, 530, anchor="center",
                                                window=state["barre"])
        else:
            state["barre"].set(1.0)

        stopper_timer()
        tick_timer(10, 1.0)

    # ── Gestion des messages serveur ───────────────────────────────────────
    def on_message(msg):
        nonlocal id_img_moi, id_img_opp, id_img_opp_ph

        def update():
            nonlocal id_img_moi, id_img_opp, id_img_opp_ph
            t = msg.get("type", "")

            # ── Partie trouvée ─────────────────────────────────────────────
            if t == "game_start":
                state["game_id"] = msg["game_id"]
                players = msg["players"]
                opp = next((p for p in players if p != username), "BOT")
                state["opponent"] = opp
                canvas.itemconfig(id_nom_opp, text=opp)
                # Afficher VS
                texte_contour(500, 360, "VS", ("Lemon Milk", 60, "bold"), "gold", tag="vs")
                init_manche()

            # ── Résultat d'une manche ──────────────────────────────────────
            elif t == "round_result":
                stopper_timer()
                players = list(msg["scores"].keys())
                opp = next((p for p in players if p != username), "BOT")

                c_me  = msg["choice_p1"] if players[0] == username else msg["choice_p2"]
                c_opp = msg["choice_p2"] if players[0] == username else msg["choice_p1"]

                # Images
                ph_me = charger_img(CHOIX_IMG.get(c_me,  CHOIX_IMG[4]), (120, 100))
                ph_op = charger_img(CHOIX_IMG.get(c_opp, CHOIX_IMG[4]), (120, 100))
                _photos["me_res"]  = ph_me
                _photos["opp_res"] = ph_op

                if id_img_moi:    canvas.delete(id_img_moi)
                if id_img_opp_ph: canvas.delete(id_img_opp_ph)
                if id_img_opp:    canvas.delete(id_img_opp)
                id_img_moi = canvas.create_image(360, 360, anchor="center", image=ph_me)
                id_img_opp = canvas.create_image(640, 360, anchor="center", image=ph_op)

                s_me  = msg["scores"].get(username, 0)
                s_opp = msg["scores"].get(opp, 0)
                state["score_me"]  = s_me
                state["score_opp"] = s_opp
                canvas.itemconfig(id_score, text=f"{s_me} : {s_opp}")

                wr = msg.get("winner_round")
                if wr is None:
                    canvas.itemconfig(id_statut, text="Égalité !", fill="grey")
                elif wr == username:
                    canvas.itemconfig(id_statut, text="Tu gagnes cette manche !", fill="green")
                else:
                    canvas.itemconfig(id_statut, text="L'adversaire gagne cette manche.", fill="red")

            # ── Fin de partie ──────────────────────────────────────────────
            elif t == "game_over":
                stopper_timer()
                masquer_boutons()
                state["game_id"] = None
                winner = msg.get("winner")
                if winner == username:
                    canvas.itemconfig(id_statut, text="🏆 Partie gagnée !", fill="green")
                elif winner is None:
                    canvas.itemconfig(id_statut, text="Partie annulée.", fill="orange")
                else:
                    canvas.itemconfig(id_statut, text="Partie perdue.", fill="red")
                client.ack_game_over()
                app.after(3000, retour_menu)

            # ── Messages d'attente ─────────────────────────────────────────
            elif t == "info":
                canvas.itemconfig(id_statut, text=msg.get("msg", ""), fill="white")

            elif t == "error":
                canvas.itemconfig(id_statut, text=msg.get("msg", ""), fill="red")

            # ── Tournoi ────────────────────────────────────────────────────
            elif t == "tournament_start":
                state["tournament_phase"] = "semi"
                bracket = msg.get("bracket", {})
                state["tournament_bracket"] = bracket
                texte = (f"Tournoi — Demi-finales\n"
                         f"{bracket.get('semi1',['?','?'])[0]} vs {bracket.get('semi1',['?','?'])[1]}\n"
                         f"{bracket.get('semi2',['?','?'])[0]} vs {bracket.get('semi2',['?','?'])[1]}")
                canvas.itemconfig(id_statut, text=texte, fill="gold")

            elif t == "tournament_final":
                state["tournament_phase"] = "final"
                players = msg.get("players", [])
                canvas.itemconfig(id_statut,
                                  text=f"FINALE ! {players[0]} vs {players[1]}",
                                  fill="gold")

            elif t == "tournament_over":
                w = msg.get("winner", "?")
                if w == username:
                    canvas.itemconfig(id_statut, text="🏆 Tu remportes le tournoi !", fill="gold")
                else:
                    canvas.itemconfig(id_statut, text=f"{w} remporte le tournoi.", fill="red")
                app.after(4000, retour_menu)

        app.after(0, update)

    client.set_on_message(on_message)

    # ── Retour menu ────────────────────────────────────────────────────────
    def retour_menu():
        app.destroy()
        import interface_principale
        interface_principale.lancer(client, username)

    # ── Lancer la connexion selon le mode ──────────────────────────────────
    canvas.itemconfig(id_statut, text="Connexion au serveur…", fill="white")

    if mode == "bot":
        client.play_bot()
    elif mode == "1v1":
        client.play_1v1()
        canvas.itemconfig(id_statut, text="En attente d'un adversaire…", fill="white")
    elif mode == "tournament":
        client.play_tournament()
        canvas.itemconfig(id_statut, text="En attente de 3 autres joueurs…", fill="white")

    app.mainloop()