import pygame
from pygame.locals import *
from gamemap import GameMap
from util import imagepath, debug
from messages import messages


class Maptile(object):
    def __init__(self, x, y, map_x, map_y, tile, size, eventstack, tilemaps, mode):
        self.mode = mode
        self.tile = tile
        self.image = pygame.Surface((size,size))
        self.map_x, self.map_y = map_x, map_y
        self.rect = pygame.Rect(x,y, size, size)
        self.eventstack = eventstack
        self.eventstack.register_event("button1", self, self.click)
        #tilemap[x][y]
        backgroundpath = tile.background()
        if backgroundpath:
            backgroundpath = imagepath(backgroundpath)
            backgroundimage = tilemaps[backgroundpath[0]].tile(backgroundpath[1], backgroundpath[2])
            backgroundimage = pygame.transform.smoothscale(backgroundimage, (size, size))
        if backgroundpath and tile.revealed():
            self.image.blit(backgroundimage,(0,0))
        else:
            self.image.fill((0,0,0,0))

    def click(self):
        if self.mode == 'editor':
            messages.message('Editor click: %sx%s' % (self.map_x, self.map_y))   
            return 
        messages.message('Tile click: %sx%s' % (self.map_x, self.map_y))
        return self.rect

class Mapview(object):
    def __init__(self, size, tilesize, eventstack, tilemaps, mode):
        self.rect = (50,65, size, size)
        self.mode = mode
        self.image  = pygame.Surface((size, size))
        self.maptiles = []
        self.tilesize = tilesize
        self.eventstack = eventstack
        self.tilemaps = tilemaps

    def loadmap(self, data):
        gamemap = GameMap(data)
        gamemap.initialize()
        for x in range(0,20):
            for y in range(0,20):
                tile = gamemap.tile(x,y)
                scn_x = 50+(self.tilesize*x)
                scn_y = 65+(self.tilesize*y)
                maptile = Maptile(scn_x,scn_y, x, y, tile, self.tilesize, self.eventstack, self.tilemaps, self.mode)
                self.maptiles.append(maptile)
                self.image.blit(maptile.image,(self.tilesize*x, self.tilesize*y))






