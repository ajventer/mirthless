import pygame
from pygame.locals import *
from util import debug, file_list, gamedir
from button import Button
from tempsprites import Tempsprites
from messages import messages

class Dialog(pygame.sprite.DirtySprite):
    def __init__(self, rect, imagecache):
        #TODO - create a container type to add things to dialogs and make them work more cleanly
        self._layer = 1
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

class FloatDialog(Dialog):
    def __init__(self, rect, imagecache):
        self._layer=5
        Dialog.__init__(self, rect, imagecache)

class TileSelector(FloatDialog, Tempsprites):
    def __init__(self, rect, frontend, onselect, onselect_parms):
        Tempsprites.__init__(self)
        self.selected = None
        self.frontend = frontend
        self._layer=5
        FloatDialog.__init__(self, rect, self.frontend.imagecache)
        self.page = 0
        prevbtn = Button('Prev', self.prev, [], self.frontend.eventstack, self.frontend.imagecache, (rect.x+10,rect.y+rect.h-50), layer=6)
        nextbtn = Button('Next', self.next, [], self.frontend.eventstack, self.frontend.imagecache, (rect.x+rect.w-100,rect.y+rect.h-50), layer=6)
        selectbtn = Button('Select', self.select, [], self.frontend.eventstack, self.frontend.imagecache, (rect.x+rect.w/2,rect.y+rect.h-50), layer=6)
        self._addtemp('ts_prevbtn', prevbtn)
        self._addtemp('ts_nextbtn', nextbtn)
        self._addtemp('ts_selectbtn', selectbtn)
        self.pages = sorted(list(self.frontend.tilemaps.keys()))
        self.update()

    def update(self):
        self.image = self.surface.copy()
        col = 0
        row = 0
        x = 10
        y = 10
        filename = self.pages[self.page]
        messages.message('Tilemap '+filename)
        for image in self.frontend.tilemaps.iterall(filename):
            if x >= self.rect.w - 75:
                col = 0
                row += 1
            x =  32 * col + 10
            y =  32 * row + 10
            image = pygame.transform.smoothscale(image, (32,32))
            self.image.blit(image, (x,y))
            col += 1

    def delete(self):
        self.kill()

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

    def select(self):
        return 'Test'






