import socket
import random
import time
from multiprocessing import Process, Manager, Lock

#some print used to debug and test

# Server constants
SERVER_IP = "172.21.72.240"
SERVER_PORT = 6859
ALLOWED_USERNAMES = ["1111", "2222", "3333", "4444"]
LOGIN_SUC = "login_success"
LOGIN_FAIL = "login_fail"
PLAYER_CODES = ["A", "B", "C", "D"]
GAME_START = "game_start"
SPEED = 1

#Grid constants
#Build and initialized the grid
GRID_SIZE = 1
GAME_AREA_SIZE = 600
GRID_COUNT = GAME_AREA_SIZE // GRID_SIZE
#value of shared_char, to control game:
START = 'S'
INIT = "I"


#a thread to control the game process
def monitor_clients(allocated_codes,lock,shared_Char):
    while True:
        #print(allocated_codes)
        time.sleep(0.1)
        if len(allocated_codes) >=2 :
            print("prepare!")
            break
    i = 10
    while i >0:
        print("will start at :",i)
        time.sleep(1)
        i = i -1
    print("start!")
    with lock:
        shared_Char.value = START




#4 thread to handel the clients
def handle_client(client_socket, game_grid, player_positions,allocated_codes,lock,index,shared_Char,old_place,new_place,delta_place):
        #Use the provided client_socket to communicate with the client
        #Use game_grid and player_positions as shared state
        #Use lock to ensure synchronized access to shared state
        #index for debug
    print(f"Connection from {client_socket}")
    #validate the username
    data = client_socket.recv(1024).decode('utf-8')
    if data in ALLOWED_USERNAMES:
        #print(data," has loged in")
        client_socket.sendall(LOGIN_SUC.encode('utf-8'))
        data = client_socket.recv(1024).decode('utf-8')
        #shake hands to ensure user got the code
        if data == "need_user_code":
            available_codes = list(set(PLAYER_CODES) - set(allocated_codes))
            assigned_code = random.choice(available_codes)
            with lock:
                allocated_codes.append(assigned_code)
            client_socket.sendall(assigned_code.encode('utf-8'))
            data = client_socket.recv(1024).decode('utf-8')
            if data == "get_user_code":
                client_socket.sendall("waiting".encode('utf-8'))
                #listen the control code, wether to start
                while True:
                    #print(shared_Char)
                    if shared_Char.value == START:
                        break
                    time.sleep(0.1)
                print("Game start at", index)
                with lock:
                    player_positions[assigned_code] = (random.randint(100, 590)*GRID_SIZE, random.randint(0, 590)*GRID_SIZE)
                    client_socket.sendall(GAME_START.encode('utf-8'))
                #don't know wether should use lock, remove if needn't
                while True:
                    client_socket.settimeout(0.01)
                    try:
                        move_command = client_socket.recv(1024).decode('utf-8').split(',')
                        player_code, direction = move_command[0], move_command[1]
                        x, y = player_positions[player_code]
                        print(player_positions[player_code])
                        grid_current_x, grid_current_y = (x - 100) // GRID_SIZE, y // GRID_SIZE
                        with lock:
                            old_place[player_code] = player_positions[player_code]

                        if direction == "up" and y > 0:
                            y -= GRID_SIZE
                        elif direction == "down" and y < 580:
                            y += GRID_SIZE
                        elif direction == "left" and x > 90:
                            x -= GRID_SIZE
                        elif direction == "right" and x < 670:
                            x += GRID_SIZE
                        print(game_grid)
                        grid_x, grid_y = (x - 100) // GRID_SIZE, y // GRID_SIZE
                        if game_grid[grid_y][grid_x] == "used":
                            print([player_code],"loss at",[index])
                            client_socket.sendall(f"{player_code},loss".encode('utf-8'))
                        else:
                            player_positions[player_code]=(x,y)
                            game_grid[grid_current_y][grid_current_x] = "used"
                        
                        #below code for check wether the grid point is used
                        '''
                        #game_grid[grid_y_current_manual][grid_y_current_manual] = "used"

                        # Check if the grid cell is used
                        
                        if game_grid[grid_y][grid_x] == "used":
                            client_socket.sendall(f"{player_code},loss".encode('utf-8'))
                            #break  # Exit the loop, ending the game for this player

                        game_grid[grid_y][grid_x] = "used"
                        print("change direction at",game_grid[grid_y][grid_x])
                        
                        with lock:
                            new_place[player_code] = (x,y)
                            player_positions[player_code] = (x, y)
                        delta_x = new_place[player_code][0] - old_place[player_code][0]
                        delta_y = new_place[player_code][1] - old_place[player_code][1]
                        with lock:
                            delta_place[player_code] = (delta_x, delta_y)
                        '''
                    except socket.timeout:
                        #below code for auto move
                        '''
                        #print("No data received after 0.1 seconds, moving on...")
                        for player_code in PLAYER_CODES:

                            x0,y0 = player_positions[player_code]
                            # Before processing the auto move, free up their current position
                            #grid_x_current, grid_y_current = (x0 - 100) // GRID_SIZE, y0 // GRID_SIZE
                            #game_grid[grid_y_current][grid_x_current] = "unused"

                            delta_x,delta_y = delta_place[player_code]
                            x1 = x0 + delta_x*SPEED
                            y1 = y0 + delta_y*SPEED
                            with lock:
                                player_positions[player_code] = (x1,y1)

                            # After moving the player, mark their new position as used
                            #game_grid[grid_y_current][grid_x_current] = "used"

                            #print(x1,x0,y1,y0)
                            if (delta_x !=0 or delta_y != 0):
                                #print('not startimg point colliding')
                                grid_x_delta, grid_y_delta = (x1 - 100) // GRID_SIZE, y1 // GRID_SIZE
                                if game_grid[grid_y_delta][grid_x_delta] == "used":
                                    print('collided')
                                    client_socket.sendall(f"{player_code},loss".encode('utf-8'))
                                    print("loss send at",game_grid[grid_y_delta][grid_x_delta],(x1-100),y1)
                                    #break  # Exit the loop, ending the game for this player
                                else:
                                    game_grid[grid_y_delta][grid_x_delta] = "used"
                        '''
                    positions = ','.join([f"{code}:{x}-{y}" for code, (x, y) in player_positions.items()])
                    client_socket.sendall(positions.encode('utf-8'))


if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server started on {SERVER_IP}:{SERVER_PORT}, waiting for connections...")

    # Use a Manager to create shared data structures
    with Manager() as manager:
        game_grid = manager.list([["unused" for _ in range(GRID_COUNT)] for _ in range(GRID_COUNT)])
        player_positions = manager.dict({code: (0, 0) for code in PLAYER_CODES})
        old_place = manager.dict({code: (0, 0) for code in PLAYER_CODES})
        new_place = manager.dict({code: (0, 0) for code in PLAYER_CODES})
        delta_place = manager.dict({code: (0, 0) for code in PLAYER_CODES})
        #Some shared objects
        allocated_codes = manager.list()
        shared_Char = manager.Value('0', INIT)#send and receive message between process
        lock = Lock()

        processes = []
        monitor_process = Process(target=monitor_clients, args=(allocated_codes,lock,shared_Char))
        monitor_process.start()
        for _ in range(4):  # Create 4 processes to handle 4 players
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            
            p = Process(target=handle_client, args=(client_socket, game_grid, player_positions,allocated_codes,lock,_,shared_Char,old_place,new_place,delta_place))
            p.start()
            processes.append(p)
        while True:
            print(allocated_codes)
        for p in processes:
            p.join()
