import socket
import threading
import pygame

# Configuration du client
HOST = '127.0.0.1'
PORT = 55555

# Initialisation de Pygame
pygame.init()

# Dimensions de l'écran
largeur, hauteur = 750, 600
taille_carré = 50

# Couleurs
blanc = (255, 255, 255)
bleu = (0, 0, 255)
rouge = (255, 0, 0)
vert = (0, 255, 0)

# Positions initiales des joueurs
joueur1_x, joueur1_y = largeur // 4, hauteur // 2
joueur2_x, joueur2_y = largeur // 2, hauteur // 2
joueur3_x, joueur3_y = 3 * largeur // 4, hauteur // 2

# Vitesse de déplacement des joueurs
vitesse = 0.1

# Créer un socket client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Création de la fenêtre
ecran = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Jeu à 3 Joueurs")

# Fonction pour envoyer les mouvements
def send_move(dx, dy):
    message = f"MOVE {dx} {dy}"
    try:
        client.send(message.encode('utf-8'))
    except socket.error as e:
        print(f"Erreur lors de l'envoi du message : {e}")

# Fonction pour recevoir les positions des joueurs
def receive_positions():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message.startswith('POS'):
                parts = message.split()
                if len(parts) == 7:
                    _, x1, y1, x2, y2, x3, y3 = map(float, parts[1:])
                    joueur1_x, joueur1_y, joueur2_x, joueur2_y, joueur3_x, joueur3_y = x1, y1, x2, y2, x3, y3
        except socket.error as e:
            print(f"Une erreur est survenue lors de la réception : {e}")
            client.close()
            break

# Lancer le thread de réception des positions
receive_thread = threading.Thread(target=receive_positions)
receive_thread.start()

# Boucle de jeu
en_cours = True
while en_cours:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            en_cours = False

    # Gestion des mouvements
    touches = pygame.key.get_pressed()
    dx, dy = 0, 0

    if touches[pygame.K_LEFT]:
        dx -= vitesse
    if touches[pygame.K_RIGHT]:
        dx += vitesse
    if touches[pygame.K_UP]:
        dy -= vitesse
    if touches[pygame.K_DOWN]:
        dy += vitesse

    # Envoi des mouvements au serveur
    try:
        send_move(dx, dy)
    except socket.error as e:
        print(f"Erreur lors de l'envoi du message : {e}")

    # Dessin des joueurs
    ecran.fill(blanc)
    pygame.draw.rect(ecran, bleu, (joueur1_x, joueur1_y, taille_carré, taille_carré))
    pygame.draw.rect(ecran, rouge, (joueur2_x, joueur2_y, taille_carré, taille_carré))
    pygame.draw.rect(ecran, vert, (joueur3_x, joueur3_y, taille_carré, taille_carré))
    pygame.display.update()

# Quitter Pygame
pygame.quit()
client.close()
