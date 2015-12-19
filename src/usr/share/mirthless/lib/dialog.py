import pygame
from pygame.locals import *
from util import debug, file_list, gamedir, imagepath, load_yaml, dump_yaml, make_hash
from button import Button, render_text, TextInput, ButtonArrow, checkboxbtn
from tempsprites import Tempsprites
from messages import messages
from gamemap import GameMap
import yaml

class Dialog(pygame.sprite.DirtySprite):
    def __init__(self, rect, imagecache, layer=4):
        self._layer=layer
        super(pygame.sprite.DirtySprite, self).__init__()
        self.pos = (rect.x, rect.y)
        tl = imagecache['frame_topleft']
        tr = imagecache['frame_topright']
        bl = imagecache['frame_bottomleft']
        br = imagecache['frame_bottomright']
        top = imagecache['frame_top']
        bottom = imagecache['frame_bottom']
        left = imagecache['frame_left']
        right = imagecache['frame_right']

        self.surface = pygame.Surface((rect.w, rect.h))
        paper = imagecache['paper background.png']
        paper = pygame.transform.smoothscale(paper, (rect.w, rect.h))
        self.surface.blit(paper, (0,0))
        self.surface.blit(tl, (0,0))
        self.surface.blit(tr, (rect.w - tr.get_size()[0], 0))
        self.surface.blit(bl, (0, rect.h - bl.get_size()[1]))
        self.surface.blit(br, (rect.w - br.get_size()[0], rect.h - br.get_size()[1]))

        top = pygame.transform.smoothscale(top, (rect.w -40, top.get_size()[1]))
        self.surface.blit(top, (tl.get_size()[0], 0))

        bottom = pygame.transform.smoothscale(bottom, (rect.w -40, bottom.get_size()[1]))
        self.surface.blit(bottom, (bl.get_size()[0], rect.h - bottom.get_size()[1]))

        left = pygame.transform.smoothscale(left, (left.get_size()[0], rect.h - 20))
        self.surface.blit(left, (0, 10))

        right = pygame.transform.smoothscale(right, (right.get_size()[0], rect.h - 20))
        self.surface.blit(right, (rect.w - right.get_size()[0], 10))        

        self.rect = rect
        self.image = self.surface.copy()


class FloatDialog(Dialog, Tempsprites):
    resolutions=[
        (1024,768),
        (1280,768),
        (1280,800),
        (1280,1024),
        (1400,1050),
        (1920,1080),
        (1920,1200),
        (1360,768)
        ]
    def __init__(self, rect, frontend, layer=5):
        self.frontend = frontend
        self._layer=layer
        Dialog.__init__(self, rect, self.frontend.imagecache, layer=self._layer)
        self.background = self.frontend.screen.subsurface(self.rect).copy()
        Tempsprites.__init__(self)

    def restorebg(self):
        self.frontend.screen.blit(self.background, self.rect)

class ContainerDialog(FloatDialog):
    def __init__(self, rect, frontend, title, layer=20, items=[],onselect=None,onselect_parms=[], animation='view',can_add=False, can_remove=False,can_select=True,addfrom=[]):
        self._layer = layer
        FloatDialog.__init__(self, rect, frontend, layer=layer)
        self.frontend = frontend
        self.image.blit(render_text (title, size=24, color=(255,0,0)),(10,10))
        self.rect = rect
        self.can_add = can_add
        self.can_remove = can_remove
        self.items = items
        self.addfrom = addfrom
        self.animation = animation
        self.onselect = onselect
        self.onselect_parms = onselect_parms
        self.clickhash = self.frontend.eventstack.register_event("button1", self, self.click)
        self.can_select = can_select
        self.layout()

    def layout(self):
        self._rmtemp()
        if self.can_add:
            addbtn = Button('Add Item', 
                self.item,
                ['add'],
                self.frontend.eventstack,
                self.frontend.imagecache,
                pos=(self.rect.x + 15,self.rect.y + 35),
                layer=self._layer +1)
            self._addtemp(make_hash(), addbtn)

    def click(self, pos):
        x,y = pos
        self._rmtemp()
        self.layout()
        if self.can_select:
            selectbtn = Button('Select Item', 
                self.item,
                ['select'],
                self.frontend.eventstack,
                self.frontend.imagecache,
                pos=(self.rect.x + 150,self.rect.y + 35),
                layer=self._layer +1)
            self._addtemp(make_hash(), selectbtn)
        else:
            selectbtn = Button('Done', 
                self.done,
                [],
                self.frontend.eventstack,
                self.frontend.imagecache,
                pos=(self.rect.x + 150,self.rect.y + 35),
                layer=self._layer +1)
            self._addtemp(make_hash(), selectbtn)
        if self.can_remove:
            rmbtn = Button('Remove Item', 
                self.item,
                ['remove'],
                self.frontend.eventstack,
                self.frontend.imagecache,
                pos=(self.rect.x + 300,self.rect.y + 35),
                layer=self._layer +1)
            self._addtemp(make_hash(), rmbtn)

    def delete(self):
        self.frontend.eventstack.unregister_event(self.clickhash)
        self._rmtemp()
        self.kill()
        self.restorebg()

    def item(self, action):
        pass

    def done(self):
        self.onselect(self.items, *self.onselect_parms)



