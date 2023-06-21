# coding: utf8
"""module fonctions contenant les fonctions utiles au programme principal serveur.py"""
import pickle
import select
import random
import socket
wlist = []
xlist = []
i = 0
DEBUG = False

def lance_serveur(hote, port):
    # On lance le serveur:
    connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connexion_principale.bind((hote, port))
    connexion_principale.listen(5)
    if DEBUG: print("Le serveur écoute à présent sur le port {}".format(port))
    return connexion_principale


def afficher_labyrinthe(carte, identifiant_client):
    """Cette fonction affiche le labyrinthe (attribut de l'objet passé en paramètre)
    Note1: si on passe par la position d'une porte, telle que mémorisée dans l'attribut portes de l'objet carte,
    on affiche la porte. En effet la porte peut avoir été 'effacée' par le déplacement du robot.
    Note2: si le contenu d'une case est son propre identifiant_client, on affiche X (son propore robot),
    si le contenu d'une case est un autre identifiant_client, on affiche x (robot d'un autre joueur)"""
    if DEBUG: print("DEBUG: Entrée de la fonction aficher_labyrinthe ")
    for ligne in range(carte.nb_lignes):
        for colonne in range(carte.nb_colonnes):
            if (colonne, ligne) in carte.robots:    # S'il y a un des robots dans cette case
                if carte.robots[(colonne, ligne)] == identifiant_client:  # Et que c'est le robot du client (notre robot)
                    print("X", end='')
                else:        # Il y a un robot mais pas le notre
                    print("x", end='')
            else:
                print(carte.labyrinthe[(colonne, ligne)], end='')
        print("")   # Ligne suivante
    print("_" * 20) # Ligne séparatrice

def frappe_clavier(touches_permises, message_erreur):
    """Cette fonction récupère une commande saisie par le joueur et vérifie qu'elle fait bien partie des commandes
    permises.
    Si ce n'est pas la cas elle affiche un message d'erreur (passé en paramètre à la fonction"""
    
    touche = input("")
    touche = touche.lower()
    
    touche_pas_ok = False
    if len(touche) == 2:        # Cas d'une direction suivie d'un facteur de répétition, ex: e2, - ou-
                                # m<n|e|s|o> pour murer dans une direction, -ou-
                                # p<n|e|s|o> pour percer une porte dans une direction
        if touche[0] not in "nesomp" or touche[1] not in "123456789neso":
            touche_pas_ok = True
        if touche[1] not in "123456789neso":    # Le 2e caractère peut être un chiffre ou une direction (cas de m et p)
            touche_pas_ok = True
    elif len(touche) == 1:      # Cas d'une direction simple (E, S, O, N) ou C pour commencer
        if touche not in touches_permises:
            touche_pas_ok = True
    else:
        touche_pas_ok = True
    
    if not touche.isalnum() or touche_pas_ok:     # En cas d'erreur 
        print(message_erreur)
        # On appelle de nouveau la fonction pour avoir une autre touche
        return frappe_clavier(touches_permises, message_erreur)
    else:
        return touche
    
