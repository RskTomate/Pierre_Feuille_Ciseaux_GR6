import socket
import threading
import json
import hashlib
import os
import time

# ─────────────────────────────────────────────
#  Stockage des utilisateurs (fichier JSON)
# ─────────────────────────────────────────────
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ─────────────────────────────────────────────
#  État global du serveur
# ─────────────────────────────────────────────
users = load_users()          # { username: hashed_password }
connected = {}                # { username: conn }
waiting_player = None         # joueur en attente de partie
games = {}                    # { game_id: { "players": [p1, p2], "state": ... } }
lock = threading.Lock()

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
def send(conn, data: dict):
    try:
        msg = json.dumps(data) + "\n"
        conn.sendall(msg.encode())
    except Exception:
        pass

def broadcast_game(game_id, data):
    game = games.get(game_id)
    if game:
        for username in game["players"]:
            conn = connected.get(username)
            if conn:
                send(conn, data)

# ─────────────────────────────────────────────
#  Logique des commandes
# ─────────────────────────────────────────────
def cmd_register(conn, username, password):
    with lock:
        if username in users:
            send(conn, {"type": "error", "msg": "Nom d'utilisateur déjà pris."})
        else:
            users[username] = hash_password(password)
            save_users(users)
            send(conn, {"type": "ok", "msg": f"Compte '{username}' créé avec succès."})

def cmd_login(conn, username, password):
    global waiting_player
    with lock:
        if username not in users:
            send(conn, {"type": "error", "msg": "Utilisateur introuvable."})
            return None
        if users[username] != hash_password(password):
            send(conn, {"type": "error", "msg": "Mot de passe incorrect."})
            return None
        if username in connected:
            send(conn, {"type": "error", "msg": "Déjà connecté depuis un autre client."})
            return None
        connected[username] = conn
        send(conn, {"type": "ok", "msg": f"Bienvenue, {username} !"})
        return username

def cmd_play(username):
    global waiting_player
    with lock:
        if waiting_player is None:
            waiting_player = username
            conn = connected.get(username)
            send(conn, {"type": "info", "msg": "En attente d'un adversaire..."})
        elif waiting_player != username:
            # Lancer la partie
            p1 = waiting_player
            p2 = username
            waiting_player = None
            game_id = f"{p1}_vs_{p2}_{int(time.time())}"
            games[game_id] = {
                "players": [p1, p2],
                "state": "in_progress",
                "turn": p1,
            }
            broadcast_game(game_id, {
                "type": "game_start",
                "game_id": game_id,
                "players": [p1, p2],
                "turn": p1,
                "msg": f"Partie lancée ! {p1} vs {p2}. C'est au tour de {p1}.",
            })
            return game_id
        else:
            conn = connected.get(username)
            send(conn, {"type": "info", "msg": "Tu es déjà en attente d'une partie."})
    return None

def cmd_action(username, game_id, action):
    """Exemple générique d'action en jeu — à adapter selon ton jeu."""
    with lock:
        game = games.get(game_id)
        if not game:
            conn = connected.get(username)
            send(conn, {"type": "error", "msg": "Partie introuvable."})
            return
        if game["state"] != "in_progress":
            conn = connected.get(username)
            send(conn, {"type": "error", "msg": "La partie est terminée."})
            return
        if game["turn"] != username:
            conn = connected.get(username)
            send(conn, {"type": "error", "msg": "Ce n'est pas ton tour."})
            return

        # ── Ici, implémente ta logique de jeu ──
        # Exemple : on passe juste le tour à l'adversaire
        players = game["players"]
        next_turn = players[1] if players[0] == username else players[0]
        game["turn"] = next_turn

        broadcast_game(game_id, {
            "type": "game_update",
            "game_id": game_id,
            "action": action,
            "played_by": username,
            "turn": next_turn,
            "msg": f"{username} a joué '{action}'. C'est maintenant le tour de {next_turn}.",
        })

def cmd_quit_game(username, game_id):
    with lock:
        game = games.get(game_id)
        if not game:
            return
        game["state"] = "finished"
        broadcast_game(game_id, {
            "type": "game_over",
            "game_id": game_id,
            "winner": None,
            "msg": f"{username} a quitté la partie.",
        })
        del games[game_id]

def disconnect(username):
    global waiting_player
    with lock:
        connected.pop(username, None)
        if waiting_player == username:
            waiting_player = None
    print(f"[SERVER] {username} déconnecté.")

# ─────────────────────────────────────────────
#  Boucle de traitement par client
# ─────────────────────────────────────────────
def handle_client(conn, addr):
    print(f"[SERVER] Connexion de {addr}")
    username = None
    current_game = None
    buffer = ""

    send(conn, {"type": "info", "msg": "Bienvenue ! Commandes : REGISTER, LOGIN, PLAY, ACTION, QUIT"})

    try:
        while True:
            data = conn.recv(4096).decode()
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    send(conn, {"type": "error", "msg": "Format JSON invalide."})
                    continue

                cmd = msg.get("cmd", "").upper()

                if cmd == "REGISTER":
                    cmd_register(conn, msg.get("username", ""), msg.get("password", ""))

                elif cmd == "LOGIN":
                    username = cmd_login(conn, msg.get("username", ""), msg.get("password", ""))

                elif cmd == "PLAY":
                    if not username:
                        send(conn, {"type": "error", "msg": "Tu dois être connecté."})
                    else:
                        gid = cmd_play(username)
                        if gid:
                            current_game = gid

                elif cmd == "ACTION":
                    if not username or not current_game:
                        send(conn, {"type": "error", "msg": "Tu n'es pas en partie."})
                    else:
                        cmd_action(username, current_game, msg.get("action", ""))

                elif cmd == "QUIT":
                    if current_game:
                        cmd_quit_game(username, current_game)
                        current_game = None
                    else:
                        break

                else:
                    send(conn, {"type": "error", "msg": f"Commande inconnue : {cmd}"})

    except Exception as e:
        print(f"[SERVER] Erreur avec {addr}: {e}")
    finally:
        if username:
            disconnect(username)
        conn.close()

# ─────────────────────────────────────────────
#  Point d'entrée
# ─────────────────────────────────────────────
if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 5000
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    print(f"[SERVER] Écoute sur {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        t.start()