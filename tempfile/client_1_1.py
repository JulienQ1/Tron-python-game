import pygame
import socket
import time #to count and control the time of a loop

SERVER_IP = "127.0.0.1"#input("Please enter a server address (127.0.0.1 for test in computer)")
SERVER_PORT = 6868#int(input("Please enter a server port"))

CHAT_SERVER_HOST = '127.0.0.1'
CHAT_SERVER_PORT = 55555

SINGAL_END = "/END"
SINGAL_REQUEST ="SIG_RE"
SINGAL_SEND = "SIG_SE"
SINGAL_GET = "SIG_SEN"

LOGIN_SUC = "login_success" #The message given by server that means username is right
LOGIN_FAIL = "login_fail"
FPS = 60 #how many loops every second
USER_NUMBER = 4
START = "game_start" #start signal provide by server
STOP = "game_stop"#stop signal provide by server
USER_NUMBER = 0 #Get usernumber from server
USER_RAMIN = 0 #Get how many user ramin from server
USER_KILLED = False #To check wether user is killed
USER_KILLED_OTHER = False# To check wether other user is killed


#dictation used to store previous posision of users
previous_positions = {"A": None, "B": None, "C": None, "D": None}

#different colors of line the users use
player_colors = {
    "A": (255, 0, 0),  # Red
    "B": (255, 255, 0),  # Yellow
    "C": (0, 0, 255),  # Blue
    "D": (0, 255, 0)  # Green
}

#init pygame and give a window
pygame.init()
screen = pygame.display.set_mode((800, 600))

#import some resources
player_images = {
    "A": pygame.image.load("MAM.png").convert_alpha(),
    "B": pygame.image.load("MBM.png").convert_alpha(),
    "C": pygame.image.load("MCM.png").convert_alpha(),
    "D": pygame.image.load("MDM.png").convert_alpha()
}
player_images_little = {
    "A": pygame.image.load("MAL.png").convert_alpha(),
    "B": pygame.image.load("MBL.png").convert_alpha(),
    "C": pygame.image.load("MCL.png").convert_alpha(),
    "D": pygame.image.load("MDL.png").convert_alpha()
}


#to define some figure

