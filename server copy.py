import socket

# Server constants
SERVER_IP = "127.0.0.1"
SERVER_PORT = 6859
ALLOWED_USERNAMES = ["1234", "5678", "9012", "3456"]
LOGIN_SUC = "login_success"
LOGIN_FAIL = "login_fail"

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the IP and port
server_socket.bind((SERVER_IP, SERVER_PORT))

# Listen for incoming connections
server_socket.listen(5) # 5 is the maximum number of queued connections
print(f"Server started on {SERVER_IP}:{SERVER_PORT}, waiting for connections...")

while True:
    # Accept a new connection
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")

    # Receive the username from the client
    data = client_socket.recv(1024).decode('utf-8')

    # Check if the username is in the allowed list
    if data in ALLOWED_USERNAMES:
        client_socket.sendall(LOGIN_SUC.encode('utf-8'))
    else:
        client_socket.sendall(LOGIN_FAIL.encode('utf-8'))

    # Close the connection
    client_socket.close()
