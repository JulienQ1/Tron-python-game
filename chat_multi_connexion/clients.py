import socket
import threading
import tkinter as tk
from tkinter.simpledialog import askstring
from tkinter import messagebox

# Configuration du client
HOST = '127.0.0.1'
PORT = 55555

# Fonction pour envoyer un message depuis l'interface graphique
def send_message(event=None):
    message = message_entry.get()
    if message:
        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, f"{username}: {message}\n")
        chat_log.config(state=tk.DISABLED)
        message_entry.delete(0, tk.END)
        client.send(f"{username}: {message}".encode('utf-8'))

# Fonction pour quitter la conversation
def quit_chat():
    client.send("Quitter le chat".encode('utf-8'))
    client.close()
    chat_window.quit()
    chat_window.destroy()
    messagebox.showinfo("Information", "Vous avez quitté la conversation.")

# Fonction pour afficher les messages reçus dans l'interface graphique
def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            chat_log.config(state=tk.NORMAL)
            chat_log.insert(tk.END, message + '\n')
            chat_log.config(state=tk.DISABLED)
        except:
            print("Une erreur est survenue. Déconnexion.")
            client.close()
            chat_window.quit()
            chat_window.destroy()
            break

# Demander le nom d'utilisateur via une boîte de dialogue
root = tk.Tk()
root.withdraw()
username = askstring("Nom d'utilisateur", "Choisissez un nom d'utilisateur :")

if username:
    # Configuration de l'interface graphique du chat
    chat_window = tk.Toplevel()
    chat_window.title(f"Chat Client - {username}")

    chat_log = tk.Text(chat_window, state=tk.DISABLED)
    chat_log.pack()

    message_entry = tk.Entry(chat_window)
    message_entry.pack(fill=tk.BOTH, expand=True)
    message_entry.bind("<Return>", send_message)

    send_button = tk.Button(chat_window, text="Envoyer", command=send_message)
    send_button.pack()

    quit_button = tk.Button(chat_window, text="Quitter", command=quit_chat)
    quit_button.pack()

    # Se connecter au serveur
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    # Envoyer le nom d'utilisateur au serveur
    client.send(username.encode('utf-8'))

    # Lancer le thread de réception
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    chat_window.protocol("WM_DELETE_WINDOW", quit_chat)

    chat_window.mainloop()
else:
    print("Nom d'utilisateur non spécifié. Fermeture du client.")
