import pygame
from pygame.locals import *
from gamemap import GameMap
from util import imagepath, debug
from messages import messages
from button import render_text
from random import randrange

class Maptile(object):
    #self.mapw, self.mapscale, self.eventstack, self.tilemaps, self
    def __init__(self, x, y, map_x, map_y, tile, frontend):
        self.frontend = frontend
        size = self.frontend.mapw
        self.tile = tile
        self.image = pygame.Surface((size,size))
        self.map_x, self.map_y = map_x, map_y
        self.rect = pygame.Rect(x,y, size, size)
        self.frontend.eventstack.register_event("button1", self, self.click)
        #tilemap[x][y]
        backgroundpath = tile.background()
        if backgroundpath:
            backgroundpath = imagepath(backgroundpath)
            backgroundimage = self.frontend.tilemaps[backgroundpath[0]].tile(backgroundpath[1], backgroundpath[2])
            backgroundimage = pygame.transform.smoothscale(backgroundimage, (size, size))
        if backgroundpath and tile.revealed():
            self.image.blit(backgroundimage,(0,0))
        else:
            if self.frontend.mode == 'editor':
                self.image.fill((randrange(0,255),0,0,0))
                self.image.blit(render_text('%sX%s' %(self.map_x,self.map_y), size=16, color=(0,255,0)), (1,1))
            else:
                self.image.fill((0,0,0,0))
                                

    def click(self):
        if self.frontend.mode == 'editor':
            messages.message('Editor click: %sx%s' % (self.map_x, self.map_y))
            return 
        messages.message('Tile click: %sx%s' % (self.map_x, self.map_y))
        return

class Mapview(object):
    def __init__(self, frontend):
        self.frontend = frontend
        size = self.frontend.mapw
        self.tilesize = self.frontend.mapscale
        self.rect = (50,65, self.frontend.mapw, self.frontend.mapw)
        self.image  = pygame.Surface((size, size))
        self.maptiles = []

    def loadmap(self, data):
        gamemap = GameMap(data)
        gamemap.initialize()
        for x in range(0,20):
            for y in range(0,20):
                tile = gamemap.tile(x,y)
                scn_x = 50+(self.tilesize*x)
                scn_y = 65+(self.tilesize*y)
                maptile = Maptile(scn_x,scn_y, x, y, tile, self.frontend)
                self.maptiles.append(maptile)
                self.image.blit(maptile.image,(self.tilesize*x, self.tilesize*y))






