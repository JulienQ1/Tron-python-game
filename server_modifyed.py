import socket
import random
import time

# Server constants
SERVER_IP = "127.0.0.1"
SERVER_PORT = 6859
ALLOWED_USERNAMES = ["1111", "2222", "3333", "4444"]
LOGIN_SUC = "login_success"
LOGIN_FAIL = "login_fail"
PLAYER_CODES = ["A", "B", "C", "D"]
GAME_START = "game_start"

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the IP and port
server_socket.bind((SERVER_IP, SERVER_PORT))

# Listen for incoming connections
server_socket.listen(5)
print(f"Server started on {SERVER_IP}:{SERVER_PORT}, waiting for connections...")

allocated_codes = set()
player_positions = {code: (random.randint(800, 1000), random.randint(700, 900)) for code in PLAYER_CODES}  # Initialize off-screen

while True:
    # Accept a new connection
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")

    data = client_socket.recv(1024).decode('utf-8')
    if data in ALLOWED_USERNAMES:
        client_socket.sendall(LOGIN_SUC.encode('utf-8'))
        data = client_socket.recv(1024).decode('utf-8')
        if data == "need_user_code":
            available_codes = list(set(PLAYER_CODES) - allocated_codes)
            if available_codes:
                assigned_code = random.choice(available_codes)
                allocated_codes.add(assigned_code)
                client_socket.sendall(assigned_code.encode('utf-8'))
                data = client_socket.recv(1024).decode('utf-8')
                if data == "get_user_code":
                    i = 0
                    while i < 10:
                        client_socket.sendall("waiting".encode('utf-8'))
                        time.sleep(1)
                        i += 1

                    # Give assigned players a random starting position
                    player_positions[assigned_code] = (random.randint(100, 700), random.randint(0, 600))
                    client_socket.sendall(GAME_START.encode('utf-8'))

                    while True:
                        move_command = client_socket.recv(1024).decode('utf-8').split(',')
                        player_code, direction = move_command[0], move_command[1]
                        x, y = player_positions[player_code]
                        if direction == "up":
                            y -= 10
                        elif direction == "down":
                            y += 10
                        elif direction == "left":
                            x -= 10
                        elif direction == "right":
                            x += 10
                        player_positions[player_code] = (x, y)

                        time.sleep(1)
                        positions = ','.join([f"{code}:{x}-{y}" for code, (x, y) in player_positions.items()])
                        client_socket.sendall(positions.encode('utf-8'))
            else:
                client_socket.sendall("ERROR: No available player codes".encode('utf-8'))
                client_socket.close()
    else:
        client_socket.sendall(LOGIN_FAIL.encode('utf-8'))
        client_socket.close()
