import pygame
from pygame.locals import *
from util import debug, file_list, readyaml, gamedir
from imagecache import ImageCache

class EventStack():
    def __init__(self):
        self.events = {
            "mouseover": {},
            "mouseout": {},
            "button1": {},
            "button1up": {}
        }

    def register_event(self, event, sprite, method):
        self.events[event][sprite] = method

    def handle_event(self, event):
        deleteme =[]
        if event.type == MOUSEMOTION:
            x,y = event.pos
            for sprite in self.events["mouseover"]:
                if sprite.rect.collidepoint(x,y):
                    self.events["mouseover"][sprite]()
                elif sprite in self.events["mouseout"]:
                    self.events["mouseout"][sprite]()
                    del self.events["mouseout"][sprite]  
        if pygame.mouse.get_pressed()[0]:
            x,y = pygame.mouse.get_pos()
            for sprite in self.events["mouseover"]:
                if sprite.rect.collidepoint(x,y):
                    self.events["button1"][sprite]()