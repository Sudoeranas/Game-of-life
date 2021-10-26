"""   13/9/2019
      Nicolas Belin
"""

TOUCHES = """
q : quitter
f : plein écran
"""

import pygame
from math import floor

class Sdl:
    """
    Ouvre une fenêtre de dimension w*h, avec pour titre 'caption'
    """
    def __init__(self, w, h, caption):
        print(TOUCHES)
        self.width = w
        self.height = h
        pygame.display.init()
        self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        pygame.display.set_caption(caption)
        pygame.mouse.set_visible(False)
        self.looping = True
        self.is_fullscreen = False
        self.keys_dict = dict()
        self.user_events_dict = dict()
        self.drawing_funcs = []
        self.register_key('q', self.stop)
        self.register_key('f', self.toggle_fullscreen)

    def stop(self):
        self.post(pygame.QUIT)

    def quit(self):
        pygame.quit()
        
    def post(self, type, *args):
        pygame.event.post(pygame.event.Event(type, *args))

    def post_user(self, name, args):
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, utype = name, args = args))

    def refresh(self):
        for f in self.drawing_funcs:
            f(self.screen)
        pygame.display.flip()
        
    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.screen = pygame.display.set_mode((self.w_old,self.h_old),
                                                  pygame.RESIZABLE)
        else:
            self.is_fullscreen = True
            self.w_old, self.h_old = self.screen.get_size()
            self.screen = pygame.display.set_mode(
                pygame.display.list_modes(0, pygame.FULLSCREEN)[0], pygame.FULLSCREEN)
        self.refresh()
            
    def register_key(self, unicode, func):
        self.keys_dict[unicode] = func

    def register_user_event(self, name, func):
        self.user_events_dict[name] = func

    def register_drawing(self, func):
        self.drawing_funcs.append(func)

    def set_timer(self, func, time):
        self.timer_func = func
        pygame.time.set_timer(pygame.USEREVENT+1, time)

    def check_event(self, ev = None):
        if not ev:
            ev = pygame.event.poll()
        if ev.type == pygame.QUIT:
            self.looping = False
        elif ev.type == pygame.KEYDOWN:
            if ev.unicode in self.keys_dict:
                self.keys_dict[ev.unicode]()
        elif ev.type == pygame.VIDEORESIZE:
            self.screen = pygame.display.set_mode(ev.size, pygame.RESIZABLE)
            self.refresh()
        elif ev.type == pygame.USEREVENT:
            if ev.utype in self.user_events_dict:
                self.user_events_dict[ev.utype](*ev.args)
        elif ev.type == pygame.USEREVENT+1:
            self.timer_func()
        return self.looping
        
    def loop(self):
        while self.looping:
            ev = pygame.event.wait()
            self.check_event(ev)
        self.quit()

    
class PixelMap(Sdl):
    """
    Affiche une fenêtre de titre 'caption' constituée de nx * ny cases.
    Une matrice de couleurs peut être fournie.
    """

    def __init__(self, width, height, nx=None, ny=None,
                 matrix=None, caption='Image', cumulate=False,
                 xmin=None, xmax=None, ymin=None, ymax=None):
        """
        :param width: (int) largeur de la fenêtre
        :param height: (int) hauteur de la fenêtre
        :param nx: (int) nombre de cases verticales
        :param nt: (int) nombre de cases horizontales
        :param matrix: (list) une matrice de couleurs 0xRRGGBB
        :param caption: (str) le titre de la fenêtre
        :param cumule_couleurs: (bool) mixer les couleurs via un canal alpha : 0xAARRGGBB
        :SE: ouvre une fenêtre
        """
        BACKGROUND_COLOR = 0x000000
        if matrix == None:
            if nx == None:
                nx = width
            if ny == None:
                ny = height
            matrix = [[BACKGROUND_COLOR]*nx for _ in range(ny)]
        else:
            nx = len(matrix[0])
            ny = len(matrix)
                
        super().__init__(width, height, caption)

        self.nx, self.ny = nx, ny
        self.cumulate = cumulate
        self.matrix = matrix
        self.xmin = xmin if xmin != None else 0
        self.xmax = xmax if xmax != None else nx - 1
        self.ymin = ymin if ymin != None else 0
        self.ymax = ymax if ymax != None else ny - 1
        self.register_drawing(self.display)
        self.refresh()
        
    def display(self, surface):
        x = lambda i: floor(i * ws / self.nx)
        y = lambda j: floor(j * hs / self.ny)
        ws, hs = surface.get_size()
        if self.ny == hs and self.nx == ws:
            for j in range(self.ny):
                for i in range(self.nx):
                    surface.set_at((i, j), self.matrix[j][i])
            #pixarray = pygame.PixelArray(surface)
            #pixarray[:,:] = self.matrix
            #pixarray.close()
        else:
            for j in range(self.ny):
                for i in range(self.nx):
                    rect = (x(i), y(j), x(i+1)-x(i)-1, y(j+1)-y(j)-1)  
                    surface.fill(self.matrix[j][i], rect)

    def update(self, matrix):
        """
        Change la matrice à utiliser.
        :param matrix: (list) la nouvelle matrice à utiliser
        """
        self.matrix = matrix

    def get_color(self, x, y):
        """
        Renvoie la couleur 0xRRGGBB dans la case
        de coordonnées (x, y)
        """
        return self.matrix[y][x]
        
    def point(self, x, y, couleur = 0xffffff):
        """
        La case de coordonnées (x, y) est colorié avec la couleur
        :param x: (int) Abscisse de la case à colorier
        :param y: (int) Ordonnée de la case à colorier
        :param couleur: (int) La couleur à utiliser (optionnel)
        """
        if x >= self.nx or x < 0 or y >= self.ny or y < 0:
            return
        if self.cumulate:
            unpack = lambda c: ((c & 0x00ff0000) >> 16,
                                (c & 0x0000ff00) >> 8,
                                c & 0x000000ff)
            src_r, src_g, src_b = unpack(couleur)
            dst_r, dst_g, dst_b = unpack(self.get_color(x, y)) 
            out_r = min(src_r + dst_r, 0xff)
            out_g = min(src_g + dst_g, 0xff)
            out_b = min(src_b + dst_b, 0xff)
            #couleur = out_r * 0x10000 + out_g * 0x100 + out_b
            couleur = (out_r << 16) | (out_g << 8) | out_b
        self.matrix[y][x] = couleur


    def __iter__(self):
        self.linear = 0
        return self

    def __next__(self):
        if self.linear < self.nx * self.ny:
            l = self.linear
            self.linear += 1
            return l % self.nx, l // self.nx
        raise StopIteration
        