def login_screen(screen, font, bg_image_path="background.jpg", button_image_path="login_button.png"):
    username = ''
    screen_width, screen_height = screen.get_size()

    # Load the background image
    background = pygame.image.load(bg_image_path)
    background = pygame.transform.scale(background, (screen_width, screen_height))

    # Load the login button image
    button = pygame.image.load(button_image_path)
    button_width, button_height = button.get_size()

    # Define button position
    button_x = (screen_width - button_width) / 2
    button_y = screen_height / 2 + 50  # 50 pixels below the input box

    prompt_text_surface = font.render('Please enter the user name:', True, (255, 255, 255))
    prompt_text_width, prompt_text_height = prompt_text_surface.get_size()
    prompt_text_position_x = (screen_width - prompt_text_width) / 2
    prompt_text_position_y = (screen_height / 2) - prompt_text_height - 10

    input_box_width = 200
    input_box_height = 32
    input_box_x = (screen_width - input_box_width) / 2
    input_box_y = screen_height / 2
    input_box = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)

    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    running = True

    while running:
        screen.fill((0, 0, 0))

        # Draw the background image
        screen.blit(background, (0, 0))
        
        screen.blit(prompt_text_surface, (prompt_text_position_x, prompt_text_position_y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
                
                # Check for login button press
                if button_x <= event.pos[0] <= button_x + button_width and button_y <= event.pos[1] <= button_y + button_height:
                    return username

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return username
                    elif event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    else:
                        username += event.unicode

        txt_surface = font.render(username, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        
        # Draw the button
        screen.blit(button, (button_x, button_y))

        pygame.display.flip()

    pygame.quit()

def login(user_nam,connection):#a function to get username and compare with the server
    # send user_name to server
    connection.sendall(user_nam.encode('utf-8'))
        
    # get response from server
    data = connection.recv(1024).decode('utf-8')
        
    if data == LOGIN_SUC:
        print("success")
        return "suc"
    elif data == LOGIN_FAIL:
        print("fail")
        return "fail"
    else:
        print("Unexpected server response")
        return "error"
    
def get_player_code(connection):
    """
    Get the player code (A, B, C, or D) from the server.

    """
    # Receive player code from server
    try:
        # Receive player code from server
        client_socket.sendall("need_user_code".encode('utf-8'))
        player_code = connection.recv(1024).decode('utf-8')

        print(player_code)

        # Check if the player code is valid
        if player_code in ['A', 'B', 'C', 'D']:
            client_socket.sendall("get_user_code".encode('utf-8'))
            return player_code
        else:
            print(f"Unexpected player code received: {player_code}")
            return None
    except Exception as e:
        print(f"Error while receiving player code: {e}")
        return None


# define a function to draw the waiting screen
def draw_waiting_screen(screen,player_code,waiting_background_path = "waiting_background.jpg" ):
    screen_width, screen_height = screen.get_size()
    
    screen.fill((0, 0, 0))  # fill the screen with black
    background = pygame.image.load(waiting_background_path)
    background = pygame.transform.scale(background, (screen_width, screen_height))
    screen.blit(background, (0, 0))

    # display the user code on left down
    font_small = pygame.font.Font(None, 32)
    player_text = font_small.render(f"Player: {player_code}", True, (255, 255, 255))
    screen.blit(player_text, (10, 560))  # away from left and botton to 10 pixel

    # print “Waiting for other user” in middle
    font_large = pygame.font.Font(None, 48)
    waiting_text = font_large.render("Waiting for other user", True, (255, 255, 255))
    text_rect = waiting_text.get_rect(center=(400, 300))  # locat in center
    screen.blit(waiting_text, text_rect)

    # draw user image in right down side
    if player_code in player_images:

        player_img = player_images[player_code]

        screen.blit(player_img, (720, 560))  # start from 10px right and botton

    pygame.display.flip()  # renew the screen

#define a function to get the userinput, and send to server
def send_movement_to_server(direction, connection):
    try:
        connection.sendall(direction.encode('utf-8'))
    except Exception as e:
        print("Error sending movement:", e)

#define a function to get the position of 4 users from server
def get_player_positions_from_server(connection):
    try:
        data = data = connection.recv(10240).decode('utf-8').split(SINGAL_END)[0]
        print(data)
        # Check if the received data is a loss message
        if ",loss" in data:
            return data
        
        player_positions = {}
        players_data = data.split(',')
        for player_data in players_data:
            code, coords = player_data.split(':')
            x, y = map(int, coords.split('-'))
            player_positions[code] = (x, y)
        return player_positions
    except Exception as e:
        print("Error receiving player positions:", e)
        return None


#send user's action to server
def send_player_action_to_server(client_socket, player_code):
    for event in pygame.event.get():
        direction = None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                direction = "up"
            elif event.key == pygame.K_DOWN:
                direction = "down"
            elif event.key == pygame.K_LEFT:
                direction = "left"
            elif event.key == pygame.K_RIGHT:
                direction = "right"
            
        if direction:
            message = f"{player_code},{direction}"
            client_socket.send(message.encode('utf-8'))




#login procedure
print("Welcom to our game")



#define the font of text
font = pygame.font.Font(None, 36)
text_surface = font.render('Please input your username:', True, (255, 255, 255))

# make an object of socket,and connect
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (SERVER_IP, SERVER_PORT)
client_socket.connect(server_address)



while True:
    font = pygame.font.Font(None, 36)  # Assuming this is your font

    username = login_screen(screen, font)
    if username:
        print(f"Logged in with username: {username}")
    else:
        print("User closed the login screen.")

    #init the input
    result = login(username,client_socket)
    # if login successfully, go to main loop, else stay here
    if result == "suc":
        break
    elif result == "error":
        print("sever is out")   
    else:
        print("User name not right, try again")

#wait for the game to start

player_code = get_player_code(client_socket)
if not player_code:
    player_code = "Unknown"


while True:
    # listening the event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    # get data from server
    data = client_socket.recv(1024).decode('utf-8')

    if data == START:
        print("Game will start")
        break
    else:
        draw_waiting_screen(screen,player_code)
        time.sleep(1)


#main loop below

# print a gray platform in the middle of screen
center_x = (screen.get_width() - 600) // 2
center_y = (screen.get_height() - 600) // 2
pygame.draw.rect(screen, (128, 128, 128), (center_x, center_y, 600, 600))

# make a new Surface to draw the trace
trail_surface = pygame.Surface(screen.get_size())
trail_surface.set_colorkey((0, 0, 0))  # set the clolr to transparrent
trail_surface.fill((0, 0, 0))

loss_notification = None  # Store any loss notification for other players
player_lost = False  # Flag to track if the current player lost
data_end = ""

# main loop

while True:
    start_time = time.time()
    screen.fill((0, 0, 0))  # clean the screen

    # show grey in middle
    center_x = (screen.get_width() - 600) // 2
    center_y = (screen.get_height() - 600) // 2
    pygame.draw.rect(screen, (128, 128, 128), (center_x, center_y, 600, 600))

    # renew the trace on trail_surface
    #player_positions = get_player_positions_from_server(client_socket)
    getted_data = get_player_positions_from_server(client_socket)
    #print(getted_data)
    if ",loss" in getted_data:
        data_end = getted_data
    else:
        player_positions = getted_data
    if player_positions:
        for player_code_drawing, (x, y) in player_positions.items():
            # Draw a line between the previous position and current position
            if previous_positions[player_code_drawing]:
                prev_x, prev_y = previous_positions[player_code_drawing]
                pygame.draw.line(trail_surface, player_colors[player_code_drawing], (prev_x + 20, prev_y + 10), (x + 20, y + 10), 2)
            previous_positions[player_code_drawing] = (x, y)  # update the previous position

    # draw trail_surface to main screen
    screen.blit(trail_surface, (0, 0))

    # draw user's image on main screen, (only position, not trace)
    for player_code_drawing, (x, y) in player_positions.items():
        if player_code_drawing in player_images_little:

            player_img = player_images_little[player_code_drawing]

            screen.blit(player_img, (x, y))
    
    # show user code left down
    font = pygame.font.SysFont(None, 36)
    if player_code in player_positions.keys():
        label = font.render(username, True, (255, 255, 255))
        screen.blit(label, (10, screen.get_height() - label.get_height() - 10))
    
    # show user image right down
    if player_code in player_positions.keys():
        if player_code in player_images:
            
            player_img = player_images[player_code]

            screen.blit(player_img, (screen.get_width() - 110, screen.get_height() - 60))
    # 2. Handle "loss" message from server
    if ",loss" in data_end:
        loser_code = data_end.split(",")[0]
        if loser_code == player_code:
            player_lost = True
            break
        else:
            loss_notification = f"{loser_code} lost"

    # 3. Display the appropriate message or box based on the above

    # For other players' loss notification
    if loss_notification:
        font = pygame.font.SysFont(None, 36)
        label = font.render(loss_notification, True, (255, 0, 0))
        screen.blit(label, (screen.get_width() - label.get_width() - 10, 10))

    pygame.display.flip()  # renew the print


    send_player_action_to_server(client_socket, player_code)

    # keep loop run in FPS
    passed_time = time.time() - start_time
    target_duration = 1/FPS
    if passed_time < target_duration:
        time.sleep(target_duration-passed_time)

    data_end = client_socket.recv(1024).decode('utf-8')
    if data_end == STOP:
        break
while True:
    rect_width = 300
    rect_height = 100
    pygame.draw.rect(screen, (0, 0, 128), (screen.get_width() // 2 - rect_width // 2, screen.get_height() // 2 - rect_height // 2, rect_width, rect_height))
        
    font = pygame.font.SysFont(None, 36)
    label = font.render("You LOST", True, (255, 255, 255))
    screen.blit(label, (screen.get_width() // 2 - label.get_width() // 2, screen.get_height() // 2 - label.get_height() // 2))
    player_end = input("Game over , N to end")
    if player_end == "N":
        break
    else:
        time.sleep(1)
client_socket.close()
