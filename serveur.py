# -*-coding:Utf-8 -*

"""roboc un jeu de robot dans un labyrithe qui se joue au claivier de la console."""

import os
import fonctions
from carte import Carte
import select

hote = ''
port = 12800
nb_min_de_clients = 2   # Nombre minimum de clients nécessaires pour démarrer une partie
nb_max_de_clients = 4   # Nombre maximum de clients acceptés pour démarrer une partie
DEBUG = False

# On charge les cartes existantes, pour chaque carte on instancie un objet de classe Carte et on l'ajoute à la liste 
# cartes[]
cartes = []     # Liste d'objets de classe Carte. Chaque élément de la liste sera un objet de classe Carte qui 
                # contient un attribut labyrinthe (de type dictionnaire) qui représente le labyrinthe. 
                # Cf la docstring de la classe Carte
for nom_fichier in os.listdir("cartes"):
    if nom_fichier.endswith(".txt"):
        chemin = os.path.join("cartes", nom_fichier)
        nom_carte = nom_fichier[:-3].lower()    # On retire le txt à la fin
        with open(chemin, "r") as fichier:
            contenu = fichier.read()
            fichier.close()
            # Pour chaque fichier carte, on crée une instance de la classe Carte, avec des attributs:
            #  -le nom de la carte
            #  -le labyrinthe, sous forme d'un dictionnaire avec clé = (x, y) et valeur = "O" ou " " ou "." ou U" ou "X"
            #  -un dico qui contiendra la position de chaque robot (x, y), indexé par le nom de socket (le tuple 
            #   (IP, port) de chaque client)
            carte_courante =  Carte(nom_carte[:-1], contenu)    # On retire le . à la fin
            # Si la méthode creer_labyrinthe_depuis_chaine de la classe Carte n'a pas été capable
            # de créer un labyrinthe (problème dans le fichier source), on sort:
            if carte_courante.labyrinthe == {}:
                print('La carte {} est incorrecte, vérifiez le fichier'.format(nom_carte[:-1]))
                exit()
            # Cet objet de type Carte est ajouté à la liste des cartes:
            cartes.append(carte_courante)

# On affiche les cartes existantes
print("Labyrinthes existants :")
for i, carte in enumerate(cartes):
    print("  {0} - {1}.".format(i + 1, carte.nom))

touches_permises = ""   
# On construit une chaine représentant les touches permises, c.à.d. les index de la liste cartes
for i in range(len(cartes)):
    touches_permises += str(i+1)
print("")
print("Entrez un numéro de labyrinthe pour commencer à jouer : ", end="")
touche = fonctions.frappe_clavier(touches_permises, "Choisissez un des labyrinthes proposés: [" + touches_permises + "]")
print("")

# On charge l'objet carte_en_cours
carte_en_cours = cartes[int(touche) - 1]

# On vérifie le nombre maximum de joeurs que ce labyrinthe peur accueillir (par exemple le "mini" peut en prendre 2 au max)
nb_max_places_dans_labyrinthe = carte_en_cours.nb_max_places_dans_labyrinthe()

# On ajuste le nb max de clients au nombre max de places disponibles pour des robots dans le labyrinte:
if nb_max_places_dans_labyrinthe < nb_max_de_clients:
    nb_max_de_clients = nb_max_places_dans_labyrinthe

# On lance le serveur:
connexion_principale = fonctions.lance_serveur(hote, port)

partie_commencee= False
clients_connectes = []
infos_connexions = []