#########################################
############   Interface   ##############
#########################################
def fenêtre(largeur, hauteur, nx=None, ny=None, titre="titre", matrice=None,
            cumule_couleurs=False, xmin=None, xmax=None, ymin=None, ymax=None): 
    """
    Affiche une fenêtre constituée de nx * ny cases
    et de largeur * hauteur pixels.
    :param largeur: (int) largeur de la fenêtre
    :param hauteur: (int) hauteur de la fenêtre
    :param nx: (int) nombre de cases verticales
    :param nt: (int) nombre de cases horizontales
    :param titre: (str) le titre de la fenêtre
    :param cumule_couleurs: (bool) mixer les couleurs via un canal alpha : 0xAARRGGBB
    :SE: ouvre une fenêtre
    """
    global pm
    
    pm = PixelMap(largeur, hauteur, nx=nx, ny=ny, caption=titre,
                  cumulate=cumule_couleurs, xmin=xmin, xmax=xmax,
                  ymin=ymin, ymax=ymax, matrix=matrice)
    return pm
    
def point(x, y, couleur = 0x00ffffff):
    """
    La case de coordonnées (x, y) est colorié avec la couleur
    :param x: (int) Abscisse de la case à colorier
    :param y: (int) Ordonnée de la case à colorier
    :param couleur: (int) La couleur à utiliser (optionnel)
    """
    pm.point(x, pm.ny - y - 1, couleur)

def couleur(x, y):
    """
    Renvoie la couleur 0xRRGGBB dans la case
    de coordonnées (x, y)
    :param x, y: (int) les coordonnées de la case
    :return: (int) la couleur 0xRRGGBB
    """
    return pm.get_color(x, y)
    
def affiche():
    """
    Affiche ou rafraîchi le contenu de la fenêtre.
    """
    pm.refresh()

def attend(durée = None):
    """
    Si aucune durée n'est indiquée, une boucle sans fin qui teste
    les touches 'f' et 'q'.
    Simon, attend la durée indiquée, teste les événements et renvoie
    si le programme doit continuer ou non.
    :param durée: (int) temps d'attente en milliseconde
    :return: (bool) vraie si le programme doit continuer à fonctionner.
    """
    if durée == None:
        pm.loop()
    else:
        pygame.time.wait(durée)
        return pm.check_event()

def quitte():
    """
    Ferme la fenêtre et stop l'exécution.
    """
    pm.quit()

def colore(pixel, couleur):
    point(*pixel, couleur)

def abscisse(pixel):
    return pm.xmin + (pixel[0] + 0.5) * (pm.xmax - pm.xmin) / pm.nx

def ordonnée(pixel):
    return pm.ymin + (pixel[1] + 0.5) * (pm.ymax - pm.ymin) / pm.ny


########################################
##############   Exemple   #############
########################################
if __name__ == '__main__':
    
    fenêtre(600, 400, 60, 40)
    point(10, 20)
    point(30, 30, 0xff0000)
    point(50, 35, 0x00ffff)
    affiche()
    attend()
    quitte()
