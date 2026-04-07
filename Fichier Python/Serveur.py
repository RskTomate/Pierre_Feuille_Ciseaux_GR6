import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 5000))  # écoute sur le port 5000
server.listen(1)

print("En attente de connexion...")
conn, addr = server.accept()
print(f"Connecté depuis {addr}")

message = conn.recv(1024).decode()
print(f"Message reçu : {message}")
conn.close()