class SettingsDialog(FloatDialog, Tempsprites):
    def __init__(self, rect, frontend, title, layer=19):
        self._layer = layer
        FloatDialog.__init__(self, rect, frontend, layer=layer)
        self.settingsdata = yaml.load(open(self.frontend.settingsfile).read())
        self.resolution = (self.settingsdata['res_x'],self.settingsdata['res_y'])
        try:
            self.respage = self.resolutions.index(self.resolution)
        except ValueError:
            self.respage = 0
        self.layout()

    def layout(self):
        self.image.blit(render_text ('Game directory:', size=24, color=(255,0,0)),(10,10))
        self.gd = TextInput(pygame.Rect(self.rect.x + 220, self.rect.y + 10, self.rect.w-250, 30), 18, self.frontend.eventstack, prompt=self.settingsdata['gamedir'], clearprompt=False, layer=self._layer +1)
        self._addtemp('gamedirinput', self.gd)
        self.image.blit(render_text ('Resolution:', size=24, color=(255,0,0)),(10,60))
        res_left = ButtonArrow(self.resbtn, ['left'], self.frontend.eventstack,self.frontend.imagecache, 'left', pos=(self.rect.x+120,self.rect.y+60), layer=self._layer +1)
        res_right = ButtonArrow(self.resbtn, ['right'], self.frontend.eventstack,self.frontend.imagecache, 'right', pos=(self.rect.x+300,self.rect.y+60), layer=self._layer +1)
        self._addtemp('settings_res_left', res_left)
        self._addtemp('settings_res_right', res_right)
        self.image.blit(render_text ('%s X %s' %self.resolution, size=24, color=(255,0,0)),(170,60))
        self.fullscreenbtn = checkboxbtn('Full screen', self.fullscreen, [], self.frontend.eventstack,self.frontend.imagecache, fontsize=24, pos=(self.rect.x + 10,self.rect.y +100),layer=self._layer +1)
        self.fullscreenbtn.checked = self.settingsdata['fullscreen']        
        self._addtemp('fullscreen', self.fullscreenbtn)
        self.hardwarebtn = checkboxbtn('Hardware rendering(requires fullscreen)', self.hardware, [], self.frontend.eventstack,self.frontend.imagecache,fontsize=24, pos=(self.rect.x + 10,self.rect.y +130),layer=self._layer +1)
        self.hardwarebtn.checked = self.settingsdata['hardware_buffer']
        self._addtemp('hardware rendering', self.hardwarebtn)
        self.image.blit(render_text ('Note: changes only take effect when you restart', size=24, color=(255,0,0)),(10,200))
        save_btn = Button('Save changes', self.save, [], self.frontend.eventstack,self.frontend.imagecache, pos=(self.rect.x + 200,self.rect.y + 250), layer=self._layer +1)
        self._addtemp('savesettings', save_btn)

    def save(self):
        self.settingsdata['gamedir'] = self.gd.text
        strings = dump_yaml(self.settingsdata)
        open(self.frontend.settingsfile,'w').write(strings)
        messages.error('Settings saved. You should restart the game when convenient.')
        self.delete()

    def delete(self):
        self._rmtemp()
        self.kill()
        self.restorebg()

    def fullscreen(self):
        self.settingsdata['fullscreen'] = self.fullscreenbtn.checked

    def hardware(self):
        self.settingsdata['hardware_buffer'] = self.hardwarebtn.checked
        if self.settingsdata['hardware_buffer']:
            self.settingsdata['fullscreen'] = True
            self.fullscreenbtn.checked = True

    def resbtn(self, direction):
        if direction == 'left':
            if self.respage > 0:
                self.respage -= 1
            else:
                self.respage = len(self.resolutions) -1
        if direction == 'right':
            if self.respage < len(self.resolutions) -1:
                self.respage += 1
            else:
                self.respage = 0    
        self.resolution = self.resolutions[self.respage]
        self.image.blit(self.surface.subsurface(170,60,300,50),(170,60))
        self.image.blit(render_text ('%s X %s' %self.resolution, size=24, color=(255,0,0)),(170,60))
        self.settingsdata['res_x'], self.settingsdata['res_y'] = self.resolution[0], self.resolution[1]     


