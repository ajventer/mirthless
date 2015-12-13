# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from util import debug, file_list, readyaml, gamedir, file_path
import os
import sys
from messagebox import MessageBox
from imagecache import ImageCache
from button import Button, render_text, scrn_print, ButtonArrow
from dialog import Dialog
from eventstack import EventStack

imagecache = ImageCache()
eventstack = EventStack()


class Messages(object):
    messages=[]
    messageindex = 0
    def __init__(self, rect):
        global eventstack
        self.rect = rect
        debug('Registering wheel handlers')
        eventstack.register_event("wheelup", self, self.scrollup) 
        eventstack.register_event("wheeldown", self, self.scrolldown)
        debug(eventstack.events["wheelup"])

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
        self.messages.append('{color 125, 0, 0; %s} ' % s.strip())

    def message(self,s):
        self.messages.append(s.strip())

    def error(self,s):
        self.messages.append('{color 255, 0, 0; %s} ' % s.strip())
        debug('Error:', self.read())

class Frontend(object):
    def __init__(self,screen=None):
        if screen:
            self.screen = screen
            self.screensize = self.screen.get_rect()
            dialogx = self.screensize.w /2
            if dialogx < 700:
                dialogx = 700
            self.rightwindow_rect = pygame.Rect(dialogx, 75, self.screensize.w - 100 -dialogx, self.screensize.h - 300)
            self.messagebox_rect = pygame.Rect(0,self.screensize.h - 190,self.screensize.w, self.screensize.h)
            self.messages = Messages(self.messagebox_rect)
            self.layout = {
                "header": [],
                "sprites": [],
                "rightwindow": Dialog(self.rightwindow_rect, imagecache),
                "dialog": None
                } 
            self.mb = MessageBox(self.messagebox_rect)

    def background(self):
        #Header:
        screensize = self.screen.get_rect()
        woodbg = imagecache['wood background.png']
        woodbg = pygame.transform.smoothscale(woodbg, (self.screensize.w, 50))
        seperator = imagecache['seperator']
        seperator = pygame.transform.smoothscale(seperator, (self.screensize.w, 20))
        self.screen.blit(woodbg, (0,0))

        self.screen.blit(seperator, (0,42))
        quit_button = Button("Quit", sys.exit, eventstack,imagecache, (5,5))
        self.layout['sprites'].append(quit_button)
        
        #Messagebox
        self.screen.blit(seperator, (0,self.screensize.h -205))
        mb_up = ButtonArrow(self.messages.scrollup, eventstack,imagecache, 'up', pos=(screensize.w - 27,screensize.h-190))
        mb_down = ButtonArrow(self.messages.scrolldown, eventstack,imagecache, 'down', pos=(screensize.w - 27,screensize.h-100))
        self.layout['sprites'].append(mb_down)
        self.layout['sprites'].append(mb_up)
        #Mainwindow
        #20+10+640+10+20

        self.background = self.screen.copy()
        return self.screen, self.background

    def draw(self):
        screensize = self.screen.get_rect()
        sprites = pygame.sprite.RenderUpdates()
        self.mb.clear(self.screen, self.background)
        g, r = self.mb.image(self.messages.read().replace('\n','/n'))
        self.screen.blit(g, r)
        for sprite in self.layout['sprites']:
            sprites.add(sprite)
        sprites.add(self.layout['rightwindow'])
        sprites.clear(self.screen, self.background)
        dirty = sprites.draw(self.screen)
        pygame.display.update(dirty)


frontend = Frontend()

def get_screen(resx, resy, hardware, fullscreen):
    flags = DOUBLEBUF
    if hardware:
        flags = flags | HWSURFACE
    if fullscreen:
        flags = flags | FULLSCREEN

    return  pygame.display.set_mode((resx, resy), flags)


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
    frontend.messages.error('Welcome to Mirthless')
    debug(frontend.messages.read())
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



class Mapview(object):
    def __init__(self, tilemap, w, h):
        self.tilemap = tilemap
        self.surface = pygame.Surface((w * tilemap.w, h * tilemap.h))

    def set_bg(self, x, y, tx, ty):
        pos_x = x * self.tilemap.w
        pos_y = y * self.tilemap.h
        debug ('Blitting %sx%s to position %sx%s' % (tx,ty,pos_x,pos_y))
        self.surface.blit(self.tilemap.tile(tx, ty), (pos_x, pos_y))





