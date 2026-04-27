"""
interface_photo_de_profil.py — Sélection de la photo de profil.
Appelé via lancer(client, username) depuis interface_principale.
"""
import os
import customtkinter as ctk
from PIL import Image, ImageDraw
from tkinter import filedialog

PDP_SAVE_PATH = "images/profil/photo_de_profil.png"
os.makedirs("images/profil", exist_ok=True)

PARCHEMIN = "#D4B13B"
BRUN_BOIS = "#000000"
OR        = "#648195"
BLANC     = "#FFFFFF"
ROUGE     = "#8B1A1A"
VERT      = "#2A6B3A"
PREVIEW_SIZE = 160


def _image_carree(img_pil, size):
    w, h = img_pil.size
    m = min(w, h)
    img_pil = img_pil.crop(((w - m) // 2, (h - m) // 2, (w + m) // 2, (h + m) // 2))
    return img_pil.resize((size, size), Image.LANCZOS).convert("RGBA")


def _placeholder():
    img = Image.new("RGBA", (PREVIEW_SIZE, PREVIEW_SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([2, 2, PREVIEW_SIZE - 2, PREVIEW_SIZE - 2],
              fill="#4A6A8A", outline=PARCHEMIN, width=3)
    try:
        from PIL import ImageFont
        fnt = ImageFont.truetype("arial.ttf", 36)
    except Exception:
        from PIL import ImageFont
        fnt = ImageFont.load_default()
    d.text((PREVIEW_SIZE // 2 - 8, PREVIEW_SIZE // 2 - 18), "?", font=fnt, fill=BLANC)
    return img


def lancer(client, username):
    ctk.set_appearance_mode("light")
    app = ctk.CTk()
    app.title("Pierre Feuille Ciseaux — Photo de profil")
    app.geometry("400x560")
    app.configure(fg_color="#7B8B8E")
    app.resizable(False, False)

    # ── Fond ──────────────────────────────────────────────────────────────
    try:
        base_img = Image.open("images/image_de_base.png").resize((400, 560), Image.LANCZOS)
        bg_image = ctk.CTkImage(light_image=base_img, size=(400, 560))
        ctk.CTkLabel(app, image=bg_image, text="").place(x=0, y=0, relwidth=1, relheight=1)
    except Exception:
        pass

    # ── Titre ─────────────────────────────────────────────────────────────
    ctk.CTkLabel(app, text="Photo de profil",
                 font=("Arial", 26, "bold"),
                 text_color=PARCHEMIN, fg_color="transparent").place(x=0, y=20, relwidth=1)

    # ── Prévisualisation ──────────────────────────────────────────────────
    _state = {"preview_pil": None}

    if os.path.exists(PDP_SAVE_PATH):
        _state["preview_pil"] = _image_carree(Image.open(PDP_SAVE_PATH), PREVIEW_SIZE)
    else:
        _state["preview_pil"] = _placeholder()

    _preview_ctk = ctk.CTkImage(light_image=_state["preview_pil"], size=(PREVIEW_SIZE, PREVIEW_SIZE))
    lbl_preview = ctk.CTkLabel(app, image=_preview_ctk, text="")
    lbl_preview.ctk_image = _preview_ctk
    lbl_preview.place(x=(400 - PREVIEW_SIZE) // 2, y=80)

    lbl_statut = ctk.CTkLabel(app, text="", font=("Arial", 12, "bold"),
                               fg_color="transparent", text_color=ROUGE)
    lbl_statut.place(x=0, y=255, relwidth=1)

    # ── Logique ───────────────────────────────────────────────────────────

    def choisir_image():
        path = filedialog.askopenfilename(
            title="Choisir une image",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
                ("Tous les fichiers", "*.*"),
            ]
        )
        if not path:
            return
        try:
            img = Image.open(path)
            _state["preview_pil"] = _image_carree(img, PREVIEW_SIZE)
            new_ctk = ctk.CTkImage(light_image=_state["preview_pil"], size=(PREVIEW_SIZE, PREVIEW_SIZE))
            lbl_preview.configure(image=new_ctk)
            lbl_preview.ctk_image = new_ctk
            lbl_statut.configure(text="Image chargée — cliquez sur Enregistrer", text_color=OR)
        except Exception as e:
            lbl_statut.configure(text=f"✗ Erreur : {e}", text_color=ROUGE)

    def enregistrer():
        if _state["preview_pil"] is None:
            lbl_statut.configure(text="✗ Aucune image sélectionnée.", text_color=ROUGE)
            return
        try:
            save_img = _state["preview_pil"].resize((256, 256), Image.LANCZOS)
            save_img.save(PDP_SAVE_PATH, "PNG")
            # Envoyer la nouvelle photo au serveur immédiatement
            client.send_profile_picture()
            lbl_statut.configure(text="✓ Photo enregistrée !", text_color=VERT)
            app.after(1200, retour)
        except Exception as e:
            lbl_statut.configure(text=f"✗ Erreur sauvegarde : {e}", text_color=ROUGE)

    def retour():
        app.destroy()
        import interface_principale
        interface_principale.lancer(client, username)

    # ── Boutons ───────────────────────────────────────────────────────────
    ctk.CTkButton(app, text="📂  Choisir une image",
                  command=choisir_image,
                  font=("Arial", 18, "bold"), text_color=BLANC,
                  fg_color=BRUN_BOIS, hover_color=OR,
                  corner_radius=8, width=220, height=44).place(x=90, y=295)

    ctk.CTkButton(app, text="💾  Enregistrer",
                  command=enregistrer,
                  font=("Arial", 18, "bold"), text_color=BLANC,
                  fg_color=VERT, hover_color="#3D9B55",
                  corner_radius=8, width=220, height=44).place(x=90, y=360)

    ctk.CTkButton(app, text="← Retour",
                  command=retour,
                  font=("Arial", 13), text_color=BRUN_BOIS,
                  fg_color=PARCHEMIN, hover_color=OR,
                  corner_radius=6, width=100, height=30).place(x=150, y=500)

    app.mainloop()