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
        result =''
        if len(self.messages) < self.buffer:
            for line in self.messages:
                result += '\n'+line.strip()
            return result
        end = min([self.messageindex + self.buffer, len(self.messages) -1])
        for I in range(self.messageindex, end):
            result += '\n'+self.messages[I].strip()
        return result

    def warning(self,s):
        self.messages.append('{color 237, 89, 9; %s} ' % s.strip())
        self.scrolldown()

    def message(self,s):
        self.messages.append(s.strip())
        self.scrolldown()

    def error(self,s):
        self.messages.append('{color 255, 0, 0; %s} ' % s.strip())
        debug('Error:', self.read())
        self.scrolldown()

messages = Messages()