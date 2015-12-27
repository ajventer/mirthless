from pygame.locals import *
import pygame
from util import save_yaml
from dialog import FloatDialog

class Journal(list):
    """
    >>> from journal import Journal
    >>> j = Journal()
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
    def write(self, s):
        self.append('')
        self += s.split('\n')

    def read(self):
        if len(self) >= self.bufferlen:
            return self.__getitem__(slice(self.bookmark, self.bookmark+self.bufferlen))
        else:
            return self

    def next(self):
        self.bookmark += self.bufferlen
        if self.bookmark >= len(self):
            self.bookmark = len(self) - self.bufferlen

    def prev(self):
        self.bookmark -= self.bufferlen
        if self.bookmark <= 0:
            self.bookmark = 0

class JournalView(FloatDialog):
    def __init__(self, rect, frontend, char, layer=5, onclose=None, title=''):
        self._layer = layer
        FloatDialog.__init__(self, rect, frontend, layer)
        book = self.frontend.imagecache['spellbookForFlare.png'].copy()
        book = pygame.transform.smoothscale(book, (self.rect.w, self.rect.h))
        self.image.blit(book, (0,0))