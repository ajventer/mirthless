# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from util import debug


def get_screen(resx, resy, hardware, fullscreen):
    flags = DOUBLEBUF
    if hardware:
        flags = flags | HWSURFACE
    if fullscreen:
        flags = flags | FULLSCREEN

    return  pygame.display.set_mode((resx, resy), flags)


def render_text (text, size=32, color=(0,0,0)):
    font = pygame.font.Font(None, size)
    rendered = font.render(str(text), 1, color)
    return rendered 

def scrn_print(surface, text, x, y, size=32, color=(0,0,0)):
    rendered_text = render_text(text, size=size, color=color)
    textpos = rendered_text.get_rect()
    textpos.centerx = x
    textpos.centery = y      
    surface.blit(rendered_text, textpos)

class Tilemap(object):
    def __init__(self, filename, width, height, scale=False):
        #Credit - this came almost directly from the tutorial at: https://qq.readthedocs.org/en/latest/tiles.html

        image = pygame.image.load(filename).convert()
        image_width, image_height = image.get_size()
        if scale:
            image_width = image_width *2
            image_height = image_height *2
        tile_table = []
        for tile_x in range(0, image_width/width):
            line = []
            tile_table.append(line)
            for tile_y in range(0, image_height/height):
                rect = (tile_x*width, tile_y*height, width, height)
                line.append(image.subsurface(rect))
        self.tile_table = tile_table
        self.scale = scale
        self.x = tile_x
        self.y = tile_y
        self.w = width
        self.h = height


    def size(self):
        return (self.x, self.y)

    def table(self):
        return self.tile_table

    def tile(self, x, y):
        if self.scale:
            image = self.tile_table[x][y]
            image = pygame.transform.scale2x(image)
            return image
        return self.tile_table[x][y]

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
        else:
            for sprite in self.events["button1up"]:
                self.events["button1up"][sprite]()
                deleteme.append(sprite)
            for sprite in deleteme:
                del self.events["button1up"][sprite]



class Button(pygame.sprite.DirtySprite):
    restcolor = (212,161,144)
    highcolor = (161,212,144)
    clickcolor = (194,144,212)
    def __init__(self, label, onclick, eventstack, pos=(0,0)):
        super(pygame.sprite.DirtySprite, self).__init__()
        self.pos = pos
        self.onclick = onclick
        self.label = render_text (label, size=32, color=(0,0,0))
        rect = self.label.get_rect()
        self.surface = pygame.Surface((rect.w * 3 + 9, rect.h + 3))
        self.surface.fill((0,0,0))
        self.rest_rect = pygame.Rect(0,0,rect.w +3,rect.h +3)
        self.hi_rect = pygame.Rect(rect.w +3,0,rect.w +3,rect.h +3)
        self.click_rect = pygame.Rect(rect.w*2 +6,0, rect.w +3,rect.h)
        debug("Rest_rect", self.rest_rect)
        debug("Hi_rect", self.hi_rect)
        debug("Click_rect", self.click_rect)
        self.surface.fill(self.restcolor, self.shadowed(self.rest_rect))
        self.surface.fill(self.highcolor, self.shadowed(self.hi_rect))
        self.surface.fill(self.clickcolor, self.click_rect)
        self.surface.blit(self.label,(0,0))
        self.surface.blit(self.label,(self.hi_rect.x, 0))
        self.surface.blit(self.label,(self.click_rect.x, 0))
        self.eventstack = eventstack

        self.rect = pygame.Rect(pos[0], pos[1], rect.w, rect.h)
        debug("Width",self.rect.w)

        self.eventstack.register_event("mouseover", self, self.mouseover)
        self.eventstack.register_event("button1", self, self.click)

        self.mouseout()

    def shadowed(self,rect):
        return pygame.Rect(rect.x, rect.y, rect.w -3, rect.h -3)

    def mouseover(self):
        self.image = self.surface.subsurface(self.hi_rect)
        self.eventstack.register_event("mouseout", self, self.mouseout)


    def mouseout(self):
        self.image = self.surface.subsurface(self.rest_rect)
     
    def click(self):
        self.image = self.surface.subsurface(self.click_rect)
        self.eventstack.register_event("button1up", self, self.mouseout)
        if self.onclick is not None:
            self.onclick()



class Mapview(object):
    def __init__(self, tilemap, w, h):
        self.tilemap = tilemap
        self.surface = pygame.Surface((w * tilemap.w, h * tilemap.h))

    def set_bg(self, x, y, tx, ty):
        pos_x = x * self.tilemap.w
        pos_y = y * self.tilemap.h
        debug ('Blitting %sx%s to position %sx%s' % (tx,ty,pos_x,pos_y))
        self.surface.blit(self.tilemap.tile(tx, ty), (pos_x, pos_y))