def nouvelle_position(robot, touche, carte):
    """La fonction nouvelle_position(robot) se charge des tests et renvoie la nouvelle position du robot en prenant en
    compte les contraintes (mur)"""
    
    # Traitement des commandes
    if touche[0] == "n":                                # Nord => on décrémente y
        nouvelle_position = (robot[0], robot[1]-1)
        # La nouvelle position pourrait sortir du labyrinthe (si on fait N et que le robot était tout en haut)
        # on vérifie donc que le nouveau tuple de position fait bien partie des tuples du labyrinthe, et s'il
        # n'en fait plus partie on ne change pas sa position
        # De même, on vérifie que nouvelle position ne soit pas celle d'un autre robot!
        if nouvelle_position not in carte.labyrinthe or \
        nouvelle_position in carte.robots or \
        carte.labyrinthe[nouvelle_position] == "O":     # On frappe un mur en allant au Nord
            return robot                                # On renvoie la position du robot inchangée
        # Validation de la nouvelle position
        if (carte.labyrinthe[nouvelle_position] == "U"):# On atteint la sortie en allant au Nord
            robot = nouvelle_position
            return robot
        else:                                           # Soit case vide soit "." soit U
            robot = nouvelle_position
        return robot
    elif touche[0] == "e":                              # Est => on incrémente x
        nouvelle_position = (robot[0]+1, robot[1])
        # La nouvelle position pourrait sortir du labyrinthe (si on fait E et que le robot était tout à droite)
        # on vérifie donc que le nouveau tuple de position fait bien partie des tuples du labyrinthe, et s'il
        # n'en fait plus partie on ne change pas sa position
        # De même, on vérifie que nouvelle position ne soit pas celle d'un autre robot!
        if nouvelle_position not in carte.labyrinthe or \
        nouvelle_position in carte.robots or \
        carte.labyrinthe[nouvelle_position] == "O":     # On frappe un mur en allant à l'Est
            return robot                                # On renvoie la position du robot inchangée
        # Validation de la nouvelle position
        if (carte.labyrinthe[nouvelle_position] == "U"):# On atteint la sortie en allant à l'Est
            robot = nouvelle_position
            return robot
        else:                                           # Soit case vide soit "." soit U
            robot = nouvelle_position
        return robot
    elif touche[0] == "s":                              # Sud => on incrémente y
        nouvelle_position = (robot[0], robot[1]+1)
        # La nouvelle position pourrait sortir du labyrinthe (si on fait S et que le robot était tout en bas)
        # on vérifie donc que le nouveau tuple de position fait bien partie des tuples du labyrinthe, et s'il
        # n'en fait plus partie on ne change pas sa position
        # De même, on vérifie que nouvelle position ne soit pas celle d'un autre robot!
        if nouvelle_position not in carte.labyrinthe or \
        nouvelle_position in carte.robots or \
        carte.labyrinthe[nouvelle_position] == "O":     # On frappe un mur en allant au Sud
            return robot                                # On renvoie la position du robot inchangée
        # Validation de la nouvelle position
        if (carte.labyrinthe[nouvelle_position] == "U"):# On atteint la sortie en allant au Sud
            robot = nouvelle_position
            return robot
        else:                                           # Soit case vide soit "." soit U
            robot = nouvelle_position
        return robot
    elif touche[0] == "o":                              # Ouest => on décrémente x
        nouvelle_position = (robot[0]-1, robot[1])
        # La nouvelle position pourrait sortir du labyrinthe (si on fait O et que le robot était tout à gauche)
        # on vérifie donc que le nouveau tuple de position fait bien partie des tuples du labyrinthe, et s'il
        # n'en fait plus partie on ne change pas sa position
        # De même, on vérifie que nouvelle position ne soit pas celle d'un autre robot!
        if nouvelle_position not in carte.labyrinthe or \
        nouvelle_position in carte.robots or \
        carte.labyrinthe[nouvelle_position] == "O":     # On frappe un mur en allant à l'Ouest
            return robot                                # On renvoie la position du robot inchangée
        # Validation de la nouvelle position
        if (carte.labyrinthe[nouvelle_position] == "U"):# On atteint la sortie en allant à l'Ouest
            robot = nouvelle_position
            return robot
        else:                                           # Soit case vide soit "." soit U
            robot = nouvelle_position
        return robot
    else:                                    # Ne devrait pas arriver, mais il faut que la fonction retourne qq chose 
        return robot

