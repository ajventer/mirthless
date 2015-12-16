import pygame
from pygame.locals import *

class Tempsprites(object):
    def __init__(self):
        self.temp = []

    def _addtemp(self, name, obj):
        self.temp.append((obj, name))
        self.frontend.sprites[name] = obj

    def _rmtemp(self):
        for t in self.temp:
            t[0].delete()
            if t[1] in self.frontend.sprites:
                del self.frontend.sprites[t[1]] 