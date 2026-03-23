import customtkinter as ctk

# ── Paramètres de la fenêtre ───────────────────────────────────────────────
app = ctk.CTk()
app.title("Pierre Feuille Ciseaux")
app.geometry("400x500")
app.configure(fg_color="dark grey")  # couleur de fond

# ── Titre principal ────────────────────────────────────────────────────────
titre = ctk.CTkLabel(
    app,
    text="Créer un compte",
    font=("Courier", 35, "bold"),
    text_color="black"
)
titre.place(x=40, y=50)

# ── Pseudo joueur ───────────────────────────────────────────────
pseudo_joueur = ctk.CTkLabel(
    app,
    text="Pseudo",
    font=("Courier", 30, "bold"),
    text_color="black"
)
pseudo_joueur.place(x=40, y=130)

# ── Zone de texte pour pseudo ─────────────────────────────────────────

textbox = ctk.CTkTextbox(app, width=150, height=10, fg_color = "white")
textbox.place(x=40, y=170)  # Position exacte en pixels

# ── Mot de passe joueur ───────────────────────────────────────────────

mdp_joueur = ctk.CTkLabel(
    app,
    text="Mot de passe",
    font=("Courier", 30, "bold"),
    text_color="black"
)
mdp_joueur.place(x=40, y=220)

# ── Zone de texte pour mdp ─────────────────────────────────────────

textbox = ctk.CTkTextbox(app, width=300, height=10, fg_color = "white")
textbox.place(x=40, y=260)  # Position exacte en pixels


# ── Valider mot de passe joueur ───────────────────────────────────────────────

mdp_joueur = ctk.CTkLabel(
    app,
    text="Valider mot de passe",
    font=("Courier", 30, "bold"),
    text_color="black"
)
mdp_joueur.place(x=40, y=310)

# ── Zone de texte pour valider mdp ─────────────────────────────────────────

textbox = ctk.CTkTextbox(app, width=300, height=10, fg_color = "white")
textbox.place(x=40, y=350)  # Position exacte en pixels

# ── bouton se connecter ───────────────────────────────────────────────
btn_ciseaux = ctk.CTkButton(
    app,
    text="Se connecter",
    font=("Segoe UI Emoji", 18),
    text_color="black",
    width= 50, height=10,
    fg_color="white",
    hover_color="grey",
    corner_radius=12
)
btn_ciseaux.place(x=270, y = 450)

# ── bouton valider connexion ───────────────────────────────────────────────
btn_ciseaux = ctk.CTkButton(
    app,
    text="Valider",
    font=("Segoe UI Emoji", 24),
    text_color="black",
    width=60, height=30,
    fg_color="grey",
    hover_color="white",
    corner_radius=12
)
btn_ciseaux.place(x=120, y=430)

# ── Lancement de la fenêtre ────────────────────────────────────────────────
app.mainloop()

