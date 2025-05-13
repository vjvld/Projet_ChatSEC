import socket
import threading
import rsa   

#Clé RSA du serveur 
server_pub, server_priv = rsa.newkeys(2048)

#Dictionnaire pour stocker les sockets
clients = {}
nicknames = []

def manage_connection(client, addr):
    print(f"Connexion de {addr}")

    #Envoi de la clé publique du serveur
    client.send(server_pub.save_pkcs1())

    try:
        #Réception de la clé publique du client
        client_pub_pem = client.recv(2048)
        client_pub = rsa.PublicKey.load_pkcs1(client_pub_pem)

        #Réception du pseudonyme (chiffré avec la clé du serveur)
        enc_nick = client.recv(1024)
        nickname = rsa.decrypt(enc_nick, server_priv).decode('utf-8')

        if nickname in nicknames:
            client.send(rsa.encrypt("PSEUDO_PRIS".encode('utf-8'), client_pub))
            enlever_client(client)
            return
        else:
            nicknames.append(nickname)
            clients[client] = (addr, nickname, client_pub)
            print(f"Pseudonyme de {addr} : {nickname}")
            diffusion(f"{nickname} a rejoint le chat !".encode('utf-8'))
            client.send(rsa.encrypt("PSEUDO_OK".encode('utf-8'), client_pub))
    except Exception:
        enlever_client(client)
        return

    #Boucle de réception des messages
    while True:
        try:
            enc_msg = client.recv(1024)
            if not enc_msg:
                break
            message = rsa.decrypt(enc_msg, server_priv).decode('utf-8')
            if message == "/quit":
                break
            diffusion(f"{nickname} : {message}".encode('utf-8'), client)
        except:
            break

    enlever_client(client)
    print(f"Déconnexion de {addr}")
    diffusion(f"{nickname} a quitté le chat.".encode('utf-8'))
    client.close()

def diffusion(message: bytes, sender=None):
    for client, (addr, nick, pub) in list(clients.items()):
        if client != sender:
            try:
                client.send(rsa.encrypt(message, pub))
            except:
                enlever_client(client)

def enlever_client(client):
    if client in clients:
        addr, nickname, _ = clients[client]
        del clients[client]
        if nickname in nicknames:
            nicknames.remove(nickname)

# Configuration du serveur 
host = "192.168.1.35"
port = 4455
serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.bind((host, port))
serveur.listen()

print(f"Serveur en écoute sur {host}:{port}")

while True:
    client, addr = serveur.accept()
    threading.Thread(target=manage_connection, args=(client, addr)).start()
