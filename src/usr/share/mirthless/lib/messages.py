import pygame
from pygame.locals import *
from util import debug

class Messages(object):
    messages=[]
    messageindex = 0
    def __init__(self, screen=None, eventstack=None):
        if screen:
            screensize = screen.get_rect()
            self.rect = pygame.Rect(0,screensize.h - 190,screensize.w, screensize.h)
        if eventstack:
            debug('Registering wheel handlers')
            eventstack.register_event("wheelup", self, self.scrollup) 
            eventstack.register_event("wheeldown", self, self.scrolldown)

    def scrollup(self):
        if self.messageindex > 5:
            self.messageindex -= 1
        else:
            self.messageindex = 0

    def scrolldown(self):
        if self.messageindex < len(self.messages) -6:
            self.messageindex += 1
        else:
            self.messageindex = len(self.messages) -6

    def read(self):
        if not self.messages:
            return ''
        result =''
        if len(self.messages) < 5:
            for line in self.messages:
                result += '\n'+line.strip()
            return result
        end = min([self.messageindex + 5, len(self.messages) -1])
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