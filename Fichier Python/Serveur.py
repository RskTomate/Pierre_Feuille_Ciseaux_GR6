import socket
import threading
import json
import hashlib
import os
import time
import random

# ─────────────────────────────────────────────
#  Stockage des utilisateurs
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
#  État global
# ─────────────────────────────────────────────
users        = load_users()
connected    = {}          # { username: conn }
waiting_1v1  = None        # joueur en attente de partie normale
games        = {}          # { game_id: { ... } }
tournaments  = {}          # { tournament_id: { ... } }
waiting_tournament = []    # liste des joueurs en attente de tournoi
lock         = threading.Lock()

# ─────────────────────────────────────────────
#  Helpers réseau
# ─────────────────────────────────────────────
def send(conn, data: dict):
    try:
        conn.sendall((json.dumps(data) + "\n").encode())
    except Exception:
        pass

def send_to(username, data: dict):
    conn = connected.get(username)
    if conn:
        send(conn, data)

def broadcast_game(game_id, data):
    game = games.get(game_id)
    if game:
        for u in game["players"]:
            if u != "BOT":
                send_to(u, data)

# ─────────────────────────────────────────────
#  Logique PFC
# ─────────────────────────────────────────────
CHOICES = {1: "Pierre", 2: "Feuille", 3: "Ciseaux"}

def resolve(c1, c2):
    if c1 == c2:
        return 0
    if (c1 == 1 and c2 == 3) or (c1 == 2 and c2 == 1) or (c1 == 3 and c2 == 2):
        return 1
    return 2

# ─────────────────────────────────────────────
#  Gestion des parties
# ─────────────────────────────────────────────
def create_game(p1, p2, tournament_id=None, match_key=None):
    """
    Crée une partie entre p1 et p2.
    - Si p2 == 'BOT' : game_start envoyé immédiatement (pas de phase READY).
    - Sinon : la partie est en état 'waiting_ready' jusqu'à ce que les deux
      joueurs aient envoyé CMD READY.
    """
    game_id = f"{p1}_vs_{p2}_{int(time.time() * 1000)}"
    is_bot_game = (p2 == "BOT")

    games[game_id] = {
        "players":       [p1, p2],
        "scores":        {p1: 0, p2: 0} if is_bot_game else {p1: 0, p2: 0},
        "choices":       {},
        "ready":         set(),          # joueurs ayant confirmé "Prêt"
        "state":         "in_progress" if is_bot_game else "waiting_ready",
        "tournament_id": tournament_id,
        "match_key":     match_key,
    }

    if is_bot_game:
        # Bot : game_start immédiat
        send_to(p1, {
            "type":    "game_start",
            "game_id": game_id,
            "players": [p1, p2],
            "msg":     f"Partie lancée ! {p1} vs {p2}",
        })
    else:
        # 1v1 humain : on prévient les deux joueurs de l'adversaire trouvé
        # mais on attend leurs READY avant d'envoyer game_start
        for u, adv in [(p1, p2), (p2, p1)]:
            send_to(u, {
                "type":      "opponent_found",
                "game_id":   game_id,
                "opponent":  adv,
                "players":   [p1, p2],
                "msg":       f"Adversaire trouvé : {adv} ! Cliquez sur Prêt pour commencer.",
            })

    return game_id


def _try_start_game(game_id):
    """Appelé après chaque READY : démarre la partie si les deux joueurs sont prêts."""
    game = games.get(game_id)
    if not game or game["state"] != "waiting_ready":
        return
    p1, p2 = game["players"]
    if p1 in game["ready"] and p2 in game["ready"]:
        game["state"] = "in_progress"
        broadcast_game(game_id, {
            "type":    "game_start",
            "game_id": game_id,
            "players": [p1, p2],
            "msg":     f"Partie lancée ! {p1} vs {p2}",
        })


def process_choices(game_id):
    """Appelé quand les deux joueurs ont choisi. Résout la manche."""
    game = games.get(game_id)
    if not game:
        return
    p1, p2 = game["players"]
    c1 = game["choices"].get(p1, 4)
    c2 = game["choices"].get(p2, random.randint(1, 3) if p2 == "BOT" else 4)

    result = resolve(c1, c2)
    if result == 1:
        game["scores"][p1] += 1
        winner_round = p1
    elif result == 2:
        game["scores"][p2] += 1
        winner_round = p2
    else:
        winner_round = None

    s1, s2 = game["scores"][p1], game["scores"][p2]

    broadcast_game(game_id, {
        "type":         "round_result",
        "game_id":      game_id,
        "choice_p1":    c1,
        "choice_p2":    c2,
        "winner_round": winner_round,
        "scores":       {p1: s1, p2: s2},
    })

    # Vider les choix pour la prochaine manche
    game["choices"] = {}

    # Vérifier si la partie est finie (premier à 3)
    if s1 >= 3 or s2 >= 3:
        game_winner = p1 if s1 >= 3 else p2
        game["state"] = "finished"
        broadcast_game(game_id, {
            "type":    "game_over",
            "game_id": game_id,
            "winner":  game_winner,
            "scores":  {p1: s1, p2: s2},
            "msg":     f"{game_winner} remporte la partie !",
        })
        tid = game.get("tournament_id")
        if tid:
            tournament_advance(tid, game["match_key"], game_winner)
        del games[game_id]


