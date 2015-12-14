import pygame
from pygame.locals import *
from util import debug, file_list, gamedir
from imagecache import ImageCache

class EventStack():
    def __init__(self):
        self.events = {
            "mouseover": {},
            "mouseout": {},
            "button1": {},
            "button2": {},
            "button3": {},
            "button1up": {},
            "wheelup": {},
            "wheeldown": {}
        }

    def register_event(self, event, sprite, method):
        self.events[event][sprite] = method

    def handle_event(self, event):
        deleteme =[]
        if event.type == pygame.QUIT:
            return True
        if event.type == MOUSEMOTION:
            x,y = event.pos
            for sprite in self.events["mouseover"]:
                if sprite.rect.collidepoint(x,y):
                    self.events["mouseover"][sprite]()
                    return
                elif sprite in self.events["mouseout"]:
                    self.events["mouseout"][sprite]()
                    del self.events["mouseout"][sprite]
                    return  
        if pygame.mouse.get_pressed()[0]:
            x,y = pygame.mouse.get_pos()
                 
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:      
                for sprite in self.events["button1"]:
                    if sprite.rect.collidepoint(x,y):
                        self.events["button1"][sprite]()               
            if event.button == 4:
                for sprite in self.events["wheelup"]:
                    if sprite.rect.collidepoint(x,y):
                        return self.events["wheelup"][sprite]()
            if event.button == 5:
                for sprite in self.events["wheeldown"]:
                    if sprite.rect.collidepoint(x,y):
                        return self.events["wheeldown"][sprite]()
