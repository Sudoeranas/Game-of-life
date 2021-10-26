# DM07
# PG2 NSI
# Game Of Life

from pixmap import fenêtre, affiche, attend, quitte
import copy


### CONSTANTES :

# Dimensions de la fenêtre en pixels :
LARGEUR, HAUTEUR = 900, 700

# Nombre de cases :
NX, NY = 45, 35  # horizontal, vertical

# Couleurs des cellules:
DEAD = 0x000444 # mortes
LIVE = 0x0000ff # vivantes

###################################
# Fonctions à réaliser pour le DM #
###################################
def init_cell_mortes():
    """
    Renvoie une matrice de cellules mortes de dimensions (NX, NY).
    :return: (list) la matrice des cellules, toutes mortes.
    """
    j = 0
    
    list1=[]
    
    while(j<NY) :
        ligne = []
        i = 0
        while (i<NX):
            ligne.append(DEAD)
            i = i + 1
        list1.append(ligne)       
        j = j + 1
        
    
    return list1
    
    

def init_cell_vivantes(m):
    """
    Initialise les cellules vivantes dans la matrice m
    avec un Pentomino au milieu (NX//2, NY//2).
    :param m: (list) la matrice des cellules à modifier
    """
    i = NX//2
    j = NY//2
    m[j][i] = LIVE
    m[j+1][i-1] = LIVE
    m[j+1][i] = LIVE
    m[j+2][i] = LIVE
    m[j+2][i+1] = LIVE



def compte_voisines_vivantes(m, x, y):
    """
    Compte les cellules vivantes parmi les 8 voisines de
    cellule[y][x].
    :param m: (list) la matrice des cellules
    :param x: (int) abscisse de la cellule (0 <= x < NX)
    :param y: (int) ordonnée de la cellule (0 <= y < NY)
    """
    voisines = [] # liste des cellules voisines
    if x > 0:
        voisines.append(m[y][x-1])
    if y > 0:
        voisines.append(m[y-1][x])
    if x < NX-1:
        voisines.append(m[y][x+1])
    if y < NY-1:
        voisines.append(m[y+1][x])
    if x > 0 and y > 0:
        voisines.append(m[y-1][x-1])
    if x > 0 and y < NY-1:
        voisines.append(m[y+1][x-1])
    if x < NX-1 and y > 0:
        voisines.append(m[y-1][x+1])
    if x < NX-1 and y < NY-1:
        voisines.append(m[y+1][x+1])
    # la liste des cellules voisines est finie,
    # il n'y a plus qu'à compter lesquelles sont vivantes :
    i = 0
    somme = 0
    while (i<len(voisines)):
        if (voisines[i] == LIVE):
            somme = somme+1
        i = i + 1
    return somme

def nouvelle_étape(m):
    """
    Modifie la matrice des cellules m pour qu'elle contienne
    la nouvelle étape.
    :param m: (list) la liste des cellules
    :return: aucun
    """
    dup = copy.deepcopy(m)
    
    j = 0
    while (j<NY):
        i = 0
        while(i<NX):
            somme = compte_voisines_vivantes(dup, i, j)
            if (somme == 3):
                m[j][i] = LIVE
            if (somme == 2 ):
                if (dup[j][i] == LIVE):
                    m[j][i] = LIVE
                else :
                    m[j][i] == DEAD
            if (somme <2 or somme >3):
                m[j][i] = DEAD
            i = i+1
        j = j+1
    

###################################

# la matrice contenant les cellules :
cellules = init_cell_mortes()

# initialisation des cellules vivantes :
init_cell_vivantes(cellules)

fenêtre(LARGEUR, HAUTEUR, matrice=cellules, titre='Game Of Life')

while attend(1000):  # Calcule une nouvelle étape toutes les secondes
    nouvelle_étape(cellules)
    affiche()

quitte()
