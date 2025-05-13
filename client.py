import socket
import threading
import rsa  

nickname = input("Choisissez votre pseudonyme : ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("192.168.1.35", 4455))


#Réception de la clé publique du serveur
server_pub_pem = client.recv(2048)
server_pub = rsa.PublicKey.load_pkcs1(server_pub_pem)

#Génération de la paire RSA du client et envoi de la clé publique
my_pub, my_priv = rsa.newkeys(2048)
client.send(my_pub.save_pkcs1())

#Envoi du pseudonyme (chiffré)
client.send(rsa.encrypt(nickname.encode('utf-8'), server_pub))

#Réponse du serveur
response_enc = client.recv(1024)
response = rsa.decrypt(response_enc, my_priv).decode('utf-8')
if response == "PSEUDO_PRIS":
    print("Ce pseudonyme est déjà pris. Veuillez relancer le client et en choisir un autre.")
    client.close()
    exit()
elif response == "PSEUDO_OK":
    print(f"Bienvenue, {nickname} !")

#Fonctions d’envoi / réception 
def envoi_messages(env):
    while True:
        message = input("")
        env.send(rsa.encrypt(message.encode('utf-8'), server_pub))
        if message == "/quit":
            print("Déconnexion...")
            env.close()
            break

def reception_messages(env):
    while True:
        try:
            data = env.recv(1024)
            if not data:
                break
            plain = rsa.decrypt(data, my_priv).decode('utf-8')
            print(plain)
        except:
            break

threading.Thread(target=envoi_messages, args=(client,)).start()
threading.Thread(target=reception_messages, args=(client,)).start()