def cmd_action(username, game_id, choice):
    """Le joueur envoie son choix (1/2/3)."""
    with lock:
        game = games.get(game_id)
        if not game or game["state"] != "in_progress":
            send_to(username, {"type": "error", "msg": "Partie introuvable ou pas encore démarrée."})
            return
        if username not in game["players"]:
            send_to(username, {"type": "error", "msg": "Tu n'es pas dans cette partie."})
            return
        if username in game["choices"]:
            send_to(username, {"type": "error", "msg": "Tu as déjà joué cette manche."})
            return

        game["choices"][username] = choice
        send_to(username, {"type": "info", "msg": "Choix enregistré, attente de l'adversaire…"})

        p1, p2 = game["players"]
        other = p2 if username == p1 else p1

        if other == "BOT" or other in game["choices"]:
            process_choices(game_id)


def cmd_ready(username, game_id):
    """Le joueur confirme qu'il est prêt à jouer."""
    with lock:
        game = games.get(game_id)
        if not game:
            send_to(username, {"type": "error", "msg": "Partie introuvable."})
            return
        if username not in game["players"]:
            send_to(username, {"type": "error", "msg": "Tu n'es pas dans cette partie."})
            return
        game["ready"].add(username)
        p1, p2 = game["players"]
        other = p2 if username == p1 else p1
        # Informer l'adversaire qu'on est prêt
        send_to(other, {"type": "opponent_ready", "msg": f"{username} est prêt !"})
        _try_start_game(game_id)

# ─────────────────────────────────────────────
#  Commandes réseau
# ─────────────────────────────────────────────
def cmd_register(conn, username, password):
    with lock:
        if not username or not password:
            send(conn, {"type": "error", "msg": "Champs vides."})
            return
        if username in users:
            send(conn, {"type": "error", "msg": "Nom d'utilisateur déjà pris."})
        else:
            users[username] = hash_password(password)
            save_users(users)
            send(conn, {"type": "ok", "msg": f"Compte '{username}' créé avec succès."})


def cmd_login(conn, username, password):
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
        send(conn, {"type": "ok", "msg": f"Bienvenue, {username} !", "username": username})
        return username


def cmd_play_bot(username):
    """Lance une partie immédiate contre le bot."""
    with lock:
        game_id = create_game(username, "BOT")
    return game_id


def cmd_play_1v1(username):
    """Matchmaking 1v1 contre un autre joueur humain."""
    global waiting_1v1
    with lock:
        if waiting_1v1 is None:
            waiting_1v1 = username
            send_to(username, {"type": "info", "msg": "En attente d'un adversaire…"})
            return None
        elif waiting_1v1 == username:
            send_to(username, {"type": "info", "msg": "Tu es déjà en file d'attente."})
            return None
        else:
            p1, p2 = waiting_1v1, username
            waiting_1v1 = None
            game_id = create_game(p1, p2)
            # Les deux joueurs reçoivent opponent_found avec le game_id
            # → handle_client mettra à jour current_game via le message opponent_found
            return game_id


def cmd_play_tournament(username):
    """Inscrit le joueur au prochain tournoi à 4."""
    global waiting_tournament
    with lock:
        if username in waiting_tournament:
            send_to(username, {"type": "info", "msg": "Tu es déjà inscrit au tournoi."})
            return
        waiting_tournament.append(username)
        nb = len(waiting_tournament)
        for u in waiting_tournament:
            send_to(u, {"type": "info", "msg": f"Tournoi : {nb}/4 joueurs inscrits…"})
        if nb == 4:
            players = list(waiting_tournament)
            waiting_tournament.clear()
            _start_tournament(players)


def _start_tournament(players):
    random.shuffle(players)
    tid = f"tournament_{int(time.time())}"
    tournaments[tid] = {
        "players":  players,
        "matches":  {
            "semi1": {"players": [players[0], players[1]], "winner": None},
            "semi2": {"players": [players[2], players[3]], "winner": None},
            "final": {"players": [],                       "winner": None},
        },
        "state": "semi",
    }
    for u in players:
        send_to(u, {
            "type":    "tournament_start",
            "players": players,
            "bracket": {
                "semi1": [players[0], players[1]],
                "semi2": [players[2], players[3]],
            },
            "msg": f"Tournoi lancé ! {players[0]} vs {players[1]}  |  {players[2]} vs {players[3]}",
        })
    with lock:
        g1 = create_game(players[0], players[1], tournament_id=tid, match_key="semi1")
        g2 = create_game(players[2], players[3], tournament_id=tid, match_key="semi2")
        tournaments[tid]["matches"]["semi1"]["game_id"] = g1
        tournaments[tid]["matches"]["semi2"]["game_id"] = g2


