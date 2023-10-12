import socket
import threading

# Configuration du serveur
HOST = '127.0.0.1'
PORT = 55555

# Créer un socket serveur
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("En attente de connexion ...")

# Liste des clients connectés
clients = []
nicknames = []

# Diffuser un message à tous les clients
def broadcast(message):
    for client in clients:
        client.send(message)

# Gérer les messages des clients
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} a quitté le chat!'.encode('utf-8'))
            nicknames.remove(nickname)
            break

# Accepter les connexions des clients
def accept_clients():
    while True:
        client, address = server.accept()
        print(f"Connexion établie avec {str(address)}")

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        print(f'Nom d\'utilisateur du client est {nickname}!')
        broadcast(f'{nickname} a rejoint le chat!'.encode('utf-8'))
        client.send('Connecté au chat!'.encode('utf-8'))

        # Lancer un thread pour gérer le client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

if __name__ == '__main__':
    accept_clients()
