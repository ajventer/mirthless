import pygame
from pygame.locals import *
from gamemap import GameMap
from util import debug
from messages import messages
from button import render_text, Button, checkboxbtn, TextInput
from dialog import FloatDialog
from tempsprites import Tempsprites
from dialog import TileSelector, MapSelector
import yaml
import os
from util import imagepath
                                
class Mapview(pygame.sprite.DirtySprite, Tempsprites):
    def __init__(self, frontend, *args):
        self._layer = 0
        super(pygame.sprite.DirtySprite, self).__init__()
        self.frontend = frontend
        size = self.frontend.mapw
        self.tilesize = self.frontend.mapscale
        self.rect = pygame.Rect(50,65, self.frontend.mapw, self.frontend.mapw)
        self.background = self.frontend.screen.subsurface(self.frontend.screensize).copy()
        self.image  = pygame.Surface((size, size))
        self.backgrounds = {}
        self.mapw = self.frontend.mapw
        Tempsprites.__init__(self)
        self.firstload = True
        self.loadmap({})


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

    def delete(self):
        self.frontend.eventstack.unregister_event(self.clickhash)
        del self.frontend.sprites['rightwindow']
        self._rmtemp()
        self.kill()
        self.frontend.screen.blit(self.background, (0,0))

    def registerclickevent(self):
        self.clickhash = self.frontend.eventstack.register_event("button1", self, self.click)

    def loadmap(self, data, reload=False):
        self.registerclickevent()
        if reload:
            self._rmtemp()
        dialog = FloatDialog(self.frontend.rightwindow_rect, self.frontend, layer=1)
        self._addtemp('rightwindow', dialog)
        self.gamemap = GameMap(data)
        self.gamemap.initialize(data=data)
        if self.frontend.mode == 'editor' and self.firstload:
            self.firstload = False
            self.mapname = TextInput(
                pygame.Rect(50, self.frontend.mapw+70, self.mapw /2,25),
                16, self.frontend.eventstack, 
                prompt=self.gamemap.get('name','Enter map displayname here'))
            mapload = Button('Load', self.load, [], self.frontend.eventstack,self.frontend.imagecache, pos=(self.mapw/2 + 50,self.frontend.mapw+67))
            mapsave = Button('Save', self.save, [], self.frontend.eventstack,self.frontend.imagecache, pos=(self.mapw/2 + 150,self.frontend.mapw+67))
            self._addtemp('mapname', self.mapname)
            self._addtemp('mapload', mapload)
            self._addtemp('mapsave', mapsave)
        for x in range(0,20):
            for y in range(0,20):
                scn_x = 50+(self.tilesize*x)
                scn_y = 65+(self.tilesize*y)
                self.image.blit(self.tileimage(x,y, self.tilesize),(self.tilesize*x, self.tilesize*y))

    def load(self):
        self._addtemp('te_mapselector',MapSelector(self.rect, self.frontend, self.loadmap))
        self.frontend.draw() 

    def save(self):
        self.gamemap.put('name', self.mapname.get_text())
        filename = self.gamemap.save_to_file('maps')
        messages.error('Saved to: %s' % os.path.basename(filename))

    def tile_editor(self, x, y, surface):
        surface.blit(render_text('Edit tile', color=(255,0,0)),(280,10))
        minx, miny = self.frontend.rightwindow_rect.x + 10, self.frontend.rightwindow_rect.y + 10
        maxx, maxy = minx + self.frontend.rightwindow_rect.w - 10, self.frontend.rightwindow_rect.h - 10
        te_canenter = checkboxbtn('Player can enter tile ?', self.canenter, (x,y), self.frontend.eventstack,self.frontend.imagecache, pos=(minx + 280,miny + 60))
        te_revealed = checkboxbtn('Tile has been revealed ?', self.revealed, (x,y), self.frontend.eventstack,self.frontend.imagecache, pos=(minx + 280,miny + 90))
        te_canenter.checked = self.gamemap.tile(x,y).canenter()
        te_revealed.checked = self.gamemap.tile(x,y).revealed()
        if self.tile.background():
            self._addtemp('te_rotate', Button('Rotate background', 
                self.rotate, (x,y), self.frontend.eventstack,self.frontend.imagecache, pos=(minx + 280, miny + 120)))             
        self._addtemp('te_canenter', te_canenter)
        self._addtemp('te_revealed', te_revealed)
        self._addtemp('te_set_background', Button('Set Background', 
            self.selectbg, (x,y), self.frontend.eventstack,self.frontend.imagecache, pos=(minx + 280, miny + 30)))              
        self.frontend.draw()

    def selectbg(self, x, y):
        self._addtemp('te_tileselector',TileSelector(self.rect, self.frontend, self.setbg, (x,y)))
        self.frontend.draw()

    def setbg(self, bgpath, x, y):
        map_x, map_y = x, y
        debug('%s - %sx%s' % (bgpath, x, y))
        self.tile = self.gamemap.tile(map_x,map_y)
        self.tile.put('background', bgpath)
        self.updatetile(x,y) 
        x = x*self.tilesize+50
        y = y*self.tilesize+65
        self.click((x,y))
        debug(bgpath)

    def rotate(self, x,y):
        bgpath = imagepath(self.tile.background())
        rot = int(bgpath[3])
        if rot == 270:
            rot = 0
        else:
            rot += 90
        bgpath = [bgpath[0], bgpath[1], bgpath[2], str(rot)]
        bgpath = ':'.join([str(I) for I in bgpath])
        debug(bgpath)
        self.setbg(bgpath, x, y)


    def canenter(self, x, y):
        self.tile.canenter(self.frontend.sprites['te_canenter'].checked)
        self.updatetile(x, y)

    def revealed(self, x, y):
        self.tile.put('/revealed', self.frontend.sprites['te_canenter'].checked)
        self.updatetile(x, y)

    def updatetile(self, x, y):
        self.gamemap.load_tile(x,y,self.tile)
        self.loadmap(self.gamemap())
        #self.frontend.screen.blit(self.image, (50,65))

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






