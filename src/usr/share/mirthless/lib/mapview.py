import pygame
from pygame.locals import *
from gamemap import GameMap
from util import debug
from messages import messages
from button import render_text, Button, checkboxbtn, TextInput
from tempsprites import Tempsprites
from dialog import TileSelector
import yaml
                                
class Mapview(Tempsprites):
    def __init__(self, frontend):
        self.frontend = frontend
        size = self.frontend.mapw
        self.tilesize = self.frontend.mapscale
        self.rect = pygame.Rect(50,65, self.frontend.mapw, self.frontend.mapw)
        self.clickhash = self.frontend.eventstack.register_event("button1", self, self.click)
        self.image  = pygame.Surface((size, size))
        self.backgrounds = {}
        self.mapw = self.frontend.mapw
        Tempsprites.__init__(self)


    def tileimage(self, x, y, scale):
        tile = self.gamemap.tile(x,y)
        tileimage = pygame.Surface((16, 16))
        backgroundpath = tile.background()
        if backgroundpath:
            backgroundimage = self.frontend.tilemaps.get_by_path(backgroundpath)
        else:
            backgroundimage = pygame.Surface((scale, scale))
        if backgroundpath and (tile.revealed() or self.frontend.mode == 'editor'):
            debug('Blitting visible tile ', backgroundimage)
            tileimage.blit(backgroundimage,(0,0))
            tileimage = pygame.transform.smoothscale(tileimage, (scale, scale))
            if self.frontend.mode == 'editor':
                tileimage.blit(render_text('%sX%s' %(x,y), size=(self.tilesize/2), color=(0,0,0), font=pygame.font.Font(None,16) ), (self.tilesize/2,self.tilesize/2))
        else:
            if self.frontend.mode == 'editor':
                if y%2 == 0 and x%2 == 0 or y%2 == 1 and x%2 == 1:
                    r, t = 255, 0
                else:
                    r, t = 0, 255
                backgroundimage.fill((r,r,r,0))
                backgroundimage.blit(render_text('%sX%s' %(x,y), size=(self.tilesize/2), color=(t,t,t), font=pygame.font.Font(None,16) ), (1,1))
                tileimage =backgroundimage
            else:
                tileimage.fill((0,0,0,0))
        return tileimage

    def loadmap(self, data):
        self.gamemap = GameMap(data)
        self.gamemap.initialize(data=data)
        mapname = TextInput(pygame.Rect(50, self.frontend.mapw+70, self.mapw /2,25), 16, self.frontend.eventstack, prompt=self.gamemap.get('core/name','Enter map displayname here'))
        mapload = Button('Load', self.load, [], self.frontend.eventstack,self.frontend.imagecache, pos=(self.mapw/2 + 50,self.frontend.mapw+67))
        mapsave = Button('Save', self.save, [], self.frontend.eventstack,self.frontend.imagecache, pos=(self.mapw/2 + 150,self.frontend.mapw+67))
        self._addtemp('mapname', mapname)
        self._addtemp('mapload', mapload)
        self._addtemp('mapsave', mapsave)
        for x in range(0,20):
            for y in range(0,20):
                tile = self.gamemap.tile(x,y)
                scn_x = 50+(self.tilesize*x)
                scn_y = 65+(self.tilesize*y)
                self.image.blit(self.tileimage(x,y, self.tilesize),(self.tilesize*x, self.tilesize*y))

    def load(self):
        pass

    def save(self):
        pass

    def tile_editor(self, x, y, surface):
        surface.blit(render_text('Edit tile', color=(255,0,0)),(280,10))
        minx, miny = self.frontend.rightwindow_rect.x + 10, self.frontend.rightwindow_rect.y + 10
        maxx, maxy = minx + self.frontend.rightwindow_rect.w - 10, self.frontend.rightwindow_rect.h - 10
        te_canenter = checkboxbtn('Player can enter tile ?', self.canenter, (x,y), self.frontend.eventstack,self.frontend.imagecache, pos=(minx + 280,miny + 60))
        te_revealed = checkboxbtn('Tile has been revealed ?', self.revealed, (x,y), self.frontend.eventstack,self.frontend.imagecache, pos=(minx + 280,miny + 90))
        te_canenter.checked = self.gamemap.tile(x,y).canenter()
        te_revealed.checked = self.gamemap.tile(x,y).revealed()
        self._addtemp('te_canenter', te_canenter)
        self._addtemp('te_revealed', te_revealed)
        self._addtemp('te_set_background', Button('Set Background', 
            self.selectbg, (x,y), self.frontend.eventstack,self.frontend.imagecache, pos=(minx + 280, miny + 30)))              
        self._addtemp('updatebtn', Button('Update tile', 
            self.updatetile, (x,y), self.frontend.eventstack,self.frontend.imagecache, pos=(minx + (maxx - minx)/2, miny + maxy - 50)))      
        self.frontend.draw()

    def selectbg(self, x, y):
        self.frontend.eventstack.unregister_event(self.clickhash)
        self._addtemp('te_tileselector',TileSelector(self.rect, self.frontend, self.setbg, (x,y)))
        self.frontend.draw()

    def setbg(self, bgpath, x, y):
        map_x, map_y = x, y
        debug('%s - %sx%s' % (bgpath, x, y))
        self.clickhash = self.frontend.eventstack.register_event("button1", self, self.click)
        self.tile = self.gamemap.tile(map_x,map_y)
        self.tile.put('core/background', bgpath)
        self.updatetile(x,y) 
        x = x*self.tilesize+50
        y = y*self.tilesize+65
        self.click((x,y))


    def canenter(self, x, y):
        self.tile.canenter(self.frontend.sprites['te_canenter'].checked)

    def revealed(self, x, y):
        self.tile.put('/core/revealed', self.frontend.sprites['te_canenter'].checked)        

    def updatetile(self, x, y):
        self.gamemap.load_tile(x,y,self.tile)
        self.loadmap(self.gamemap())
        self.frontend.screen.blit(self.image, (50,65))

    def click(self, pos):
        self._rmtemp()
        x, y = pos
        x = x - 50
        y = y - 65
        map_x = int(x / self.tilesize)
        map_y = int(y / self.tilesize)
        zoomimage = self.tileimage(map_x, map_y, 128)
        self.frontend.sprites['rightwindow'].image.blit(zoomimage, (15,15))
        self.tile = self.gamemap.tile(map_x,map_y)
        if self.frontend.mode == 'editor':
            self.tile_editor(map_x,map_y, self.frontend.sprites['rightwindow'].image)
            return 
        messages.message('Tile click: %sx%s' % (map_x, map_y))
        return






