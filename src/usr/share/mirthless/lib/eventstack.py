import pygame
from pygame.locals import *
from util import debug, file_list, gamedir
from imagecache import ImageCache
from util import make_hash

class EventStack():
    def __init__(self):
        self.events ={
            "mouseover": {},
            "mouseout": {},
            "button1": {},
            "button2": {},
            "button3": {},
            "button1up": {},
            "wheelup": {},
            "wheeldown": {},
            "keydown": {},
        }

    def register_event(self, event, sprite, method):
        id = make_hash()
        self.events[event][sprite] = (method, id)
        return id 

    def unregister_event(self, hash):
        delme = []
        for k in self.events:
            for sprite in self.events[k]:
                if self.events[k][sprite][1] == hash:
                    delme.append((k,sprite))
        for event in delme:
            debug('Deregistering event %s for %s' % (event[0], event[1]))
            del self.events[event[0]][event[1]]

    def get_events(self, key):
        #Size-change safe index
        eventlist = [i for i in list(self.events[key].keys())]
        eventlist.sort(key=lambda x: x._layer, reverse=True)
        return eventlist

    def handle_event(self, event):
        handlers = []
        deleteme =[]
        if event.type == KEYDOWN:
            x,y = pygame.mouse.get_pos()
            for sprite in self.get_events("keydown"):
                if sprite.rect.collidepoint(x,y):
                    self.events["keydown"][sprite][0](event)
                    return
        if event.type == pygame.QUIT:
            return True
        if event.type == MOUSEMOTION:
            x,y = event.pos
            for sprite in self.get_events("mouseover"):
                if sprite.rect.collidepoint(x,y):
                    self.events["mouseover"][sprite][0]((x,y))
                    return
                elif sprite in self.events["mouseout"]:
                    self.events["mouseout"][sprite][0]((x,y))
                    del self.events["mouseout"][sprite]
                    return                  
        if event.type == pygame.MOUSEBUTTONUP:
            x, y = event.pos
            if event.button == 1:      
                for sprite in self.get_events("button1"):
                    if sprite.rect.collidepoint(x,y):
                        self.events["button1"][sprite][0]((x,y))
                        return
            if event.button == 4:
                for sprite in self.get_events("wheelup"):
                    if sprite.rect.collidepoint(x,y):
                        self.events["wheelup"][sprite][0]()
            if event.button == 5:
                for sprite in self.get_events("wheeldown"):
                    if sprite.rect.collidepoint(x,y):
                        self.events["wheeldown"][sprite][0]()
                        return
