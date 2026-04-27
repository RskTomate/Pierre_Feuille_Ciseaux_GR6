"""
network_client.py — Module réseau réutilisable pour le client du jeu.
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
        self._on_message = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.connected = True
        threading.Thread(target=self._recv_loop, daemon=True).start()

    def disconnect(self):
        self.connected = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass

    def send(self, data: dict):
        if not self.connected:
            raise RuntimeError("Non connecté au serveur.")
        self.sock.sendall((json.dumps(data) + "\n").encode())

    # ── Commandes ──────────────────────────────────────────────────────────
    def register(self, username, password):
        self.send({"cmd": "REGISTER", "username": username, "password": password})

    def login(self, username, password):
        self.send({"cmd": "LOGIN", "username": username, "password": password})

    def play_bot(self):
        self.send({"cmd": "PLAY_BOT"})

    def play_1v1(self):
        self.send({"cmd": "PLAY_1V1"})

    def play_tournament(self):
        self.send({"cmd": "PLAY_TOURNAMENT"})

    def action(self, choice: int):
        """choice : 1=Pierre, 2=Feuille, 3=Ciseaux"""
        self.send({"cmd": "ACTION", "choice": choice})

    def quit_game(self):
        self.send({"cmd": "QUIT"})

    def ack_game_over(self):
        self.send({"cmd": "GAME_OVER_ACK"})

    # ── Réception ─────────────────────────────────────────────────────────
    def set_on_message(self, callback):
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