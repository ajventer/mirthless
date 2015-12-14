import pygame
from pygame.locals import *
from gamemap import GameMap
from util import debug
from messages import messages
from button import render_text
from random import randrange

                                
class Mapview(object):
    def __init__(self, frontend):
        self.frontend = frontend
        size = self.frontend.mapw
        self.tilesize = self.frontend.mapscale
        self.rect = pygame.Rect(50,65, self.frontend.mapw, self.frontend.mapw)
        self.frontend.eventstack.register_event("button1", self, self.click)
        self.image  = pygame.Surface((size, size))


    def tileimage(self, x, y, scale):
        tileimage = pygame.Surface((self.tilesize, self.tilesize))
        backgroundpath = tile.background()
        if backgroundpath:
            tileimage = self.frontend.tilemaps.get_by_path(backgroundpath)
            tileimage = pygame.transform.smoothscale(backgroundimage, (scale, scale))
        if backgroundpath and tile.revealed():
            self.image.blit(backgroundimage,(0,0))
        else:
            if self.frontend.mode == 'editor':
                tileimage.fill((randrange(0,255),0,0,0))
                tileimage.blit(render_text('%sX%s' %(x,y), size=16, color=(0,255,0)), (1,1))
            else:
                tileimage.fill((0,0,0,0))
        return tileimage

    def loadmap(self, data):
        gamemap = GameMap(data)
        gamemap.initialize()
        for x in range(0,20):
            for y in range(0,20):
                tile = gamemap.tile(x,y)
                scn_x = 50+(self.tilesize*x)
                scn_y = 65+(self.tilesize*y)
                self.image.blit(tileimage(x,y, self.tilesize),(self.tilesize*x, self.tilesize*y))

    def click(self, pos):
        x, y = pos
        x = x - 50
        y = y - 65
        map_x = int(x / self.tilesize)
        map_y = int(y / self.tilesize)

        zoomimage = tileimage(map_x, map_y, 128)
        self.frontend.sprites['rightwindow'].image.blit(zoomimage, (15,15))
        if self.frontend.mode == 'editor':
            messages.message('Editor click: %sx%s' % (map_x, map_y))
            return 
        messages.message('Tile click: %sx%s' % (map_x, map_y))
        return






