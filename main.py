import socket
import threading

# Sélection du mode souhaité
selection = input("Bonjour ! Etes-vous l'hôte (1) ou le client (2) ? ")

# Mode serveur
if selection == "1":
    # Création du socket et association de l'adresse IP
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.bind(("192.168.1.111", 4455))
    serveur.listen()

    # Attente de la connexion du client
    client, addr = serveur.accept()
    print("Connexion de", addr)

# Mode client
elif selection == "2":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("192.168.1.111", 4455))
else:
    exit()

# Fonction d'envoi des messages
def envoi_messages(env):
    while True:
        message = input("")
        if message == "/quit":  # Si le message est /quit, fermer la connexion
            print("Déconnexion...")
            env.close()  # Fermer la connexion
            break
        env.send(message.encode())  # Envoi du message
        print("Vous :", message)

# Fonction de réception des messages
def reception_messages(env):
    while True:
        try:
            data = env.recv(1024)  # Récupération du message
            if not data:  # Si la connexion est fermée, sortir
                break
            print("Collègue :", data.decode())  # Affichage du message
        except:
            break  # Si une erreur se produit, sortir

# Lancement des threads pour l'envoi et la réception des messages
threading.Thread(target=envoi_messages, args=(client,)).start()
threading.Thread(target=reception_messages, args=(client,)).start()