while not partie_commencee:
    # Conditions pour démarrer une partie:
    #    -le nombre de clients est entre nb_min_de_clients et nb_max_de_clients    -et-
    #    -un des clients à demandé à commencer la partie (commande 'c')
    # On vérifie à chaque boucle que de nouveaux clients ne demandent pas à se connecter
    # On écoute la connexion principale en lecture, uniquement si on n'a pas encore atteint le nb max de clients,
    # on attend 1s:
    if len(clients_connectes) < nb_max_de_clients:     # On peut encore accepter des clients supplémentaires
        connexions_demandees, wlist, xlist = select.select([connexion_principale], [], [], 1.00)
        if DEBUG: print("connexions_demandees", connexions_demandees)

        for connexion in connexions_demandees:
            connexion_avec_client, info_connexion = connexion.accept()     # On accepte la connexion
            print("Nouveau client connecté : {}".format(info_connexion))
            # On ajoute le socket connecté à la liste des clients
            clients_connectes.append(connexion_avec_client)
            if DEBUG: print("clients_connectes =", clients_connectes)
            fonctions.envoie_message(clients_connectes, "Il y a {} joueurs connectés.\n".format(len(clients_connectes)))
            if len(clients_connectes) >= nb_min_de_clients:     # Si la partie peut commencer, on le propose à tous
                fonctions.envoie_message(clients_connectes, "Appuyez sur c pour commencer.")    

    if DEBUG: print("Liste des clients connectés", clients_connectes)
    if DEBUG: print("Liste des infos sur les connexions", infos_connexions)

    # Dès qu'on atteint le nombre minimum de clients connectés, on regarde si un client veut commencer.
    if len(clients_connectes) >= nb_min_de_clients:
        # On check si un des clients connectés veut lancer la partie:
        if fonctions.client_veut_commencer(clients_connectes):
            partie_commencee = True

# La partie peut commencer:
#    positionner aléatoirement le robot de chaque joueur dans le labyrinthe
#    carte_en_cours.labyrinthe[(x,y)] = (tuple identifiant client)
#    carte_en_cours.robots[(tuple identifiant client)] = (x, y)
# Parcourir la liste des clients, en les identifiant par leur tuple (IP, port local):
for client in clients_connectes:
    identifiant_client = client.getpeername()
    # Trouver aléatoirement une case libre dans la carte:
    (x, y) = fonctions.trouve_case_libre(carte_en_cours)
    # Si le tuple renvoyé est (0, 0) c'est qu'il n'y a pas de case libre pour mettre le robot, on
    # ne peut pas jouer, on atrrête tout:
    if (x, y) == (0, 0):
        print("Erreur: il n'a pas été possible de trouver une case libre pour mettre tous les robots")
        print('Choisissez un labyrinthe plus grand ou bien diminuez le nombre de joueurs')
        fonctions.envoie_message(clients_connectes, "Deconnexion")
        exit()
    else: 
        # Écrire dans le dico robots de la carte, à la clé de la case libre, l'identifiant du client:
        carte_en_cours.robots[(x,y)] = identifiant_client

# La partie commence !
fonctions.envoie_message(clients_connectes, "La partie commence!")
fonctions.envoie_message(clients_connectes, "Version multijoueurs : le but du jeu est d'ammener son robot (représenté par un X majuscule à la sortie du labyrinthe (représentée par un U majuscule).")
fonctions.envoie_message(clients_connectes, "L'ordinateur permet à chaque joueur de déplacer son robot d'une case à chaque tour, ou bien d'effectuer une action comme m (poser un mur) ou p (percer une porte).")
fonctions.envoie_message(clients_connectes, "Comme un joueur peut donner un ordre de déplacement multiple (par exemple e5 = se déplacer 5 fois vers l'Est), il est possible que l'ordinateur invite l'autre joueur à jouer plusieurs fois de suite, tant que le nomnbre de déplacements demandés par le premier joueus n'a pas été effectué.")
fonctions.envoie_message(clients_connectes, "Entrez une commande de direction nord est sud ouest [neso] suivie d'un facteur multiplicatif optionnel entre 1 et 9, ou\nEntrez une commande mur ou porte [mp] suivie d'une direction [neso], ou\nEntrez c pour commencer (si la partie n'est pas commencée)")

# Envoyer le labyrinthe à tous les joueurs. Avec pickle.dumps on transforme l'objet carte en data string, pour pouvoir
# l'envoyer au client. Le client utilsie pickle.loads pour faire l'opération inverse
fonctions.envoie_carte(clients_connectes, carte_en_cours)

