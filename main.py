import socket
import threading
import rsa

public_key, private_key = rsa.newkeys(1024)
public_collegue = None


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
    client.send(public_key.save_pkcs1("PEM"))
    public_collegue = rsa.PublicKey.load_pkcs1(client.recv(1024))

    print("Connexion de", addr)


# Mode client
elif selection == "2":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("192.168.1.111", 4455))
    client.send(public_key.save_pkcs1("PEM"))
    public_collegue = rsa.PublicKey.load_pkcs1(client.recv(1024))
else:
    exit()

# Fonction d'envoi des messages
def envoi_messages(env):
    while True:
        message = input("")
        env.send(rsa.encrypt(message.encode(), public_collegue))  # Envoi du message
        if message == "/quit":  # Si le message est /quit, fermer la connexion
            print("Déconnexion...")
            env.close()  # Fermer la connexion
            break
        print("Vous :", message)

# Fonction de réception des messages
def reception_messages(env):
    while True:
        try:
            data = rsa.decrypt(env.recv(1024), private_key).decode()  # Récup du message
            if not data:  # Si la connexion est fermée, sortir
                break
        except:
            break  # Si une erreur se produit, sortir
        print("Collègue : ", data)

# Lancement des threads pour l'envoi et la réception des messages
threading.Thread(target=envoi_messages, args=(client,)).start()
threading.Thread(target=reception_messages, args=(client,)).start()