class TileSelector(FloatDialog):
    def __init__(self, rect, frontend, onselect, onselect_parms, layer=5):
        self.onselect = onselect
        self.selected = None
        self.frontend = frontend
        self._layer=layer
        FloatDialog.__init__(self, rect, self.frontend, layer=self._layer)
        self.page = self.frontend.tilemaps.lastpage
        prevbtn = Button('Prev', self.prev, [], self.frontend.eventstack, self.frontend.imagecache, (rect.x+10,rect.y+rect.h-50), layer=self._layer +1)
        nextbtn = Button('Next', self.next, [], self.frontend.eventstack, self.frontend.imagecache, (rect.x+rect.w-100,rect.y+rect.h-50), layer=self._layer +1)
        self.clickhash = self.frontend.eventstack.register_event("button1", self, self.click)
        self._addtemp('ts_prevbtn', prevbtn)
        self._addtemp('ts_nextbtn', nextbtn)
        self.rect = rect
        self.onselect_parms = onselect_parms

        self.pages = sorted(list(self.frontend.tilemaps.keys()))
        self.update()

    def update(self):
        self.image = self.surface.copy()
        col = 0
        row = 0
        x = 10
        y = 10
        filename = self.pages[self.page]
        self.pagepaths = []
        self.image.blit(render_text (filename, size=32, color=(0,0,0)),(self.rect.x+self.rect.w/2, self.rect.y+self.rect.h -50))
        for imagepath in self.frontend.tilemaps.iterall(filename):
            if x >= self.rect.w - 75:
                col = 0
                row += 1
            x =  32 * col + 10
            y =  32 * row + 10
            thisrect = pygame.Rect(self.rect.x + x, self.rect.y+ y, 32, 32)
            self.pagepaths.append((thisrect, imagepath))
            image = pygame.transform.smoothscale(self.frontend.tilemaps.get_by_path(imagepath), (32,32))
            self.image.blit(image, (x,y))
            col += 1

    def click(self, pos):
        x, y = pos
        for path in self.pagepaths:
            if path[0].collidepoint(x, y):
                self.onselect(path[1], *self.onselect_parms)

    def delete(self):
        self._rmtemp()
        self.frontend.eventstack.unregister_event(self.clickhash)
        self.kill()
        self.restorebg()

    def next(self):
        self.page += 1
        if self.page >= len(self.pages):
            self.page = 0
        self.update()


    def prev(self):
        self.page -= 1
        if self.page <= 0:
            self.page = len(self.pages) -1
        self.update()

class MapSelector(TileSelector):
    def __init__(self, rect, frontend, onselect):
        self.onselect = onselect
        self.frontend = frontend
        self.rect = rect
        self._layer=5
        FloatDialog.__init__(self, rect, self.frontend)
        prevbtn = Button('Prev', self.prev, [], self.frontend.eventstack, self.frontend.imagecache, (rect.x+10,rect.y+rect.h-50), layer=6)
        nextbtn = Button('Next', self.next, [], self.frontend.eventstack, self.frontend.imagecache, (rect.x+rect.w-100,rect.y+rect.h-50), layer=6)
        self.clickhash = self.frontend.eventstack.register_event("button1", self, self.click)
        self._addtemp('ts_prevbtn', prevbtn)
        self._addtemp('ts_nextbtn', nextbtn)
        counter = 0
        self.page = 0
        self.pages = [[]]
        pagecounter=0
        for mapfile in file_list('maps'):
            if counter >= 9:
                self.pages.append([])
                pagecounter += 1
            counter += 1
            self.pages[pagecounter].append(self.minimap(mapfile))
        self.update()


    def minimap(self, filename):
        gamemap = GameMap(load_yaml('maps', filename))
        name = gamemap.name()
        surface = pygame.Surface((128,128))
        for x in range(0,20):
            for y in range(0,20):
                tilepath = gamemap.tile(x,y).background()
                if tilepath:
                    tileimage = self.frontend.tilemaps.get_by_path(tilepath)
                    tileimage = pygame.transform.smoothscale(tileimage, (6,6))
                else:
                    tileimage = pygame.Surface((6,6))
                    tileimage.fill((0,0,0))
                surface.blit(tileimage,(x*6, y*6))
        text = render_text(name, size=20, color=(0,0,0), font=pygame.font.Font(None,20))
        textrect = text.get_rect()
        textblock = pygame.Surface((textrect.w, textrect.h))
        textblock.fill((255,255,255))
        textblock.blit(text, (0,0))
        surface.blit(textblock, (0,60))
        return (surface, filename)

    def update(self):
        self.image = self.surface.copy()
        col = 0
        row = 0
        x = 10
        y = 10
        self.pagepaths = []
        for image in self.pages[self.page]:
            imagepath = image[1]
            image = image[0]
            if col == 2:
                col = 0
                row += 1
            x =  130 * col + 10
            y =  130 * row + 10
            thisrect = pygame.Rect(self.rect.x + x, self.rect.y+ y, 128, 128)
            self.pagepaths.append((thisrect, imagepath))
            self.image.blit(image, (x,y))
            col += 1

    def click(self, pos):
        x, y = pos
        for path in self.pagepaths:
            if path[0].collidepoint(x, y):
                data = load_yaml('maps', path[1])
                self.onselect(data, True)







