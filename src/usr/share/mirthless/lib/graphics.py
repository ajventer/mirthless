# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from util import debug, file_list, readyaml, gamedir
import os
import sys
from messagebox import MessageBox

class Campaign(object):
    def ___init__(self,screen):
        #Temporary class until new game class is done
        pass
    def warning(*args):
        pass

    def message(*args):
        pass

    def error(*args):
        pass


class Frontend(object):
    campaign = Campaign()
    def __init__(self,screen=None):
        if screen:
            self.screen = screen
            self.screensize = self.screen.get_rect()
            self.layout = {
                "header": [],
                "mainwindow": [],
                "rightmenu": [],
                "messagebox":  '',
                "dialog": None
                } 
            self.mb = MessageBox(pygame.Rect(0,self.screensize.h - 190,self.screensize.w, self.screensize.h))

    def background(self):
        #Header:
        screensize = self.screen.get_rect()
        woodbg = imagecache['wood background.png']
        woodbg = pygame.transform.smoothscale(woodbg, (self.screensize.w, 50))
        seperator = imagecache['seperator']
        seperator = pygame.transform.smoothscale(seperator, (self.screensize.w, 20))
        self.screen.blit(woodbg, (0,0))

        self.screen.blit(seperator, (0,50))
        
        #Messagebox
        self.screen.blit(seperator, (0,self.screensize.h -200))


        #Mainwindow
        self.background = self.screen.copy()
        return self.screen, self.background

    def draw(self):
        screensize = self.screen.get_rect()
        sprites = pygame.sprite.RenderUpdates()
        self.mb.clear(self.screen, self.background)
        g, r = self.mb.image(self.layout['messagebox'].replace('\n','/n'))
        self.screen.blit(g, r)
        for sprite in self.layout['header']:
            sprites.add(sprite)
        sprites.clear(self.screen, self.background)
        dirty = sprites.draw(self.screen)
        pygame.display.update(dirty)



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

class ImageCache(dict):
    def __init__(self):
        super(dict, self).__init__() 

    def load(self):
        for image in file_list('images', '*.png'):
            debug('Loading: ',image)
            key = os.path.basename(image)
            self[key] = pygame.image.load(image).convert()
        gui_map = readyaml('images', 'gui_rects.yaml')
        for key in gui_map:
            rect = pygame.Rect(gui_map[key]['x'], gui_map[key]['y'], gui_map[key]['w'], gui_map[key]['h'])
            self.assign(key, 'RPG_GUI_v1.png', rect)


    def __call__(self, key):
        return self[key]

    def assign(self, keyname, filename, rect):
        debug ('Loading subsurface ', keyname)
        self[keyname] = self[filename].subsurface(rect)



imagecache = ImageCache()
frontend = Frontend()

def initpygame(settings, caption):
    global imagecache
    global frontend
    pygame.init()
    screen = get_screen(settings['res_x'], settings['res_y'], settings['hardware_buffer'], settings['fullscreen'])
    imagecache.load()
    wallpaper = imagecache['landscape.png']
    wallpaper = pygame.transform.smoothscale(wallpaper, (settings["res_x"], settings["res_y"]))
    screen.blit(wallpaper,(0,0))    
    pygame.display.set_caption(caption)  
    frontend = Frontend(screen)
    frontend.layout['messagebox'] = """
    This is a multiline messagebox where system messages to the user
    will be displayed. The system supports quite a lot of very cool features here.
    Even clickable links"""
    return screen, frontend.background(), frontend

class Tilemap(object):
    def __init__(self, filename, width, height):
        #Credit - this came almost directly from the tutorial at: https://qq.readthedocs.org/en/latest/tiles.html

        image = imagecache(filename)
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, image_width/width):
            line = []
            tile_table.append(line)
            for tile_y in range(0, image_height/height):
                rect = (tile_x*width, tile_y*height, width, height)
                line.append(image.subsurface(rect))
        self.tile_table = tile_table
        self.x = tile_x
        self.y = tile_y
        self.w = width
        self.h = height


    def size(self):
        return (self.x, self.y)

    def table(self):
        return self.tile_table

    def tile(self, x, y):
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

class Button(pygame.sprite.DirtySprite):
    restcolor = (212,161,144)
    highcolor = (161,212,144)
    clickcolor = (194,144,212)
    def __init__(self, label, onclick, eventstack, pos=(0,0)):
        super(pygame.sprite.DirtySprite, self).__init__()
        button_rest = imagecache['button_rest']
        button_hi = imagecache['button_hi']
        button_click = imagecache['button_click']
        self.pos = pos
        self.onclick = onclick
        self.label = render_text (label, size=32, color=(0,0,0))

        labelrect = self.label.get_rect()
        
        self.button_rest = pygame.transform.smoothscale(button_rest, (labelrect.w + 20, labelrect.h + 12))
        self.button_rest.blit(self.label,(10,6))

        self.button_hi = pygame.transform.smoothscale(button_hi, (labelrect.w + 20, labelrect.h + 12))
        self.button_hi.blit(self.label,(10,6))

        self.button_click = pygame.transform.smoothscale(button_click, (labelrect.w + 20, labelrect.h + 12))
        self.button_click.blit(self.label,(10,6))


        rect = self.button_rest.get_rect()

        self.eventstack = eventstack

        self.rect = pygame.Rect(pos[0], pos[1], rect.w, rect.h)

        self.eventstack.register_event("mouseover", self, self.mouseover)
        self.eventstack.register_event("button1", self, self.click)

        self.mouseout()

    def mouseover(self):
        self.image = self.button_hi
        self.image.convert()
        self.eventstack.register_event("mouseout", self, self.mouseout)


    def mouseout(self):
        self.image = self.button_rest
        self.image.convert()
     
    def click(self):
        self.image = self.button_click
        self.image.convert()
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