def porte_et_mur(carte, commande, position_robot, client):
    """Fonction de traitement des cas "mur" et "porte": la position du robot ne change pas mais une case du labyrinthe
    est modifiée.
    S'il n'est pas possible de positionner une porte ou un mur là où le joueur l'a demandé, la fonction renvoie False.
    Si c'est possible, la fonction positionne un "m" ou un "p" dans le labyrinthe.:"""
    dico = {"m":"O", "p":"."}     # Pour traduire m en "." et "p" en "O" sans if
    if len(commande) != 2:
        envoie_message([client], "Les commandes p ou m doivent êtres suivies d'une direction\n")
        return False        
    elif commande[1] == "n":    # Mettre un mur ou une porte au Nord de la position du robot
        # Vérifier position de porte ou mur ne sort pas du labyrinthe (si N alors que le robot est en haut)
        # De même, on vérifie que la position où mettre la porte/mur ne soit pas celle d'un autre robot!
        # Enfin ne dois pas être le "U" de sortie !
        if (position_robot[0], position_robot[1]-1) not in carte.labyrinthe or \
        (position_robot[0], position_robot[1]-1) in carte.robots or \
        carte.labyrinthe[(position_robot[0], position_robot[1]-1)] == "U":
            envoie_message([client], "Position de mur ou porte en dehors du labyrinthe ou sur au autre robot\n")
            return False
        else:
            carte.labyrinthe[(position_robot[0], position_robot[1]-1)] = dico[commande[0]]
            return True 
    elif commande[1] == "e":    # Mettre un mur ou une porte à l'Est de la position du robot
        # Vérifier position de porte ou mur ne sort pas du labyrinthe (si E alors que le robot est à droite)
        # De même, on vérifie que la position où mettre la porte/mur ne soit pas celle d'un autre robot!
        # Enfin ne dois pas être le "U" de sortie !
        if (position_robot[0]+1, position_robot[1]) not in carte.labyrinthe or \
        (position_robot[0]+1, position_robot[1]) in carte.robots or \
        carte.labyrinthe[(position_robot[0]+1, position_robot[1])] == "U":
            envoie_message([client], "Position de mur ou porte en dehors du labyrinthe ou sur au autre robot\n")
            return False
        else:
            carte.labyrinthe[(position_robot[0]+1, position_robot[1])] = dico[commande[0]]
            return True 
    elif commande[1] == "s":    # Mettre un mur ou une porte au Sud de la position du robot
        # Vérifier position de porte ou mur ne sort pas du labyrinthe (si S alors que le robot est en bas)
        # De même, on vérifie que la position où mettre la porte/mur ne soit pas celle d'un autre robot!
        # Enfin ne dois pas être le "U" de sortie !
        if (position_robot[0], position_robot[1]+1) not in carte.labyrinthe or \
        (position_robot[0], position_robot[1]+1) in carte.robots or \
        carte.labyrinthe[(position_robot[0], position_robot[1]+1)] == "U":
            envoie_message([client], "Position de mur ou porte en dehors du labyrinthe ou sur au autre robot\n")
            return False
        else:
            carte.labyrinthe[(position_robot[0], position_robot[1]+1)] = dico[commande[0]]
            return True 
    elif commande[1] == "o":    # Mettre un mur ou une porte à l'Ouest de la position du robot
        # Vérifier position de porte ou mur ne sort pas du labyrinthe (si O alors que le robot est à gauche)
        # De même, on vérifie que la position où mettre la porte/mur ne soit pas celle d'un autre robot!
        # Enfin ne dois pas être le "U" de sortie !
        if (position_robot[0]-1, position_robot[1]) not in carte.labyrinthe or \
        (position_robot[0]-1, position_robot[1]) in carte.robots or \
        carte.labyrinthe[(position_robot[0]-1, position_robot[1])] == "U":
            envoie_message([client], "Position de mur ou porte en dehors du labyrinthe ou sur au autre robot\n")
            return False
        else:
            carte.labyrinthe[(position_robot[0]-1, position_robot[1])] = dico[commande[0]]
            return True 

