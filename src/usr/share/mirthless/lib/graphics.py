# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *


def get_screen(resx, resy, hardware, fullscreen):
    flags = DOUBLEBUF
    if hardware:
        flags = flags | HWSURFACE
    if fullscreen:
        flags = flags | FULLSCREEN

    return  pygame.display.set_mode((resx, resy), flags)


def scrn_print(surface, text, x, y, size=32, color=(0,0,0)):
    font = pygame.font.Font(None, size)
    text = font.render(str(text), 1, color)
    textpos = text.get_rect()
    textpos.centerx = x
    textpos.centery = y
    surface.blit(text, textpos)

class Tilemap(object):
    def __init__(self, filename, width, height):
        #Credit - this came almost directly from the tutorial at: https://qq.readthedocs.org/en/latest/tiles.html
        image = pygame.image.load(filename).convert()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, image_width/width):
            line = []
            tile_table.append(line)
            for tile_y in range(0, image_height/height):
                rect = (tile_x*width, tile_y*height, width, height)
                line.append(image.subsurface(rect))
        self.tile_table = tile_table

    def table(self):
        return self.tile_table

    def tile(self, x, y):
        return self.tile_table[x][y]
