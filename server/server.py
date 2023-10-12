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
SPEED = 1

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the IP and port
server_socket.bind((SERVER_IP, SERVER_PORT))

# Listen for incoming connections
server_socket.listen(5)
print(f"Server started on {SERVER_IP}:{SERVER_PORT}, waiting for connections...")

allocated_codes = set()

#Build and initialized the grid
GRID_SIZE = 1
GAME_AREA_SIZE = 600
GRID_COUNT = GAME_AREA_SIZE // GRID_SIZE
# Initialize the game grid as unused
game_grid = [["unused" for _ in range(GRID_COUNT)] for _ in range(GRID_COUNT)]
#player_positions = {code: (800 + random.randint(1, 10)*GRID_SIZE, random.randint(0, 59)*GRID_SIZE) for code in PLAYER_CODES}
player_positions = {code: (0, 0) for code in PLAYER_CODES}
old_place = {code: (0, 0) for code in PLAYER_CODES}
new_place = {code: (0, 0) for code in PLAYER_CODES}
delta_place = {code: (0, 0) for code in PLAYER_CODES}
delta_x = 0
delta_y = 0
  # Initialize on the grid
  # Initialize off-screen

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
                    while i < 1:
                        client_socket.sendall("waiting".encode('utf-8'))
                        time.sleep(1)
                        i += 1

                    # Give assigned players a random starting position
                    player_positions[assigned_code] = (random.randint(100, 590)*GRID_SIZE, random.randint(0, 590)*GRID_SIZE)

                    client_socket.sendall(GAME_START.encode('utf-8'))

                    while True:
                        client_socket.settimeout(0.01)
                        try:
                            move_command = client_socket.recv(1024).decode('utf-8').split(',')
                            player_code, direction = move_command[0], move_command[1]
                            x, y = player_positions[player_code]
                            old_place[player_code] = player_positions[player_code]
                            if direction == "up" and y > 0:
                                y -= GRID_SIZE
                            elif direction == "down" and y < 580:
                                y += GRID_SIZE
                            elif direction == "left" and x > 90:
                                x -= GRID_SIZE
                            elif direction == "right" and x < 670:
                                x += GRID_SIZE

                            # Check if the grid cell is used
                            grid_x, grid_y = (x - 100) // GRID_SIZE, y // GRID_SIZE
                            if game_grid[grid_y][grid_x] == "used":
                                client_socket.sendall(f"{player_code},loss".encode('utf-8'))
                                #break  # Exit the loop, ending the game for this player

                            game_grid[grid_y][grid_x] = "used"
                            new_place[player_code] = (x,y)
                            player_positions[player_code] = (x, y)
                            delta_x = new_place[player_code][0] - old_place[player_code][0]
                            delta_y = new_place[player_code][1] - old_place[player_code][1]
                            delta_place[player_code] = (delta_x, delta_y)
                        except socket.timeout:
                            #print("No data received after 0.1 seconds, moving on...")
                            for player_code in PLAYER_CODES:
                                x0,y0 = player_positions[player_code]
                                delta_x,delta_y = delta_place[player_code]
                                x1 = x0 + delta_x*SPEED
                                y1 = y0 + delta_y*SPEED
                                player_positions[player_code] = (x1,y1)
                                #print(x1,x0,y1,y0)
                                if (delta_x !=0 or delta_y != 0):
                                    #print('not startimg point colliding')
                                    grid_x_delta, grid_y_delta = (x1 - 90) // GRID_SIZE, y1 // GRID_SIZE
                                    if game_grid[grid_y_delta][grid_x_delta] == "used":
                                        print('collided')
                                        client_socket.sendall(f"{player_code},loss".encode('utf-8'))
                                        print("loss send at",game_grid[grid_y_delta][grid_x_delta],(x1-90),y1)
                                        #break  # Exit the loop, ending the game for this player
                                    else:
                                        print('used case now')
                                        game_grid[grid_y_delta][grid_x_delta] = "used"
                        positions = ','.join([f"{code}:{x}-{y}" for code, (x, y) in player_positions.items()])
                        client_socket.sendall(positions.encode('utf-8'))
            else:
                client_socket.sendall("ERROR: No available player codes".encode('utf-8'))
                client_socket.close()
    else:
        client_socket.sendall(LOGIN_FAIL.encode('utf-8'))
        client_socket.close()