# Boucle principale:
# On stocke pour chaque client la pile des commandes à traiter (car chaque client peut envoyer des commandes multiples).
# On utilise un dico qui a comme clé la socket du client (pris dans la liste clients_connectes) et comme valeur une
# liste qui contient la "pile" des commandes à traiter pour chaque client. Par exemple:
# commandes_a_traiter[<socket du client1] = [commande1, commande2] 
# commandes_a_traiter[<socket du client2] = [commande1, commande2, commande3]
# commandes_a_traiter[<socket du client3] = []
# Pour chaque client:
#    -regarder s'il n'y a pas une commande à traiter dans la pile de commandes à traiter:
#        -s'il y a une commande à traiter: 
#            -la sortir de la pile avec pop puis la traiter
#            -si le robot du client a atteint la sortie, la partie est terminée, envoyer message à tous, sortir de la boucle
#            -sinon, renvoyer le labyrinthe modifié à tous
#        -s'il n'y a pas de commande à traiter: envoyer message "à votre tour" au client, attendre la réponse:
#            -si la réponse est une commmande simple: la traiter, renvoyer le labyrinthe modifié à tous
#            -si la réponse est une commande multiple: l'énumérer en n commandes simples identiques, les placer dans la
#             pile du joueur, traiter une commande simple (pop), renvoyer le labyrinthe modifié à tous
#
# Initialisation du dico des commandes à traiter:
commandes_a_traiter = {}
for client in clients_connectes:
    commandes_a_traiter[client] = []

partie_en_cours = True
while partie_en_cours:
    for client in clients_connectes:
        if DEBUG: print("commandes_a_traiter = ", commandes_a_traiter)
        # Récupérer les infos de connection de ce client (source_IP, source_port):
        infos_client = client.getpeername()
        if DEBUG: print("infos_client = ", infos_client)
        commande_valide = False
        while not commande_valide:        
            if len(commandes_a_traiter[client]) != 0:           # Liste des commandes non vide pour ce client
                commande = commandes_a_traiter[client].pop()
            else:                                               # Pas de commande en pile, demander au joueur de jouer
                fonctions.envoie_message([client], "À votre tour")
                commande = client.recv(1024).decode()
                if DEBUG: print("commande = ", commande)
                # Si commande multiple, l'énumérer en n commandes simples et les placer dans la pile:
                if len(commande) == 2 and commande[1] in "123456789":
                    repetition = int(commande[1])
                    for i in range(repetition):
                        commandes_a_traiter[client].append(commande[0])
                    # 'poper' une commande de lapile:
                    commande = commandes_a_traiter[client].pop()
            # Trouver la position du robot de ce client, dans le dico robots de la carte:
            for position, infos in carte_en_cours.robots.items():
                if infos == infos_client: position_robot = position
            # Traitement des cas "mur" et "porte": la position du robot ne change pas mais une case du labyrinthe est
            # modifiée:
            if commande[0] in "mp":
                if fonctions.porte_et_mur(carte_en_cours, commande, position_robot, client):
                    commande_valide = True
                else:
                    commande_valide = False
                    continue
            elif commande[0] == "c":
                fonctions.envoie_message([client], "La partie est déjà commencée")
                commande_valide = False
                continue
            else:       # Commande de movement de robot ordinaire
                # Déterminer la nouvelle position du robot de ce client:
                nouvelle_position = fonctions.nouvelle_position(position_robot, commande, carte_en_cours)
                # Si la nouvelle position est la même que l'ancienne c'est que le robot ne pouvait se mouvoir (mur),
                # la commande dans la pile ne pouvait pas être traitée, il faut donc effacer toutes les commandes
                # restantes de la pile (qui seront nécessairement impossibles aussi) et demander au joueur de rejouer:
                if nouvelle_position == position_robot:
                    commandes_a_traiter[client].clear()
                    fonctions.envoie_message([client], "Mouvement impossible : à votre tour")
                    commande_valide = False
                    continue
                else:   # Le mouvement était possible
                    commande_valide = True
                # Effacer l'ancienne position du robot dans le labyrinthe:
                del carte_en_cours.robots[position_robot]
                # Écrire la nouvelle position du robot dans le labyrinthe:
                carte_en_cours.robots[nouvelle_position] = infos_client
                if carte_en_cours.labyrinthe[nouvelle_position] == "U":     # Yes!
                    # Partie terminée, envoyer msg à tous, sortir de la boucle
                    fonctions.envoie_message([client], "\n********************\n* Vous avez gagné! *\n********************")
                    fonctions.envoie_message(clients_connectes, "La partie est terminée!")
                    partie_en_cours = False
            # Puis renvoyer le labyrinthe modifié à tous:
            fonctions.envoie_carte(clients_connectes, carte_en_cours)
        if not partie_en_cours: break       # Si la partie est finie, inutile de continuer la boucle des clients
    
fonctions.envoie_message(clients_connectes, "Merci d'avoir joué.")
fonctions.envoie_message(clients_connectes, "Deconnexion")

# Fermeture des connections:
#for client in clients_connectes:
#    client.close()