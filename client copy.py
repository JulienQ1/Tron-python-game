import pygame
import socket
import time #to count and control the time of a loop

SERVER_IP = "127.0.0.1" #The IP of the server
SERVER_PORT = 0000 #The port used of server
CLIENT_IP = "127.0.0.1" #The IP of client
CLIENT_PORT = 0000 #The port used by client
LOGIN_SUC = "login_success" #The message given by server that means username is right
LOGIN_FAIL = "login_fail"
FPS = 60 #how many loops every second
USER_NUMBER = 4
START = "game_start" #start signal provide by server
STOP = "game_stop"#stop signal provide by server

#init pygame and give a window
#pygame.init()
#screen = pygame.display.set_mode((1024, 1024))

#define the font of text
#font = pygame.font.Font(None, 36)
#text_surface = font.render('Please input your username:', True, (255, 255, 255))

#init the input part
#username = ''
#input_box = pygame.Rect(250, 250, 140, 32)
#color_inactive = pygame.Color('lightskyblue3')
#color_active = pygame.Color('dodgerblue2')
#color = color_inactive
#active = False




# make an object of socket,and connect
#client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_address = (SERVER_IP, SERVER_PORT)
#client_socket.connect(server_address)

#login procedure
print("Welcom to our game")

#init pygame and give a window
pygame.init()

#define the font of text
font = pygame.font.Font(None, 36)
text_surface = font.render('Please input your username:', True, (255, 255, 255))

# make an object of socket,and connect
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (SERVER_IP, SERVER_PORT)
client_socket.connect(server_address)



while True:

    screen = pygame.display.set_mode((500, 500))  # Assuming this is your screen size
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


while True:
    # Getting data from server
    data = client_socket.recv(1024).decode('utf-8')
    
    if data == START:
        print("Game will start")
        break
    else:
        print("wait for other users")
        time.sleep(1)



#main loop below
while True:
    start_time = time.time() # Record the time of the loop start
    #put the main boday of our game below


    #below and first line for make sure loop FPS time every second.
    passed_time = time.time() - start_time
    target_dureation = 1/FPS
    if passed_time < target_dureation:
        time.sleep(target_dureation-passed_time)
    #give information that the game need to be optimized as it couldn't run according to FPS
    else:
        print("please optimise the game")
        break
    #Stop the game if server send a stop signal
    data_end = client_socket.recv(1024).decode('utf-8')
    if data_end == STOP:
        break



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
    
def login_screen(screen, font):
    username = ''
    input_box = pygame.Rect(250, 250, 140, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    running = True

    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None  # Return None if user closes the window
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return username  # Return the username if the user presses enter
                    elif event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    else:
                        username += event.unicode

        txt_surface = font.render(username, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()

    pygame.quit()

