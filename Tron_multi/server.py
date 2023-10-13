import socket
import threading

# Configuration du serveur
HOST = '127.0.0.1'
PORT = 55555

# Créer un socket serveur
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("En attente de connexions...")

# Liste des clients connectés
clients = []
nicknames = []

# Positions initiales des joueurs
joueurs = {
    "joueur1": (100, 300),
    "joueur2": (375, 300),
    "joueur3": (650, 300)
}

# Vitesse de déplacement des joueurs
vitesse = 5

# Diffuser un message à tous les clients
def broadcast(message):
    for client in clients:
        client.send(message)

# Gérer les messages des clients
def handle(client, nickname):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message.startswith('MOVE'):
                _, dx, dy = message.split()
                dx, dy = float(dx), float(dy)

                # Mettre à jour la position du joueur
                x, y = joueurs[nickname]
                x += dx * vitesse
                y += dy * vitesse
                joueurs[nickname] = (x, y)

                # Diffuser la nouvelle position des joueurs
                positions = 'POS'
                for name, (x, y) in joueurs.items():
                    positions += f' {name} {x} {y}'
                broadcast(positions.encode('utf-8'))

        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} a quitté le jeu!'.encode('utf-8'))
            nicknames.remove(nickname)
            break

# Accepter les connexions des clients
def accept_clients():
    while len(clients) < 3:
        client, address = server.accept()
        print(f"Connexion établie avec {str(address)}")

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        print(f'Nom d\'utilisateur du client est {nickname}!')
        broadcast(f'{nickname} a rejoint le jeu!'.encode('utf-8'))
        client.send('Connecté au jeu!'.encode('utf-8'))

        # Envoyer les positions initiales des joueurs
        positions = 'POS'
        for name, (x, y) in joueurs.items():
            positions += f' {name} {x} {y}'
        client.send(positions.encode('utf-8'))

        # Lancer un thread pour gérer le client
        thread = threading.Thread(target=handle, args=(client, nickname))
        thread.start()

if __name__ == '__main__':
    accept_clients()
