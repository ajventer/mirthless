import pygame
from pygame.locals import *
from util import debug

class Messages(object):
    messages=[]
    messageindex = 0
    def __init__(self, screen=None, eventstack=None):
        self.buffer = 6
        if screen:
            screensize = screen.get_rect()
            self.rect = pygame.Rect(0,screensize.h - 190,screensize.w, screensize.h)

    def scrollup(self):
        if self.messageindex > self.buffer:
            self.messageindex -= 1
        else:
            self.messageindex = 0

    def scrolldown(self):
        if self.messageindex < len(self.messages) - self.buffer:
            self.messageindex += 1
        else:
            self.messageindex = len(self.messages) - self.buffer

    def read(self):
        if not self.messages:
            return ''
        result =[]
        if len(self.messages) < self.buffer:
            for line in self.messages:
                result.append(str(line).strip())
            return result
        end = min([self.messageindex + self.buffer, len(self.messages)])
        for I in range(self.messageindex, end):
            line = self.messages[I]
            result.append(str(line).strip())
        return result

    def warning(self,s):
        self.messages.append('{{237,89,9}}%s' %s)
        self.scrolldown()

    def message(self,s):
        self.messages.append('{{255,255,255}}%s' %s)
        self.scrolldown()

    def error(self,s):
        self.messages.append('{{255, 0, 0}}%s' %s)
        debug('Error:', self.read())
        self.scrolldown()

messages = Messages()