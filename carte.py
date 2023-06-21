# -*-coding:Utf-8 -*

"""Ce module contient la classe Carte."""

class Carte:

    """Objet qui contient le nom de la carte, la carte sous forme de dictionnaire (la clé étant un tuple (x, y),
    la valeur étant le contenu d'une case) et la position courante du robot (x, y).
    L'objet contient aussi un attribut tuple robot qui repésente la position du robot.
    L'objet contient aussi un attribut dictionnaire robots qui contient les position de tous les robots des joueurs
    L'objet contient aussi une méthode qui permet de lire le fichier carte et de le transformer
    en dictionnaire."""

    def __init__(self, nom, chaine):
        self.nom = nom
        self.nb_colonnes = 0    # Attribut pour mémoriser le nombre de colonnes (pour affichage ultérieur)
        self.nb_lignes = 0      # Attribut pour mémoriser le nombre de lignes (pour affichage ultérieur)
        self.robot = (0, 0)     # Position du robot en (x, y)
        self.robots = {}        # Ce dico contiendra les positions des robots (de tous les joueurs)
                                #   clé = position du robot du joueur (x, y)
                                #   valeur = le socket du joueur, (l'IP, port local client)
        self.labyrinthe = self.creer_labyrinthe_depuis_chaine(chaine)

    def creer_labyrinthe_depuis_chaine(self, chaine):
        """ Lire la chaine (contenu) ligne par ligne puis caractère par caractère, et créer un dictionnaire
        qui représente le labyrinthe sous forme d'un dictionnaire avec clé = (x, y) et valeur = "O" ou " " ou "."
         ou U" ou " "
        L'origine (x, y) = (0, 0) est le coin en haut et à gauche de la carte"""

        x = 0   # x = numéro de colonne
        y = 0   # y = numéro de ligne
        labyrinthe = {}
      
        liste = chaine.split(sep="\n")      # On tokenise la chaine en une liste, avec une ligne par élément
        self.nb_colonnes = len(liste[0])    # Le 1er élément contient autant de caractères que de colonnes
                                            # (le labyrinthe est rectangulaire)
        for ligne in liste:
            x = 0   # Nouvelle ligne, on remet donc le numéro de colone à 0
            for char in ligne:
                labyrinthe[(x, y)] = char
                x += 1  # Caractère suivant
            y += 1  # Ligne suivante
            self.nb_lignes += 1
        if self.verifier_constitution_labyrinthe(labyrinthe):
            return labyrinthe
        else:
            print("La carte {} est incorrecte. Vérifiez qu'il n'y a qu'une sortie et que tous les bords ont un mur.".format(self.nom))
            return {}       # On renvoie un dico labyrinthe vide
    
    def verifier_constitution_labyrinthe(self, labyrinthe):
        """Cette méthode vérifie que le labyrinthe qu'on vient de constituer à partir de la chaine
        est correct, c'est à dire:
        -il doit pouvoir contenir au moins 2 robots (avoir 2 cases libres en plus des bords), donc
         le produit (colonnes -2) * (lignes -2) >= 2
        -tous les bords ont soit un 'O' soit un 'U' unique (pas de blancs)
        -une et une seule seule sortie 'U'"""
        if (self.nb_colonnes - 2) * (self.nb_lignes -1) <2:
            return False
        # Constitution d'une chaine qui contient les bords horizontaux du haut et du bas:
        bords_horizontaux = ''
        for col in range(self.nb_colonnes):                 # Bord horizontal du haut
            bords_horizontaux += labyrinthe[(col, 0)]
        for col in range(self.nb_colonnes):                 # Bord horizontal du bas
            bords_horizontaux += labyrinthe[(col, self.nb_lignes - 1)]
        # Constitution d'une chaine qui contient les bords verticaux de gauche et de droite:
        bords_verticaux = ''
        for ligne in range(self.nb_lignes):                 # Bord vertical de gauche
            bords_verticaux += labyrinthe[(0, ligne)]
        for ligne in range(self.nb_lignes):                 # Bord vertical de droite
            bords_verticaux += labyrinthe[(self.nb_colonnes -1, ligne)]
        bords = bords_horizontaux + bords_verticaux
        # Dans cette chaine il ne doit pas y avoir de blancs, les seuls caractères permis sont 'O' et
        # 'U', ce dernier ne doit être présent qu'une seule fois:
        for char in bords:
            if char != 'O' and char != 'U':
                return False
        if bords.count('U') != 1:
                return False
        return True
    
    def nb_max_places_dans_labyrinthe(self):
        """Cette méthode compte le nombre de cases libres, ce qui dicte le nombre maximum de joueurs"""
        max_places = 0
        for cle in self.labyrinthe:
            if self.labyrinthe[cle] == " ":
                max_places += 1
        return max_places

    def __repr__(self):
        return "<Carte {}>".format(self.nom)