def client_veut_commencer(clients_connectes):
    """Fonction qui vérifie si un client a envoyé "c" pour commencer la partie
    Un select.select sur la liste des clienst connectés attend qu'un des clients envoie des donnée, avec un timeout
    de 1 seconde si aucun client n'envoie une donnée, auquel cas la fonction renvoie False
    Si un client a envoyé une donnée, un select.recv va lire cette donnée, et si c'est un 'c' renvoie True"""
    clients_a_lire = []
    if DEBUG: print("Début fonction client_veut_commencer")
    if DEBUG: print("fonction client_veut_commencer: clients_connectes = ", clients_connectes)
    try:
        clients_a_lire, wlist, xlist, = select.select(clients_connectes, [], [], 5.00)
        if DEBUG: print("fonction client_veut_commencer: clients_a_lire", clients_a_lire)
    except select.error:    # Erreur ou timeout atteint aucun client n'a envoyé qq chose
        if DEBUG: print("fonction client_veut_commencer: select.error")
        return False
        pass        # Est-ce nécessaire vu que la fonction renvoie False (donc , se finit) ?? tbc
    else:
        if DEBUG: print("fonction client_veut_commencer: clients_a_lire", clients_a_lire)
        for client in clients_a_lire:
            # Client est de type socket, on va lire 1024 caractères
            try:
                msg_recu = client.recv(1024)
                if DEBUG: print("fonction client_veut_commencer: msg_recu = ", msg_recu)
            except select.error:
                print("Erreur: le client n'est plus connecté.")
                return False
                continue    # On passe au client suivant                
            # Peut planter si le message contient des caractères spéciaux
            msg_recu = msg_recu.decode()
            if DEBUG: print("Dans fonction client_veut_commencer: msg_recu = ", msg_recu)
            if msg_recu[0] == 'c':
                return True

def envoie_message(clients_connectes, message):
    """Fonction qui envoie le même message à tous les clients connectés"""
    for client in clients_connectes:
        try:
            client.send(message.encode())
        except select.error:
            print("Erreur: le client n'est plus connecté.")
            continue    # On passe au client suivant
        # Pour régler des pbms de synchronisme, le client renvoir un 'ack' à chaque message reçu. Il faut le lre.
        ack = client.recv(1024).decode()
        if DEBUG: print("Dans fonction envoie_message: ack = ", ack)

def trouve_case_libre(carte):
    """Fonction qui va trouver aléatoirement une case libre dans la carte. Elle renvoie les coordonnées de cette case"""
    # On commence par construire une liste de cases vides, chaque élément de la liste est un tuple (x, y)
    liste_cases_vides = []
    for ligne in range(carte.nb_lignes):
        for colonne in range(carte.nb_colonnes):
            if (carte.labyrinthe[(colonne, ligne)]) == ' ':
                # La case est vide, ok, mais il y a peut-être déjà un robot dessus!
                if not (colonne, ligne) in carte.robots:    # pas de robot dans cette case
                    liste_cases_vides.append((colonne, ligne))
    # On choisit une case aléatoirement, si la liste des cases vides n'est pas vide (car si le
    # labyrinthe est très petit, il y a juste la place pour 2 robots par exemple):
    if liste_cases_vides:
        return liste_cases_vides[random.randint(0, len(liste_cases_vides)-1)]
    else:
        # S'il n'y a pas de case libre pour placer un robot, on ne peut pas jouer, on renvoie
        # arbitrairement le tuple (0, 0) qui est une position impossible pour un robot,
        # coin en haut à gauchje
        return (0, 0)

def envoie_carte(clients_connectes, carte):
    """Fonction qui envoie le labyrinthe à tous les joueurs. Avec pickle.dumps on transforme l'objet carte en 
    data string, pour pouvoir l'envoyer au client. Le client utilise pickle.loads pour faire l'opération inverse"""
    data_string = pickle.dumps(carte)   # Transformer l'objet carte en data_string:
    for client in clients_connectes:
        client.send(data_string)
        ack = client.recv(1024).decode()
        if DEBUG: print("ack = ", ack)