def tournament_advance(tid, match_key, winner):
    with lock:
        t = tournaments.get(tid)
        if not t:
            return
        t["matches"][match_key]["winner"] = winner

        if match_key in ("semi1", "semi2"):
            w1 = t["matches"]["semi1"]["winner"]
            w2 = t["matches"]["semi2"]["winner"]
            if w1 and w2:
                t["state"] = "final"
                t["matches"]["final"]["players"] = [w1, w2]
                all_players = t["players"]
                for u in all_players:
                    send_to(u, {
                        "type": "tournament_final",
                        "players": [w1, w2],
                        "msg": f"Finale ! {w1} vs {w2}",
                    })
                gf = create_game(w1, w2, tournament_id=tid, match_key="final")
                t["matches"]["final"]["game_id"] = gf

        elif match_key == "final":
            t["state"] = "done"
            t["matches"]["final"]["winner"] = winner
            all_players = t["players"]
            for u in all_players:
                send_to(u, {
                    "type":   "tournament_over",
                    "winner": winner,
                    "msg":    f"🏆 {winner} remporte le tournoi !",
                })


def cmd_quit_game(username, game_id):
    with lock:
        game = games.get(game_id)
        if not game:
            return
        game["state"] = "finished"
        broadcast_game(game_id, {
            "type":    "game_over",
            "game_id": game_id,
            "winner":  None,
            "msg":     f"{username} a quitté la partie.",
        })
        games.pop(game_id, None)


def disconnect(username):
    global waiting_1v1
    with lock:
        connected.pop(username, None)
        if waiting_1v1 == username:
            waiting_1v1 = None
        if username in waiting_tournament:
            waiting_tournament.remove(username)
    print(f"[SERVER] {username} déconnecté.")

# ─────────────────────────────────────────────
#  Boucle par client
# ─────────────────────────────────────────────
def handle_client(conn, addr):
    print(f"[SERVER] Connexion de {addr}")
    username = None
    current_game = None
    buf = ""

    send(conn, {"type": "info", "msg": "Connecté au serveur PFC."})

    try:
        while True:
            data = conn.recv(4096).decode()
            if not data:
                break
            buf += data
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    send(conn, {"type": "error", "msg": "JSON invalide."})
                    continue

                cmd = msg.get("cmd", "").upper()

                if cmd == "REGISTER":
                    cmd_register(conn, msg.get("username", ""), msg.get("password", ""))

                elif cmd == "LOGIN":
                    username = cmd_login(conn, msg.get("username", ""), msg.get("password", ""))

                elif cmd == "PLAY_BOT":
                    if not username:
                        send(conn, {"type": "error", "msg": "Connecte-toi d'abord."})
                    else:
                        current_game = cmd_play_bot(username)

                elif cmd == "PLAY_1V1":
                    if not username:
                        send(conn, {"type": "error", "msg": "Connecte-toi d'abord."})
                    else:
                        gid = cmd_play_1v1(username)
                        if gid:
                            # J2 (celui qui complète la paire) reçoit le game_id ici
                            current_game = gid

                elif cmd == "PLAY_TOURNAMENT":
                    if not username:
                        send(conn, {"type": "error", "msg": "Connecte-toi d'abord."})
                    else:
                        cmd_play_tournament(username)

                elif cmd == "SET_GAME":
                    # Le client nous informe du game_id qu'il a reçu via opponent_found
                    # (utile pour J1 qui était en file d'attente)
                    gid = msg.get("game_id")
                    if gid and gid in games:
                        current_game = gid
                    else:
                        send(conn, {"type": "error", "msg": "game_id invalide."})

                elif cmd == "READY":
                    if not username or not current_game:
                        send(conn, {"type": "error", "msg": "Tu n'es pas en partie."})
                    else:
                        cmd_ready(username, current_game)

                elif cmd == "ACTION":
                    if not username or not current_game:
                        send(conn, {"type": "error", "msg": "Tu n'es pas en partie."})
                    else:
                        try:
                            choice = int(msg.get("choice", 0))
                        except (ValueError, TypeError):
                            choice = 0
                        if choice not in (1, 2, 3):
                            send(conn, {"type": "error", "msg": "Choix invalide (1=Pierre, 2=Feuille, 3=Ciseaux)."})
                        else:
                            cmd_action(username, current_game, choice)

                elif cmd == "GAME_OVER_ACK":
                    current_game = None

                elif cmd == "QUIT":
                    if current_game:
                        cmd_quit_game(username, current_game)
                        current_game = None
                    else:
                        break

                else:
                    send(conn, {"type": "error", "msg": f"Commande inconnue : {cmd}"})

    except Exception as e:
        print(f"[SERVER] Erreur {addr}: {e}")
    finally:
        if username:
            disconnect(username)
        conn.close()

# ─────────────────────────────────────────────
#  Point d'entrée
# ─────────────────────────────────────────────
if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 5000
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(20)
    print(f"[SERVER] PFC Server en écoute sur {HOST}:{PORT}")
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()