# coding: utf8
import unittest
import sys
sys.path.append("..")
import socket
import fonctions
import select
import warnings

hote = 'localhost'
port = 12800
wlist = []
xlist = []

class MutliJoueurTest(unittest.TestCase):
    """Test cases utilisés pour tester les fonctions mutli-joueurs.
    Note: l'intelligence du code étant dans les scripts serveur.py et client.py, qui utilisent
          très peu de fonctions du module fonctions.py, je ne vois pas comment tester le code
          autremenbt qu'en le recopiant dans ce script de test, ce qui va à l'encontre de l'objectif
          des test unitaires.... En fait je ne vois pas vraiment comment utiliser les tests unitaires
          pour tester les fonctions multi-joueurs réseau, désolé."""

    def test_lancement_serveur(self):
        """On lance un serveur, puis on vérifie qu'il écoute bien sur le port désigné""" 
        connexion_principale = fonctions.lance_serveur(hote, port)
        # Le port de la socket doit être celui demandé:
        self.assertEqual(connexion_principale.getsockname()[1], port)
        
    def test_connexion_client_ok(self):
        """Test d'une connexion réussie"""
        connexion_principale = fonctions.lance_serveur(hote, port)  # @UnusedVariable
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning) # To avoid "ResourceWarning: unclosed socket.socket"
        connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            connexion_avec_serveur.connect((hote, port))
        except socket.error:
            self.assertRaises(socket.error)
        else:  # pas d'erreur
            self.assertTrue(True)

    def test_connexion_client_ko(self):
        """Test d'une connexion ratée (mauvais numéro de port)"""
        connexion_principale = fonctions.lance_serveur(hote, port)  # @UnusedVariable
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning) # To avoid "ResourceWarning: unclosed socket.socket"
        connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connexion ratée (mauvais port):
        self.assertRaises(ConnectionRefusedError, connexion_avec_serveur.connect, (hote, port+1))
    
    def test_serveur_2_clients(self):
        """Test vu du serveur, qui voit que 2 clients sont bien connectés"""
        clients_connectes = []
        i = 0
        connexion_principale = fonctions.lance_serveur(hote, port)
        # Le client se connecte 2 fois
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning) # To avoid "ResourceWarning: unclosed socket.socket"        
        connexion1_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connexion1_avec_serveur.connect((hote, port))
        connexion2_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connexion2_avec_serveur.connect((hote, port))
        # Le serveur accepte les 2 clients:
        connexions_demandees, wlist, xlist = select.select([connexion_principale], [], [], 1.00)  # @UnusedVariable
        while i <2:
            for connexion in connexions_demandees:
                connexion_avec_client = connexion.accept()     # On accepte la connexion
                # On ajoute le socket connecté à la liste des clients
                clients_connectes.append(connexion_avec_client)
            i += 1
        self.assertEqual(len(clients_connectes), 2) # Il y a bien 2 clients connectés
        
if __name__ == '__main__':
    unittest.main()