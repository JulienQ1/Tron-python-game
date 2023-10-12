import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 12345))  
server.listen(2)  
clients = []


def handle_client(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            if data == b'quit':
                print(f"Client {client_socket.getpeername()} a quitté le jeu.")
                clients.remove(client_socket)
                client_socket.close()
            else : 
                broadcast(data, client_socket)

        except Exception as e:
            print(f"Erreur: {str(e)}")
            break

    client_socket.close()


def broadcast(message, client_socket):
    for client in clients:
        if client != client_socket:
            try:
                client.send(message)
            except Exception as e:
                print(f"Erreur lors de la diffusion: {str(e)}")

print("Le serveur est prêt à écouter les connexions...")
while True:
    client_socket, addr = server.accept()
    clients.append(client_socket)
    print(f"Client {addr} connecté au serveur.")

    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.start()


