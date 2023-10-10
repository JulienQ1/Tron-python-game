import socket

# Constants
SERVER_IP = "127.0.0.1"
SERVER_PORT = 0000
LOGIN_SUC = "login_success"
LOGIN_FAIL = "login_fail"
USER_NUMBER = 4
START = "game_start"
STOP = "game_stop"

# Create a server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (SERVER_IP, SERVER_PORT)
server_socket.bind(server_address)
server_socket.listen(USER_NUMBER)

print("Server started and waiting for clients to connect...")

# List to keep track of client sockets
clients = []

# Accept connections from clients
while len(clients) < USER_NUMBER:
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")
    clients.append(client_socket)
    
    # Receive username from the client
    username = client_socket.recv(1024).decode('utf-8')
    
    # For simplicity, let's assume every username is valid and just send a success message
    client_socket.sendall(LOGIN_SUC.encode('utf-8'))
    
print("All expected users connected. Starting the game...")

# Send start message to all clients
for client in clients:
    client.sendall(START.encode('utf-8'))

# Assume the game runs for some time, and then...
# Send stop message to all clients
for client in clients:
    client.sendall(STOP.encode('utf-8'))

# Close the server socket
server_socket.close()
