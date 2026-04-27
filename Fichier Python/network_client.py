"""
network_client.py — Module réseau réutilisable pour le client du jeu.
Gère la connexion TCP au serveur et l'envoi/réception de messages JSON.
"""
import socket
import json
import threading
import base64
import os

PDP_PATH = "images/profil/photo_de_profil.png"


class GameClient:
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False
        self._buffer = ""
        self._on_message = None   # callback(dict) appelé à chaque message reçu

    # ── Connexion ──────────────────────────────────────────────────────────
    def connect(self):
        """Ouvre la connexion TCP. Lève une exception si le serveur est inaccessible."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.connected = True
        t = threading.Thread(target=self._recv_loop, daemon=True)
        t.start()

    def disconnect(self):
        self.connected = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass

    # ── Envoi ──────────────────────────────────────────────────────────────
    def send(self, data: dict):
        if not self.connected:
            raise RuntimeError("Non connecté au serveur.")
        msg = json.dumps(data) + "\n"
        self.sock.sendall(msg.encode())

    # ── Commandes haut niveau ──────────────────────────────────────────────
    def register(self, username: str, password: str):
        self.send({"cmd": "REGISTER", "username": username, "password": password})

    def login(self, username: str, password: str):
        self.send({"cmd": "LOGIN", "username": username, "password": password})

    def send_profile_picture(self):
        """Envoie la photo de profil en base64 au serveur (après login réussi)."""
        if os.path.exists(PDP_PATH):
            with open(PDP_PATH, "rb") as f:
                data_b64 = base64.b64encode(f.read()).decode()
        else:
            data_b64 = ""
        self.send({"cmd": "SET_PICTURE", "picture": data_b64})

    def play_bot(self):
        self.send({"cmd": "PLAY_BOT"})

    def play_1v1(self):
        self.send({"cmd": "PLAY_1V1"})

    def play_tournament(self):
        self.send({"cmd": "PLAY_TOURNAMENT"})

    # Ancienne méthode conservée pour compatibilité
    def play(self):
        self.play_bot()

    def set_game(self, game_id: str):
        """Informe le serveur du game_id reçu via opponent_found (pour J1 en file d'attente)."""
        self.send({"cmd": "SET_GAME", "game_id": game_id})

    def ready(self):
        """Signale au serveur que le joueur est prêt à commencer la partie."""
        self.send({"cmd": "READY"})

    def action(self, choice: int):
        """Envoie le choix du joueur : 1=Pierre, 2=Feuille, 3=Ciseaux."""
        self.send({"cmd": "ACTION", "choice": choice})

    def quit_game(self):
        self.send({"cmd": "QUIT"})

    def ack_game_over(self):
        self.send({"cmd": "GAME_OVER_ACK"})

    # ── Réception (thread interne) ─────────────────────────────────────────
    def set_on_message(self, callback):
        """Enregistre le callback appelé pour chaque message serveur reçu."""
        self._on_message = callback

    def _recv_loop(self):
        while self.connected:
            try:
                data = self.sock.recv(4096).decode()
                if not data:
                    break
                self._buffer += data
                while "\n" in self._buffer:
                    line, self._buffer = self._buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                        if self._on_message:
                            self._on_message(msg)
                    except json.JSONDecodeError:
                        pass
            except Exception:
                break
        self.connected = False