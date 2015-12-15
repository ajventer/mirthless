import pygame
from pygame.locals import *
from gamemap import GameMap
from util import debug
from messages import messages
from button import render_text, Button

                                
class Mapview(object):
    def __init__(self, frontend):
        self.frontend = frontend
        size = self.frontend.mapw
        self.tilesize = self.frontend.mapscale
        self.rect = pygame.Rect(50,65, self.frontend.mapw, self.frontend.mapw)
        self.frontend.eventstack.register_event("button1", self, self.click)
        self.image  = pygame.Surface((size, size))
        self.backgrounds = {}


    def tileimage(self, x, y, scale):
        tileimage = pygame.Surface((self.tilesize, self.tilesize))
        backgroundpath = self.backgrounds['%s_%s' % (x,y)]
        if backgroundpath:
            tileimage = self.frontend.tilemaps.get_by_path(backgroundpath)
        tileimage = pygame.transform.smoothscale(tileimage, (scale, scale))
        if backgroundpath and tile.revealed():
            self.image.blit(backgroundimage,(0,0))
        else:
            if self.frontend.mode == 'editor':
                if y%2 == 0 and x%2 == 0 or y%2 == 1 and x%2 == 1:
                    r, t = 255, 0
                else:
                    r, t = 0, 255
                tileimage.fill((r,r,r,0))
                tileimage.blit(render_text('%sX%s' %(x,y), size=(self.tilesize/2), color=(t,t,t)), (1,1))
            else:
                tileimage.fill((0,0,0,0))
        return tileimage

    def loadmap(self, data):
        gamemap = GameMap(data)
        gamemap.initialize()
        for x in range(0,20):
            for y in range(0,20):
                tile = gamemap.tile(x,y)
                self.backgrounds['%s_%s' % (x,y)] = tile.background()
                scn_x = 50+(self.tilesize*x)
                scn_y = 65+(self.tilesize*y)
                self.image.blit(self.tileimage(x,y, self.tilesize),(self.tilesize*x, self.tilesize*y))

    def tile_editor(self, x, y, surface):
        surface.blit(render_text('Edit tile', color=(255,0,0)),(280,10))
        button = Button('Click Me', self.clickme, (x,y), self.frontend.eventstack,self.frontend.imagecache, pos=(900,50))
        self.frontend.sprites['tile_edit'] = button
        self.frontend.draw()

    def clickme(self, x, y):
        messages.message('Clicked %sX%s' %(x,y))

    def click(self, pos):
        x, y = pos
        x = x - 50
        y = y - 65
        map_x = int(x / self.tilesize)
        map_y = int(y / self.tilesize)
        zoomimage = self.tileimage(map_x, map_y, 256)
        self.frontend.sprites['rightwindow'].image.blit(zoomimage, (15,15))
        if self.frontend.mode == 'editor':
            self.tile_editor(map_x,map_y, self.frontend.sprites['rightwindow'].image)
            return 
        messages.message('Tile click: %sx%s' % (map_x, map_y))
        return






