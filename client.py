import socket
import threading
import rsa  
import tkinter as tk
from tkinter import scrolledtext, PhotoImage

#Connexion au serveur
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("192.168.56.1", 4455))

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
    connexionFrame.place_forget()  #Cache la page de connexion
    frame_chat.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    zoneMessageRecu.pack(padx=10, pady=(10, 5), fill=tk.BOTH, expand=True)
    zoneMessageEnv.pack(side=tk.LEFT, padx=(10, 5), pady=(0, 10), fill=tk.X, expand=True)
    boutonEnv.pack(side=tk.RIGHT, padx=(5, 10), pady=(0, 10))
    threading.Thread(target=reception_messages, daemon=True).start()

#Fonction pour changer la couleur du bouton quand la souris passe dessus	   
def sourisParDessusBouton(bouton):
    bouton['background'] = '#00adb5'
    bouton['foreground'] = '#222831'
def sourisNonSurBouton(bouton):
    bouton['background'] = '#222831'
    bouton['foreground'] = '#eeeeee'

#Création de la fenêtre principale
interface = tk.Tk()
interface.title("CHATSEC") #Nom de la fenêtre
interface.geometry("600x400")  #Taille de la fenêtre
interface.resizable(False, False)  #Empêche le redimensionnement
interface.configure(bg="#222831") #Couleur du background
interface.bind("<Escape>", lambda event: interface.quit()) #Pour quitter avec Echap

#Page de connexion
connexionFrame = tk.Frame(interface, bg="#393e46", bd=2, relief=tk.RIDGE, padx=10, pady=10)
connexionFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

logo_img = PhotoImage(file="logo.png") 
logoLabel = tk.Label(connexionFrame, image=logo_img, bg="#393e46")
logoLabel.pack(pady=(10, 0))

titreLabel = tk.Label(connexionFrame, text="CHATSEC", font=("Arial", 35, "bold"), fg="#00adb5", bg="#393e46")
titreLabel.pack(pady=(10, 10))

infoLabel = tk.Label(connexionFrame, text="Entrez votre pseudonyme :", font=("Arial", 12), bg="#393e46", fg="#eeeeee")
infoLabel.pack(pady=5)

pseudonymeEnv = tk.Entry(connexionFrame, width=30, font=("Arial", 12))
pseudonymeEnv.pack(pady=5)
pseudonymeEnv.bind("<Return>", lambda event: connexion())

boutonConnexion = tk.Button(connexionFrame, text="Valider", command=connexion, font=("Arial", 12, "bold"), bg="#222831", fg="#eeeeee", activebackground="#00adb5", activeforeground="#222831", bd=0)
boutonConnexion.pack(pady=(10, 20))
boutonConnexion.bind("<Enter>", lambda e: sourisParDessusBouton(boutonConnexion))
boutonConnexion.bind("<Leave>", lambda e: sourisNonSurBouton(boutonConnexion))

#Page de discussion
frame_chat = tk.Frame(interface, bg="#393e46", bd=2, relief=tk.RIDGE, padx=10, pady=10)

zoneMessageRecu = scrolledtext.ScrolledText(frame_chat, state=tk.DISABLED, wrap=tk.WORD, width=50, height=15, font=("Arial", 11), bg="#222831", fg="#eeeeee", bd=0)
zoneMessageEnv = tk.Entry(frame_chat, width=50, font=("Arial", 12), bg="#222831", fg="#eeeeee", bd=0, insertbackground="#eeeeee")
zoneMessageEnv.bind("<Return>", lambda event: envoi_messages())

boutonEnv = tk.Button(frame_chat, text="➤", command=envoi_messages, font=("Arial", 12, "bold"), bg="#222831", fg="#eeeeee", bd=0, activebackground="#00adb5", activeforeground="#222831")

boutonEnv.bind("<Enter>", lambda e: sourisParDessusBouton(boutonEnv))
boutonEnv.bind("<Leave>", lambda e: sourisNonSurBouton(boutonEnv))

interface.mainloop()