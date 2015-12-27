from pygame.locals import *
import pygame
from util import save_yaml
from dialog import FloatDialog
from util import gamedir
import json
import os
from tempsprites import Tempsprites
from button import render_text

class Journal(list):
    """
    >>> from journal import Journal
    >>> j = Journal()
    >>> j.autosave = False
    >>> j.write('Hello world')
    >>> j.write('Love me')
    >>> j.read()
    ['', 'Hello world', '', 'Love me']
    >>> j.bufferlen = 2
    >>> j.read()
    ['', 'Hello world']
    >>> j.prev()
    >>> j.read()
    ['', 'Hello world']
    >>> j.next()
    >>> j.read()
    ['', 'Love me']
    """
    bufferlen = 30
    bookmark = 0
    autosave = True
    def write(self, s):
        self.append('')
        self += s.split('\n')
        if self.autosave:
            self.savetoslot()

    def read(self):
        if len(self) >= self.bufferlen:
            return self.__getitem__(slice(self.bookmark, self.bookmark+self.bufferlen))
        else:
            return self

    def next(self):
        self.bookmark += self.bufferlen
        if self.bookmark >= len(self):
            self.bookmark = len(self) - self.bufferlen

    def scrollup(self):
        self.prev()

    def scrolldown(self):
        self.next()

    def prev(self):
        self.bookmark -= self.bufferlen
        if self.bookmark <= 0:
            self.bookmark = 0

    def savetoslot(self):
        savedir = gamedir[0]
        filename = os.path.join(savedir,'journal','journal.yaml')
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        open(filename, 'w').write(json.dumps(self,indent=4))

class JournalView(FloatDialog, Tempsprites):
    def __init__(self, rect, frontend, journal, layer=5, title=''):
        self._layer = layer
        self.journal = journal
        self.frontend = frontend
        FloatDialog.__init__(self, rect, frontend, layer)
        if self.journal is None:
            self.journal = self.frontend.game.journal
        self.rect = rect
        book = self.frontend.imagecache['spellbookForFlare.png'].copy()
        book = pygame.transform.smoothscale(book, (self.rect.w, self.rect.h))
        self.image.blit(book, (0,0))
        self.mb_rect = pygame.Rect(self.rect.x +200, self.rect.y + 10, self.rect.w - 400, self.rect.h - 200)
        self.bg = self.image.copy()
        self.up = self.frontend.eventstack.register_event("wheelup", self, self.journal.prev) 
        self.down = self.frontend.eventstack.register_event("wheeldown", self, self.journal.next)

    def delete(self):
        self.frontend.eventstack.unregister_event(self.up)
        self.frontend.eventstack.unregister_event(self.down)
        FloatDialog.delete(self)

    def update(self):
        self.image.blit(self.bg, (0,0))
        x = self.mb_rect.x
        y = self.mb_rect.y
        for line in self.journal.read():
            lineimg=render_text(line, 16, (0,0,0))
            y +=  lineimg.get_rect().h
            if y >= self.mb_rect.y + self.mb_rect.h:
                x = self.mb_rect.w/2 + 300
                y = self.mb_rect.y
            self.image.blit(lineimg,(x,y))
