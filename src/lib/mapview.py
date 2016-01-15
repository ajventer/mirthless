import pygame
from pygame.locals import *
from gamemap import GameMap
from util import debug
from messages import messages
from button import render_text, Button, checkboxbtn, TextInput
from dialog import FloatDialog, ContainerDialog
from tempsprites import Tempsprites
from dialog import TileSelector, MapSelector
from animatedsprite import ButtonSprite
import yaml
import os
from util import imagepath, file_list, load_yaml, make_hash, default_text, editsnippet
from item import Item
from math import hypot

                                
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
        self.dialog = FloatDialog(self.frontend.rightwindow_rect, self.frontend, layer=1)
        self._addtemp('rightwindow', self.dialog)
        if self.frontend.mode == 'editor':
            self.loadmap({})
        else:
            loc = self.frontend.game.player.location()
            mapname = loc['map']
            self.loadmap(load_yaml('maps', mapname))


    def tileimage(self, x, y, scale):
        tile = self.gamemap.tile(x,y)
        tileimage = pygame.Surface((16, 16))
        backgroundpath = tile.background()
        if backgroundpath:
            backgroundimage = self.frontend.tilemaps.get_by_path(backgroundpath)
        else:
            backgroundimage = pygame.Surface((scale, scale))
        if backgroundpath and (tile.revealed() or self.frontend.mode == 'editor'):
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

    def tileicons(self, x, y, scn_x, scn_y, scale):
        rect = pygame.Rect(scn_x, scn_y, scale, scale)
        if self.frontend.mode != 'editor':
            if not self.gamemap.tile(x,y).get('revealed', False):
                return
            player = self.frontend.game.player
            loc = player.location()
            if loc['x'] == x and loc['y'] == y and not 'player' in self.frontend.sprites:
                playerbtn = ButtonSprite(
                    self.frontend.tilemaps,
                    rect,
                    self.frontend.eventstack,
                    onclick = self.click,
                    onclick_params = [(scn_x,scn_y)],
                    animations = player.getsubtree('animations'),
                    layer=self._layer+2,
                    fps=5,
                    mouseover=player.displayname(),
                    frontend=self.frontend)
                self.frontend.sprites['player'] = playerbtn
        scn_x = 50+(self.tilesize*x)
        scn_y = 65+(self.tilesize*y)
        npc = None
        animations = {'view':[]}
        for objtype, item in self.gamemap.tile_objects(x,y):
            if objtype != 'npc':
                animations['view'] += item.get('animations/view')
            else:
                npc = ButtonSprite(
                    self.frontend.tilemaps,
                    rect,
                    self.frontend.eventstack,
                    onclick = self.click,
                    onclick_params = [(scn_x,scn_y)],
                    animations = item.getsubtree('animations'),
                    layer=self._layer+2,
                    fps=5,
                    mouseover=item.displayname(),
                    frontend=self.frontend)
        if animations['view'] and npc is None:
            itemsprite = ButtonSprite(
                self.frontend.tilemaps,
                rect,
                self.frontend.eventstack,
                onclick = self.click,
                onclick_params = [(scn_x,scn_y)],
                animations = animations,
                layer=self._layer+1,
                fps=3,
                frontend=self.frontend)
            self._addtemp(make_hash(), itemsprite)
        if npc is not None and not npc.get_hash() in self.frontend.sprites:
            self.frontend.sprites[npc.get_hash()] = npc
            if not npc in self.frontend.game.characters: 
                self.frontend.game.characters.append(npc)

    def update(self):
        self.loadmap(self.gamemap())


    def zoomicons(self, x, y, scn_x, scn_y):
        objlist = list(self.gamemap.tile_objects(x,y))
        n = len(objlist)
        if not n:
            return
        col, row = 0, 0
        if n%2 != 0:
            n += 1
        colcount = n/2
        if n < 4:
            scale = int(128/n)
        else:
            scale = int(128/colcount)
        for objtype,item in objlist:
            s_x = scn_x + col*scale
            s_y = scn_y + row*scale
            rect = pygame.Rect(s_x, s_y, scale, scale)
            if objtype != 'money':
                animations = item.getsubtree('animations')
                name=item.displayname()
            else:
                animations = item
                name='Money'
            itemsprite = ButtonSprite(
            self.frontend.tilemaps,
            rect,
            self.frontend.eventstack,
            onclick = self.targetclick,
            onclick_params = [x,y,objtype, item],
            animations = animations,
            layer=self._layer+2,
            mouseover=name,
            fps=5,
            frontend=self.frontend)
            if objtype == 'npc':
                itemsprite.setanimation('stand')
            else:
                itemsprite.setanimation('view')
            self._addtemp(make_hash(), itemsprite)
            col += 1
            if col == colcount:
                col = 0
                row += 1
    
    def targetclick(self,x,y,objtype, item):
        minx, miny = self.frontend.rightwindow_rect.x + 10, self.frontend.rightwindow_rect.y + 10
        if self.frontend.mode == 'editor':
            rmBtn = Button('Remove',
            self.removefromtile,
            [x,y,objtype,item],
            self.frontend.eventstack,
            self.frontend.imagecache,
            pos=(minx,miny + 185)
            )
            self._addtemp(make_hash(), rmBtn)

    def removefromtile(self,x,y,objtype,item):
        self.gamemap.removefromtile(x,y,item,objtype)
        self.tile = self.gamemap.tile(x,y)
        self._rmtemp()
        self.updatetile(x, y)

    def delete(self):
        self.frontend.eventstack.unregister_event(self.clickhash)
        del self.frontend.sprites['rightwindow']
        self._rmtemp()
        self.kill()
        self.frontend.screen.blit(self.background, (0,0))

    def registerclickevent(self):
        self.clickhash = self.frontend.eventstack.register_event("button1", self, self.click)
        if self.frontend.mode != 'editor':
            self.frontend.eventstack.register_event("keydown", self, self.keydown)
            self.has_focus = True

    def maploadsavename(self):
        name = self.gamemap.get('name','Enter map displayname here')
        self.mapname = TextInput(
            pygame.Rect(50, self.frontend.mapw+70, self.mapw /2,25),
            16, self.frontend.eventstack, 
            prompt=self.gamemap.get('name',name))
        mapload = Button('Load', self.load, [], self.frontend.eventstack,self.frontend.imagecache, pos=(self.mapw/2 + 50,self.frontend.mapw+67))
        mapsave = Button('Save', self.save, [], self.frontend.eventstack,self.frontend.imagecache, pos=(self.mapw/2 + 150,self.frontend.mapw+67))
        self._addtemp('mapname', self.mapname)
        self._addtemp('mapload', mapload)
        self._addtemp('mapsave', mapsave)        

    def loadmap(self, data, reload=False):
        if reload:
            self._rmtemp()
        self.registerclickevent()
        self.gamemap = GameMap(data)
        self.gamemap.initialize(data=data)
        if self.frontend.mode == 'editor':
            self.maploadsavename()
        for x in range(0,20):
            for y in range(0,20):
                scn_x = 50+(self.tilesize*x)
                scn_y = 65+(self.tilesize*y)
                self.image.blit(self.tileimage(x,y, self.tilesize),(self.tilesize*x, self.tilesize*y))
                self.tileicons(x,y, scn_x, scn_y, self.tilesize)

    def load(self):
        self._addtemp('te_mapselector',MapSelector(self.rect, self.frontend, self.loadmap))
        self.frontend.draw() 

    def save(self):
        if self.mapname.text:
            self.gamemap.put('name', self.mapname.text)
        filename = self.gamemap.save_to_file('maps')
        messages.error('Saved to: %s' % os.path.basename(filename))

    def player_can_goto(self, x, y):
        loc = self.frontend.game.player.location()
        xdiff = loc['x'] - x
        ydiff = loc['y'] - y
        distance = hypot(xdiff, ydiff)
        return distance <= 1.5 and self.gamemap.tile(x,y).canenter()

    def player_controls(self, x,y, surface):
        minx, miny = self.frontend.rightwindow_rect.x + 10, self.frontend.rightwindow_rect.y + 10
        maxx, maxy = minx + self.frontend.rightwindow_rect.w - 10, self.frontend.rightwindow_rect.h - 10
        if self.player_can_goto(x, y):
             player_go_here = Button('Go Here', 
                                    self.goto, 
                                    ['player', x, y],
                                    self.frontend.eventstack,
                                    self.frontend.imagecache,
                                    pos=(minx +180,miny + 10))
             self._addtemp('player_go_here', player_go_here)

    def keydown(self, event):
        messages.message('Processing event '+event.unicode)
        loc = self.frontend.game.player.location()
        x = loc['x']
        y = loc['y']
        if event.key == K_LEFT or event.unicode.upper() == 'A':
            x -= 1
        elif event.key == K_RIGHT or event.unicode.upper() == 'D':
            x += 1
        elif event.key == K_UP or event.unicode.upper() == 'W':
            y -= 1
        elif event.key == K_DOWN or event.unicode.upper() == 'S':
            y += 1
        else:
            return False
        if self.player_can_goto(x, y):
            self.goto('player', x, y)
        return True

    def goto(self, charname, x, y):
        sprite = self.frontend.sprites[charname]
        scn_x = 50+(self.tilesize*x)
        scn_y = 65+(self.tilesize*y)
        sprite.onarive = self.arrive_at
        sprite.onarive_params = [charname,x,y]
        sprite.goto = (scn_x, scn_y)

    def arrive_at(self, charname, x, y):
        if charname == 'player':
            self.frontend.game.player.moveto(self.gamemap, x,y)
            self.frontend.game.player.savetoslot()
        else:
            for char in self.frontend.game.characters:
                if char.get_hash() == charname:
                    char.moveto(self.gamemap, x, y)
                    char.savetoslot('characters')
                    break
        self.gamemap.savetoslot('maps')



    def tile_editor(self, x, y, surface):
        surface.blit(render_text('Edit tile', color=(255,0,0)),(280,10))
        minx, miny = self.frontend.rightwindow_rect.x + 10, self.frontend.rightwindow_rect.y + 10
        maxx, maxy = minx + self.frontend.rightwindow_rect.w - 10, self.frontend.rightwindow_rect.h - 10
        te_canenter = checkboxbtn('Player can enter tile ?', self.canenter, (x,y), self.frontend.eventstack,self.frontend.imagecache, pos=(minx + 180,miny + 60))
        te_revealed = checkboxbtn('Tile has been revealed ?', self.revealed, (x,y), self.frontend.eventstack,self.frontend.imagecache, pos=(minx + 180,miny + 90))
        te_canenter.checked = self.gamemap.tile(x,y).canenter()
        te_revealed.checked = self.gamemap.tile(x,y).revealed()
        if self.tile.background():
            self._addtemp('te_rotate', Button('Rotate background', 
                self.rotate, (x,y), self.frontend.eventstack,self.frontend.imagecache, pos=(minx + 180, miny + 120)))
        self._addtemp('te_canenter', te_canenter)
        self._addtemp('te_revealed', te_revealed)
        self._addtemp('te_set_background', Button('Set Background', 
            self.selectbg, (x,y), self.frontend.eventstack,self.frontend.imagecache, pos=(minx + 180, miny + 30)))
        if self.tile.background() and self.tile.canenter():
            te_additem = Button('Add Item', self.additem, [x,y], self.frontend.eventstack,self.frontend.imagecache, pos=(minx,miny + 160))
            te_addnpc = Button('Add NPC', self.addnpc, [x,y], self.frontend.eventstack,self.frontend.imagecache, pos=(minx + 120,miny + 160))
            te_onenter = Button('Events/OnEnter', self.onenter, [x,y], self.frontend.eventstack,self.frontend.imagecache, pos=(minx + 250,miny + 160))
            self._addtemp('te_additem', te_additem)
            self._addtemp('te_addnpc', te_addnpc)
            self._addtemp('te_onenter', te_onenter)
        te_clone_tile = Button('Clone Tile', self.clonetile, [x,y], self.frontend.eventstack,self.frontend.imagecache, pos=(minx,miny + 200))
        self._addtemp('te_clone', te_clone_tile)
        clone_coords = TextInput(
            pygame.Rect(minx + 150,  miny + 200, 100,25),
            16, self.frontend.eventstack, 
            prompt='%sx%s' %(x,y), layer=3)
        self._addtemp('te_clone_coords', clone_coords)
        debug(self.frontend.sprites)

    def clonetile(self, x,y):
        target=self.frontend.sprites['te_clone_coords'].text
        tx, ty = target.split('x')
        tx, ty = int(tx), int(ty)
        for iy in range(y,ty +1):
            for ix in range(x,tx +1):
                self.gamemap.copy_tile(x,y,ix,iy)
        self.updatetile(x, y)

    def selectlist(self, dirname,action, x, y):
        self._rmtemp()
        itemlist = []
        for itemfile in file_list(dirname):
            itemfile = os.path.basename(itemfile)
            itemlist.append(Item(load_yaml(dirname,itemfile)))
        c = ContainerDialog(self.rect,
            self.frontend,
            'Add %s' % dirname,
            self._layer + 1,
            items=itemlist,
            onclose=action,
            onclose_parms=[x,y],
            onselect=action,
            onselect_parms=[x,y],
            animation='view',
            can_add=False,
            can_remove=False)
        self._addtemp('te_listmanager' , c)

    def additem(self, x, y):
        self.selectlist('items', self.newitem, x, y)


    def addnpc(self, x, y):
        self.selectlist('characters', self.newnpc, x, y)

    def onenter(self,x,y):
        default = default_text
        data = self.gamemap.tile(x,y).get('events/onenter', default)
        data = editsnippet('\n'.join(data))
        tile = self.gamemap.tile(x,y)
        tile.put('events/onenter',data.split('\n'))
        self.gamemap.load_tile(x,y,tile)
        self.tile = self.gamemap.tile(x,y)
        self.updatetile(x, y)

    def newnpc(self, item, x,y):
        self._rmtemp()
        if item is not None:
            self.gamemap.addtotile( x, y, item, 'npc')
            debug(self.gamemap())
        self.tile = self.gamemap.tile(x,y)
        self.updatetile(x, y)

    def newitem(self, item,x,y):
        self._rmtemp()
        if item is not None:
            self.gamemap.addtotile( x, y, item, 'items')
        self.tile = self.gamemap.tile(x,y)
        self.updatetile(x, y)

    def selectbg(self, x, y):
        self._addtemp('te_tileselector',TileSelector(self.rect, self.frontend, self.setbg, (x,y)))

    def setbg(self, bgpath, x, y):
        map_x, map_y = x, y
        self.tile = self.gamemap.tile(map_x,map_y)
        self.tile.put('background', bgpath)
        self.updatetile(x,y) 
        x = x*self.tilesize+50
        y = y*self.tilesize+65
        self.click((x,y))

    def rotate(self, x,y):
        bgpath = imagepath(self.tile.background())
        rot = int(bgpath[3])
        if rot == 270:
            rot = 0
        else:
            rot += 90
        bgpath = [bgpath[0], bgpath[1], bgpath[2], str(rot)]
        bgpath = ':'.join([str(I) for I in bgpath])
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
        self.dialog = FloatDialog(self.frontend.rightwindow_rect, self.frontend, layer=1)
        self._addtemp('rightwindow', self.dialog)
        zoomimage = self.tileimage(x, y, 128)
        self.dialog.image.blit(zoomimage, (15,15))
        self.zoomicons(x, y, self.frontend.rightwindow_rect.x + 15,self.frontend.rightwindow_rect.y + 15)
        if self.frontend.mode == 'editor':
            self.maploadsavename()
            self.tile_editor(x,y, self.dialog.image)
        else:
            self.player_controls(x,y, self.dialog.image)

    def click(self, pos):
        self._rmtemp()
        x, y = pos
        x = x - 50
        y = y - 65
        map_x = int(x / self.tilesize)
        map_y = int(y / self.tilesize)
        self.tile = self.gamemap.tile(map_x, map_y)
        if self.tile.get('revealed', False) or self.frontend.mode == 'editor':
            self.updatetile(map_x, map_y)
