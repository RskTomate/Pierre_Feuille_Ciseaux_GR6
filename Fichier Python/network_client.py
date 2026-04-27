"""
network_client.py — Module réseau réutilisable pour le client du jeu.
Gère la connexion TCP au serveur et l'envoi/réception de messages JSON.
"""
import socket
import json
import threading


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
        # Thread d'écoute en arrière-plan
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

    def play(self):
        self.send({"cmd": "PLAY"})

    def action(self, action: str):
        self.send({"cmd": "ACTION", "action": action})

    def quit_game(self):
        self.send({"cmd": "QUIT"})

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
