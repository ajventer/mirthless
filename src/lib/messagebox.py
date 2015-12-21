import pygame
from pygame.locals import *
from util import file_path
import re

def render_text (text, size=32, color=(0,0,0)):
    font = pygame.font.SysFont('monospace', size)
    #font = pygame.font.Font(file_path('fonts','BLKCHCRY.TTF'), size)
    return font.render(str(text), 1, color)

class MessageBox(pygame.sprite.DirtySprite):
    def __init__(self, messages, rect, frontend, defaultcolor=(255,255,255)):
        self._layer=0
        super(pygame.sprite.DirtySprite, self).__init__()
        self.frontend = frontend
        self.messages = messages
        self.defaultcolor = defaultcolor
        self.up = self.frontend.eventstack.register_event("wheelup", self, messages.scrollup) 
        self.down = self.frontend.eventstack.register_event("wheeldown", self, messages.scrolldown)
        self.rect = rect
        self.surface = pygame.Surface((self.rect.w, self.rect.h))
        self.background = self.surface.copy()
        self.image = self.surface

    def delete(self):
        self.frontend.eventstack.unregister(self.up)
        self.frontend.eventstack.unregister(self.down)
        self.kill()

    def update(self):
        self.surface.blit(self.background, (0,0))
        y = self.surface.get_rect().y
        for line in self.messages.read():
            color=self.defaultcolor
            pattern = r'{{(.*)}}'
            m = re.search(pattern, line)
            if m:
                color = tuple([int(i) for i in m.groups()[0].split(',')])
                line = re.sub(pattern, '', line)
            lineimg=render_text(line, 16, color)
            self.surface.blit(lineimg,(10,y))
            y += lineimg.get_rect().h
        self.image = self.surface


