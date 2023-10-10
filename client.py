import pygame
import socket
import time #to count and control the time of a loop

SERVER_IP = "127.0.0.1" #The IP of the server
SERVER_PORT = 6859 #The port used of server
CLIENT_IP = "127.0.0.1" #The IP of client
CLIENT_PORT = 6859 #The port used by client
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


#init pygame and give a window
pygame.init()
screen = pygame.display.set_mode((800, 600))

#import some resources
player_images = {
    "A": pygame.image.load("MA.png").convert_alpha(),
    "B": pygame.image.load("MB.png").convert_alpha(),
    "C": pygame.image.load("MC.png").convert_alpha(),
    "D": pygame.image.load("MD.png").convert_alpha()
}


#to define some figure

def login_screen(screen, font):
    username = ''
    screen_width, screen_height = screen.get_size()  # 获取屏幕尺寸

    # 渲染 "Please enter the user name:" 文本
    prompt_text_surface = font.render('Please enter the user name:', True, (255, 255, 255))
    prompt_text_width, prompt_text_height = prompt_text_surface.get_size()  # 获取文本尺寸

    # 计算文本和输入框的位置以居中它们
    prompt_text_position_x = (screen_width - prompt_text_width) / 2
    prompt_text_position_y = (screen_height / 2) - prompt_text_height - 10

    input_box_width = 200  # 可以根据您的需求进行调整
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

        # 绘制文本和输入框
        screen.blit(prompt_text_surface, (prompt_text_position_x, prompt_text_position_y))

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
    try:
        # Receive player code from server
        player_code = connection.recv(1024).decode('utf-8')

        # Check if the player code is valid
        if player_code in ['A', 'B', 'C', 'D']:
            return player_code
        else:
            print(f"Unexpected player code received: {player_code}")
            return None
    except Exception as e:
        print(f"Error while receiving player code: {e}")
        return None


# 定义一个函数来绘制待机界面
def draw_waiting_screen(player_code):
    screen.fill((0, 0, 0))  # 用黑色填充屏幕

    # 在左下角显示玩家代号
    font_small = pygame.font.Font(None, 32)
    player_text = font_small.render(f"Player: {player_code}", True, (255, 255, 255))
    screen.blit(player_text, (10, 560))  # 稍微离左边界和底部10像素

    # 在画面正中显示“Waiting for other user”
    font_large = pygame.font.Font(None, 48)
    waiting_text = font_large.render("Waiting for other user", True, (255, 255, 255))
    text_rect = waiting_text.get_rect(center=(400, 300))  # 居中定位
    screen.blit(waiting_text, text_rect)

    # 在右下角显示玩家图片
    if player_code in player_images:
        player_img = pygame.transform.scale(player_images[player_code], (80, 40))
        screen.blit(player_img, (720, 560))  # 从右边界和底部边界10像素的位置开始

    pygame.display.flip()  # 更新显示内容



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

      # Assuming this is your screen size
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
    # 监听事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    # 从服务器获取数据
    data = client_socket.recv(1024).decode('utf-8')

    if data == START:
        print("Game will start")
        break
    else:
        draw_waiting_screen(player_code)
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
client_socket.close()