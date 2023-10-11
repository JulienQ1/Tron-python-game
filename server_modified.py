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

GRID_SIZE = 10
GAME_AREA_SIZE = 600
GRID_COUNT = GAME_AREA_SIZE // GRID_SIZE
# Initialize the game grid as unused
game_grid = [["unused" for _ in range(GRID_COUNT)] for _ in range(GRID_COUNT)]
player_positions = {code: (random.randint(10, 59)*GRID_SIZE, random.randint(0, 59)*GRID_SIZE) for code in PLAYER_CODES}  # Initialize on the grid

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
                    while i < 2:
                        client_socket.sendall("waiting".encode('utf-8'))
                        time.sleep(1)
                        i += 1

                    # Give assigned players a random starting position on the grid
                    player_positions[assigned_code] = (random.randint(10, 59)*GRID_SIZE, random.randint(0, 59)*GRID_SIZE)
                    client_socket.sendall(GAME_START.encode('utf-8'))

                    while True:
                        client_socket.settimeout(0.5)
                        try:
                            move_command = client_socket.recv(1024).decode('utf-8').split(',')
                            player_code, direction = move_command[0], move_command[1]
                            x, y = player_positions[player_code]
                            if direction == "up" and y > 100:
                                y -= GRID_SIZE
                            elif direction == "down" and y < 700-GRID_SIZE:
                                y += GRID_SIZE
                            elif direction == "left" and x > 100:
                                x -= GRID_SIZE
                            elif direction == "right" and x < 700-GRID_SIZE:
                                x += GRID_SIZE

                            # Check if the grid cell is used
                            grid_x, grid_y = (x - 100) // GRID_SIZE, y // GRID_SIZE
                            if game_grid[grid_y][grid_x] == "used":
                                client_socket.sendall(f"{player_code},loss".encode('utf-8'))
                                break  # Exit the loop, ending the game for this player

                            game_grid[grid_y][grid_x] = "used"
                            player_positions[player_code] = (x, y)

                        except socket.timeout:
                            print("No data received after 0.5 seconds, moving on...")

                        positions = ','.join([f"{code}:{x}-{y}" for code, (x, y) in player_positions.items()])
                        client_socket.sendall(positions.encode('utf-8'))
            else:
                client_socket.sendall("ERROR: No available player codes".encode('utf-8'))
                client_socket.close()
    else:
        client_socket.sendall(LOGIN_FAIL.encode('utf-8'))
        client_socket.close()
