import socket
import pygame
from pygame.locals import *

# Initialisation du client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 12345))  # Remplacez par l'adresse IP et le port du serveur

# Initialisation de Pygame
pygame.init()
screen_width, screen_height = 700, 650
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

PLAYER1_COLOR = (255, 0, 0)  # Rouge
PLAYER2_COLOR = (0, 0, 255)  # Bleu

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

#quit 
quit_game = False 

def quit():
    global quit_game
    quit_game = True
    client.send(b'quit') 
    
startGame = False
while startGame == False:
    screen.fill(BLACK)
    font = pygame.font.Font('freesansbold.ttf', 60)
    font2 = pygame.font.Font('freesansbold.ttf', 36)
    startLabel = font.render('Tron Game - CreaTech', 1, (WHITE))
    label2 = font2.render('Press SHIFT to start!', 1, (WHITE))
    quit_label = font2.render('Press Q to quit', 1, (WHITE))

    for event in pygame.event.get():
        if event.type == QUIT:  # Gestion de la fermeture de la fenêtre
            quit()
        keyState = pygame.key.get_pressed()
        if keyState[pygame.K_RSHIFT] or keyState[pygame.K_LSHIFT]:
            startGame = True
        if keyState[pygame.K_q]:
            quit()  # Appel de la fonction de sortie

    screen.blit(startLabel, (65, 225))
    screen.blit(label2, (170, 450))
    screen.blit(quit_label, (200, 500))
    pygame.display.flip()
   



player_color = PLAYER1_COLOR  

# Position initiale du carré contrôlé par le client
x, y = 200, 200

# Taille du carré
square_size = 50

# Boucle principale du jeu
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    # Gestion des mouvements du carré par les touches fléchées
    keys = pygame.key.get_pressed()
    if keys[K_LEFT]:
        x -= 5
    if keys[K_RIGHT]:
        x += 5
    if keys[K_UP]:
        y -= 5
    if keys[K_DOWN]:
        y += 5

    # Limiter les coordonnées pour éviter le clipping
    x = max(0, min(x, screen_width - square_size))
    y = max(0, min(y, screen_height - square_size))

    # Dessiner le carré
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, player_color, (x, y, square_size, square_size))

    # Envoyer la position du carré au serveur
    client.send(f"{x},{y}".encode())

    # Recevoir les positions de l'autre carré depuis le serveur
    data = client.recv(1024)
    if data:
        other_x, other_y = map(int, data.decode().split(','))
        # Dessiner l'autre carré
        pygame.draw.rect(screen, WHITE, (other_x, other_y, square_size, square_size))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
client.close()

# En fin de partie, vous pouvez également appeler la fonction quit() pour quitter proprement
quit()
