# coding: utf8

import socket
import time
from threading import Thread
import fonctions
import pickle 

hote = "localhost"
port = 12800
DEBUG = False

connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connecte_au_serveur = False
while not connecte_au_serveur:
    try:
        connexion_avec_serveur.connect((hote, port))
    except socket.error:
        print("Le serveur a refusé la connexion, assurez-vous qu'il est démarré et est en attente")
        print("Temporisation 3s")
        time.sleep(3)
    else:
        print("Connexion établie avec le serveur sur le port de destination {}".format(port))
        # Le tuple (ip, port_source) permet de distinguer chaque client. Le serveur s'en sert pour identifier le
        # robot d'un client par rapport au robot d'un autre client. Dans le labyrinthe reçu, le client reconnaitra
        # ainsi son robot et l'affichera avec un X. Il affichera les autres robots avec un x.
        identifiant_client = connexion_avec_serveur.getsockname()     
        print("Votre identifiant est : {}".format(identifiant_client))
        # On passe en mode non bloquant sur le recv, pour ne pas bloquer le Thread 2 si le serveur n'envoie rien
        # Après 1 seconde le recv passe en exception si rien n'a été reçu du serveur
        connexion_avec_serveur.settimeout(1)
        connecte_au_serveur = True

global msg_a_envoyer
msg_a_envoyer = ""

# 1er Thread : va demander à l'humain d'entrer une commande
class Saisie_commande(Thread):
    """Thread chargé simplement de demander à l'humain d'entrer une commande"""
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        """Code à exécuter pendant l'exécution du Thread"""
        global msg_a_envoyer
        while True:
            if DEBUG: print("Thread 1 : Message à envoyer: ", msg_a_envoyer)
            touches_permises = "cnesomp123456789"
            touche = fonctions.frappe_clavier(touches_permises, "Entrez une commande de direction [neso] suivie d'un facteur multiplicatif optionnel entre 1 et 9, ou\nEntrez une commande mur ou porte [mp] suivie d'une direction [neso], ou\nEntrez c pour commencer (si la partie n'est pas commencée)")
###            touche = fonctions.frappe_clavier(touches_permises, "Entrez la commande c pour commencer, ou \nEntrez une commande de direction [neso] suivie d'un facteur multiplicatif optionnel entre 1 et 9, ou\nEntrez une commande mur ou porte [mp] suivie d'une direction [neso]")
            msg_a_envoyer = touche
        if DEBUG: print("Fin du Thread 1")

# 2eme thread: gère les communications avec le serveur, en permanence: 
class Envoi_commande(Thread):
    """Thread chargé d'écouter (recv) les messages du serveur et d'envoyer la commande en cours au serveur"""
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        """Code à exécuter pendant l'exécution du Thread"""
        # pour plus tard : on peut recevoir avec recv un stream avec des \n au milieu:
        # pour afficher ligne par ligne, usitliser split, e.g. 
        # for line in message.decode().split('\n'):
        #     print(line)
        
        global msg_a_envoyer
        if DEBUG: print("Thread 2 : Message à envoyer: ", msg_a_envoyer)
        msg_recu = b''
        while True:
            if DEBUG: print("Thread 2 (dans le while): Message à envoyer: ", msg_a_envoyer)
            # Envoyer des messages au serveur, si demmandé par le joueur (Thread 1):
            # Peut planter si on tape des caractère spéciaux
            # On envoie le message, s'il y a un message à envoyer, en l'encodant en bytes
            if msg_a_envoyer != "":
                if DEBUG: print("on va envoyer ", msg_a_envoyer)
                connexion_avec_serveur.send(msg_a_envoyer.encode())
                # Maintenant qu'on a envoyé le message on le remet à vide (ce sera le 1er thread qui va définir sa
                # prochaine valeur)
                msg_a_envoyer = ""

            # Puis écouter les messages du serveur et agir en fonction
            if DEBUG: print("Thread 2 en écoute du serveur")
            msg_recu_precedent = msg_recu
            try:
                msg_recu = connexion_avec_serveur.recv(16384)    # Attention la taille d'un labyrinthe peut être >1024
                ###print("DEBUG: msg_recu = ", msg_recu)
                # Aquittement du message au serveur: ( Pour régler des pbms de synchronisme)
                connexion_avec_serveur.send(b'ack')
            except socket.error:
                if DEBUG: print("Thread 2 - Rien reçu du serveur")
                pass
            else:
                # On a bien reçu un message (sinon on serait dans le except socket.error) et on essaie de le décoder 
                # Si c'est possible c'est que c'est un message texte, sinon c'est que c'est un labyrinthe envoyé sous
                # forme de data string (pickle.dumps):
                try:
                    msg_recu.decode()
                except UnicodeDecodeError:
                    if DEBUG: print(" section except UnicodeDecodeError")
                    if DEBUG: print("data_string = ", msg_recu)
                    carte = pickle.loads(msg_recu)
                    # Afficher le labyrinthe reçu, avec un X pour son propre robot et un x pour ceux des autres
                    fonctions.afficher_labyrinthe(carte, identifiant_client)
                    continue
                if msg_recu.decode() == "ping":
                    if DEBUG: print("ping reçu du serveur")
                elif msg_recu.decode() == "Appuyez sur c pour commencer.":
                    if msg_recu != msg_recu_precedent:  # Pour éviter d'imprimer sans cesse le même message
                        print(msg_recu.decode())
                        msg_recu_precedent = msg_recu
                elif msg_recu.decode() == "Deconnexion":
                    print("Deconnexion du serveur.")
                    connexion_avec_serveur.close()
                    break
                else:       # Autre type de message reçu
                    if msg_recu != msg_recu_precedent:  # Pour éviter d'imprimer sans cesse le même message
                        print(">{}".format(msg_recu.decode()))
                        msg_recu_precedent = msg_recu                   
        if DEBUG: print("Fin du Thread 2")
        
# Création des threads
thread_1 = Saisie_commande()
thread_2 = Envoi_commande()

# Lancement des threads
thread_1.start()
thread_2.start()

# On attend que les threads se terminent complètement
thread_1.join()
thread_2.join()
