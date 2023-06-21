# coding: utf8
import unittest
import sys
sys.path.append("..")
from carte import Carte

class CarteTest(unittest.TestCase):
    """Test cases utilisés pour tester les fonctions du module carte (qui contient la classe Carte.
    Ces tests vérifient la constitution d'un labyrinthe standard et la création d'un labyrinthe depuis une chaîne"""
   
    def test_constitution_labyrinthe_ok(self):
        """Test le fonctionnement de la méthode verifier_constitution_labyrinthe de la classe Carte dans le module carte"""

        carte_ok = 'OOOO\nO  U\nOOOO'                       # Carte correcte
        # La constitution d'un labyrinthe se fait en instantiant un objet de la la ckasse Carte. Le labyrinthe lui-même est
        # un attribut de l'objet, appelé labyrinthe (un dico)
        carte_courante = Carte("carte_ok", carte_ok)
        self.assertNotEqual(carte_courante.labyrinthe, {})  # Si la carte est correcte,le divco labyrinthe est non vide

    def test_constitution_labyrinthe_0_sorties(self):
        """Carte KO: 0 sorties"""

        carte_ko_0_sorties = 'OOOO\nO  O\nOOOO'             # Carte incorrecte
        carte_courante = Carte("carte_ko_0_sorties", carte_ko_0_sorties)
        self.assertEqual(carte_courante.labyrinthe, {})     # Si la carte est incorrecte,le dico labyrinthe est vide

    def test_constitution_labyrinthe_2_sorties(self):
        """Carte KO: 2 sorties"""

        carte_ko_2_sorties ='OOOO\nO  U\nOOUO'
        carte_courante = Carte("carte_ko_2_sorties", carte_ko_2_sorties)
        self.assertEqual(carte_courante.labyrinthe, {})     # Si la carte est incorrecte,le dico labyrinthe est vide
 
    def test_constitution_labyrinthe_bord_trou(self):
        """Carte KO: bordure avec trou"""

        carte_ko_bord_avec_trou = 'OOOO\nO  U\nOO O'
        carte_courante = Carte("carte_ko_bord_avec_trou", carte_ko_bord_avec_trou)
        self.assertEqual(carte_courante.labyrinthe, {})     # Si la carte est incorrecte,le dico labyrinthe est vide

if __name__ == '__main__':
    unittest.main()