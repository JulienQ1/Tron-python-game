import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 12345))
server.listen(2)
clients = []

PLAYER_COLORS = [(255, 0, 0), (0, 0, 255)]  # Rouge et Bleu

def handle_client(client_socket, player_color):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            if data == b'quit':
                print(f"Client {client_socket.getpeername()} a quitté le jeu.")
                clients.remove(client_socket)
                client_socket.close()
            else:
                broadcast(data, client_socket, player_color)

        except Exception as e:
            print(f"Erreur: {str(e)}")
            break

    client_socket.close()

def broadcast(message, client_socket, player_color):
    for client in clients:
        if client != client_socket:
            try:
                # Envoyer les coordonnées x et y ainsi que la couleur du joueur
                client.send(f"{message.decode()},{player_color}".encode())
            except Exception as e:
                print(f"Erreur lors de la diffusion: {str(e)}")

print("Le serveur est prêt à écouter les connexions...")
player_index = 0
while True:
    client_socket, addr = server.accept()
    clients.append(client_socket)
    print(f"Client {addr} connecté au serveur.")

    # Assigner la couleur du joueur actuel
    player_color = PLAYER_COLORS[player_index]
    player_index = (player_index + 1) % len(PLAYER_COLORS)

    client_handler = threading.Thread(target=handle_client, args=(client_socket, player_color))
    client_handler.start()
