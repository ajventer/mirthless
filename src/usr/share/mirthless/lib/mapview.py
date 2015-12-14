import pygame
from pygame.locals import *
from gamemap import GameMap
from util import imagepath, debug
from messages import messages

class ZoomSprite(pygame.sprite.DirtySprite):
    def __init__(self,rect):
        super(pygame.sprite.DirtySprite, self).__init__()
        self.rect = rect
        self.image = pygame.Surface((rect.w / 2, rect.h /2))
        self.pos = (self.rect.x, self.rect.y)

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
            self.image.fill((0,0,0,0))

    def click(self):
        debug(self.frontend.rightwindow_rect.y)
        zoomrect = pygame.Rect(self.frontend.rightwindow_rect.x + 15,self.frontend.rightwindow_rect.y + 15,self.frontend.rightwindow_rect.w  - 15,self.frontend.rightwindow_rect.h - 15)
        debug(zoomrect)        
        zoomimage = pygame.transform.smoothscale(self.image, (zoomrect.w, zoomrect.h))
        zoomsprite = ZoomSprite(zoomrect)
        zoomsprite.image.blit(zoomimage, (0,0))
        self.frontend.layout['sprites'].append(zoomsprite)
        if self.frontend.mode == 'editor':
            messages.message('Editor click: %sx%s' % (self.map_x, self.map_y))

            return 
        messages.message('Tile click: %sx%s' % (self.map_x, self.map_y))
        return self.rect

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






