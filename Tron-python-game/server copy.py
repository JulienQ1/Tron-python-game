import socket
import random
import time

# Server constants
SERVER_IP = "127.0.0.1"
SERVER_PORT = 6859
ALLOWED_USERNAMES = ["1234", "5678", "9012", "3456"]
LOGIN_SUC = "login_success"
LOGIN_FAIL = "login_fail"
PLAYER_CODES = ["A", "B", "C", "D"]
GAME_START = "game_start"

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the IP and port
server_socket.bind((SERVER_IP, SERVER_PORT))

# Listen for incoming connections
server_socket.listen(5)  # 5 is the maximum number of queued connections
print(f"Server started on {SERVER_IP}:{SERVER_PORT}, waiting for connections...")

allocated_codes = set()  # Keep track of allocated player codes

while True:
    # Accept a new connection
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")

    # Receive the username from the client
    data = client_socket.recv(1024).decode('utf-8')

    # Check if the username is in the allowed list
    if data in ALLOWED_USERNAMES:
        client_socket.sendall(LOGIN_SUC.encode('utf-8'))

        # Assign a player code that hasn't been allocated yet
        available_codes = list(set(PLAYER_CODES) - allocated_codes)
        if available_codes:
            assigned_code = random.choice(available_codes)
            allocated_codes.add(assigned_code)
            client_socket.sendall(assigned_code.encode('utf-8'))

            # Wait for 2 seconds
            time.sleep(2)

            # Send game start signal
            client_socket.sendall(GAME_START.encode('utf-8'))

            # Send random player positions for testing
            while True:
                time.sleep(1)  # Wait a second before sending the next positions
                positions = ','.join([f"{code}:{random.randint(100, 700)}-{random.randint(0, 600)}"
                                    for code in PLAYER_CODES])
                client_socket.sendall(positions.encode('utf-8'))


        else:
            client_socket.sendall("ERROR: No available player codes".encode('utf-8'))
            client_socket.close()

    else:
        client_socket.sendall(LOGIN_FAIL.encode('utf-8'))
        client_socket.close()
