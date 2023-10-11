import socket
import random
import time
import multiprocessing

# some stable values
SERVER_IP = "127.0.0.1"
SERVER_PORT = 6859
ALLOWED_USERNAMES = ["1111", "2222", "3333", "4444"]
LOGIN_SUC = "login_success"
LOGIN_FAIL = "login_fail"
PLAYER_CODES = ["A", "B", "C", "D"]
GAME_START = "game_start"
SPEED = 1

GRID_SIZE = 1
GAME_AREA_SIZE = 600
GRID_COUNT = GAME_AREA_SIZE // GRID_SIZE

# position and grid
game_grid = [["unused" for _ in range(GRID_COUNT)] for _ in range(GRID_COUNT)]
player_positions = {code: (0, 0) for code in PLAYER_CODES}
old_place = {code: (0, 0) for code in PLAYER_CODES}
new_place = {code: (0, 0) for code in PLAYER_CODES}
delta_place = {code: (0, 0) for code in PLAYER_CODES}

# user names
available_codes = list(set(PLAYER_CODES))
lossers = set()
allocated_codes = set()

def user_login(server_socket, process_index,shared_data):
    allocated_codes = shared_data
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")
    print(f"process alive:", process_index)
    data = client_socket.recv(1024).decode('utf-8')
    if data in ALLOWED_USERNAMES:
        client_socket.sendall(LOGIN_SUC.encode('utf-8'))
        data = client_socket.recv(1024).decode('utf-8')
        print(f"repport from", process_index, data)
        if data == "need_user_code":
            available_codes = list(set(PLAYER_CODES) - allocated_codes)
            if available_codes:
                assigned_code = random.choice(available_codes)
                allocated_codes.add(assigned_code)
                client_socket.sendall(assigned_code.encode('utf-8'))
                data = client_socket.recv(1024).decode('utf-8')
                if data == "get_user_code":
                    res = (assigned_code, "given")
                    print(res)

if __name__ == '__main__':
    #make a list could share between processes
    manager = multiprocessing.Manager()
    shared_data = manager.list(allocated_codes)

    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the IP and port
    server_socket.bind((SERVER_IP, SERVER_PORT))

    # Listen for incoming connections
    server_socket.listen(5)
    print(f"Server started on {SERVER_IP}:{SERVER_PORT}, waiting for connections...")

    count = 10
    while True:
        # Accept a new connection
        process1 = multiprocessing.Process(target=user_login, args=(server_socket, 1,shared_data))
        process2 = multiprocessing.Process(target=user_login, args=(server_socket, 2,shared_data))
        process3 = multiprocessing.Process(target=user_login, args=(server_socket, 3,shared_data))
        process4 = multiprocessing.Process(target=user_login, args=(server_socket, 4,shared_data))

        # start process
        process1.start()
        process2.start()
        process3.start()
        process4.start()

        if (len(allocated_codes) > 1):  # more than one user here
            count = count - 1
        time.sleep(1)
        print(f"will start at",count)
        if (count < 1):
            break

    print("Main process done")
