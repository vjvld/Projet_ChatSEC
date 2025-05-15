import socket
import threading
import rsa  
import tkinter as tk
from tkinter import scrolledtext

#Connexion au serveur
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("192.168.1.168", 4455))

#Réception de la clé publique du serveur
server_pub_pem = client.recv(2048)
server_pub = rsa.PublicKey.load_pkcs1(server_pub_pem)

#Génération de la paire RSA du client et envoi de la clé publique
my_pub, my_priv = rsa.newkeys(2048)
client.send(my_pub.save_pkcs1())

pseudonyme = None

#Fonction pour envoyer des messages
def envoi_messages():
    message = zoneMessageEnv.get()
    if message :
        #Affichage du message dans la zone de texte
        zoneMessageRecu.config(state=tk.NORMAL)
        zoneMessageRecu.insert(tk.END, f"Vous : {message}\n")
        zoneMessageRecu.config(state=tk.DISABLED)
        zoneMessageRecu.see(tk.END)

        #Envoi du message au serveur
        client.send(rsa.encrypt(message.encode('utf-8'), server_pub))
        if message == "/quit":
            print("Déconnexion...")
            client.close()
            interface.quit()
        else:
            zoneMessageEnv.delete(0, tk.END)

#Fonction pour recevoir les messages
def reception_messages():
    while True:
        try:
            data = client.recv(1024)
            if not data:
                break
            plain = rsa.decrypt(data, my_priv).decode('utf-8')
            zoneMessageRecu.config(state=tk.NORMAL)
            zoneMessageRecu.insert(tk.END, plain + "\n")
            zoneMessageRecu.config(state=tk.DISABLED)
            zoneMessageRecu.see(tk.END)
        except:
            break

#Fonction pour se connecter
def connexion():
    global pseudonyme
    pseudonyme = pseudonymeEnv.get()
    if pseudonyme:
        client.send(rsa.encrypt(pseudonyme.encode('utf-8'), server_pub))
        response_enc = client.recv(1024)
        response = rsa.decrypt(response_enc, my_priv).decode('utf-8')
        print(response)
        if response == "PSEUDO_PRIS":
            infoLabel.config(text="Ce pseudonyme est déjà pris. Veuillez en choisir un autre.", fg="red")
            pseudonymeEnv.delete(0, tk.END)
            pseudonyme = None
        elif response == "PSEUDO_OK":
            #Change la page pour afficher la zone de discussion
            pseudonymeEnv.pack_forget()
            boutonConnexion.pack_forget()
            infoLabel.pack_forget()
            afficher_zone_chat()
            #Affichage d'un message de bienvenue
            zoneMessageRecu.config(state=tk.NORMAL)
            zoneMessageRecu.insert(tk.END, f"Vous êtes connecté(e) en tant que : {pseudonyme}\n")
            zoneMessageRecu.config(state=tk.DISABLED)
            zoneMessageRecu.see(tk.END)
            
#Fonction pour afficher la zone de discussion
def afficher_zone_chat():
    zoneMessageRecu.pack(padx=10, pady=10)
    zoneMessageEnv.pack(side=tk.LEFT, padx=10, pady=10)
    boutonEnv.pack(side=tk.RIGHT, padx=10, pady=10)
    threading.Thread(target=reception_messages, daemon=True).start()

#Création de la fenêtre principale
interface = tk.Tk()
interface.title("CHATSEC") #Nom de la fenêtre
interface.geometry("600x400")  #Taille de la fenêtre
interface.resizable(False, False)  #Empêche le redimensionnement

#Outils de connexion
infoLabel = tk.Label(interface, text="Entrez votre pseudonyme :")
infoLabel.pack(pady=10)
pseudonymeEnv = tk.Entry(interface, width=30)
pseudonymeEnv.pack(pady=5)
boutonConnexion = tk.Button(interface, text="Valider", command=connexion)
boutonConnexion.pack(pady=10)

#Outils de discussion
zoneMessageRecu = scrolledtext.ScrolledText(interface, state=tk.DISABLED, wrap=tk.WORD, width=50, height=20)
zoneMessageEnv = tk.Entry(interface, width=40)
boutonEnv = tk.Button(interface, text="Envoyer", command=envoi_messages)

interface.mainloop()