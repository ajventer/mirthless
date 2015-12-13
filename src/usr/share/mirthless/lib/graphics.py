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

    def message(self,s):
        self.messages.append(s.strip())

    def error(self,s):
        self.messages.append('{color 255, 0, 0; %s} ' % s.strip())
        debug('Error:', self.read())

def todo_event():
    frontend.messages.warning('Event not yet implemented')


class Frontend(object):
    game_menu = [
        ("Main Menu", todo_event),
        ("Inventory", todo_event),
        ("Spellbook", todo_event),
        ("About", todo_event),
        ("Quit", sys.exit)
    ]
    editor_menu = [
        ("Main Menu", todo_event),
        ("Items and spells", todo_event),
        ("NPCs and Monsters", todo_event),
        ("Quests", todo_event),
        ("Quit", sys.exit)
    ]
    def __init__(self,screen=None, mode='game'):
        self.mode = mode
        self.messages = Messages(pygame.Rect(0,0,0,0))
        if screen:
            self.screen = screen
            self.screensize = self.screen.get_rect()
            dialogx = (self.screensize.w /2)+50
            self.mapw = int(self.screensize.w /2)-50
            self.mapscale = int(self.mapw /20)
            debug ("Mapwidth: ", self.mapw, "Tile size", self.mapscale)
            self.rightwindow_rect = pygame.Rect(dialogx, 75, self.screensize.w - 100 -dialogx, self.screensize.h - 300)
            self.messagebox_rect = pygame.Rect(0,self.screensize.h - 190,self.screensize.w, self.screensize.h)
            self.messages = Messages(self.messagebox_rect)
            self.layout = {
                "header": [],
                "sprites": [],
                "dialog": None
                } 
            self.mb = MessageBox(self.messagebox_rect)

    def screenlayout(self):
        #Header:
        screensize = self.screen.get_rect()
        woodbg = imagecache['wood background.png']
        woodbg = pygame.transform.smoothscale(woodbg, (self.screensize.w, 50))
        seperator = imagecache['seperator']
        seperator = pygame.transform.smoothscale(seperator, (self.screensize.w, 20))
        self.screen.blit(woodbg, (0,0))

        self.screen.blit(seperator, (0,42))
        debug ('Game mode is', self.mode)
        if self.mode == 'game':
            menu = self.game_menu
        else:
            menu = self.editor_menu
        for button in menu:
            self.layout["sprites"].append(Button(button[0], button[1], eventstack,imagecache, (menu.index(button) * 220,5)))
      
        #Messagebox
        self.screen.blit(seperator, (0,self.screensize.h -205))
        mb_up = ButtonArrow(self.messages.scrollup, eventstack,imagecache, 'up', pos=(screensize.w - 27,screensize.h-190))
        mb_down = ButtonArrow(self.messages.scrolldown, eventstack,imagecache, 'down', pos=(screensize.w - 27,screensize.h-100))
        self.layout['sprites'].append(mb_down)
        self.layout['sprites'].append(mb_up)
        #Mainwindow
        #20+10+640+10+20
        self.layout['sprites'].append(Dialog(self.rightwindow_rect, imagecache))

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
        sprites.clear(self.screen, self.background)
        dirty = sprites.draw(self.screen)
        pygame.display.update(dirty)

#Holds a single tilemap
class Tilemap(object):
    def __init__(self, filename):
        width, height = 16, 16
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


    def iterall(self):
        for x, row in enumerate(self.tile_table):
            for y, tile in enumerate(row):
                yield(tile)

    def size(self):
        return (self.x, self.y)

    def table(self):
        return self.tile_table

    def tile(self, x, y):
        return self.tile_table[x][y]

#Holds all the tilemaps in a collection
class Tilemaps(dict):
    def initialize(self):
        keyfilter = list(imagecache.gui_map.keys())
        keyfilter.append('RPG_GUI_v1.png')
        keyfilter.append('wood background.png')
        keyfilter.append('paper background.png')
        for key in imagecache:
            if not key in keyfilter:
                self[key] = Tilemap(key)
        return self

    #Get all tiles in a specific map sequentially
    def iterall(self, key):
        return self[key].iterall

    def tile(self,mapname,x,y):
        return self[mapname].tile(x,y)



frontend = Frontend()
tilemaps = Tilemaps()

def get_screen(resx, resy, hardware, fullscreen):
    flags = DOUBLEBUF
    if hardware:
        flags = flags | HWSURFACE
    if fullscreen:
        flags = flags | FULLSCREEN

    return  pygame.display.set_mode((resx, resy), flags)


def initpygame(settings, caption):
    mode = 'game'
    if '--editor' in sys.argv:
        mode = 'editor'
        debug ('Loading game editor')    
    global imagecache
    imagecache = ImageCache()
    global frontend
    frontend = Frontend(mode=mode)
    global tilemaps
    tilemaps = Tilemaps()
    pygame.init()
    screen = get_screen(settings['res_x'], settings['res_y'], settings['hardware_buffer'], settings['fullscreen'])
    imagecache.load()
    wallpaper = imagecache['landscape.png']
    wallpaper = pygame.transform.smoothscale(wallpaper, (settings["res_x"], settings["res_y"]))
    screen.blit(wallpaper,(0,0))    
    pygame.display.set_caption(caption)  
    frontend = Frontend(screen, mode=mode)
    frontend.messages.error('Welcome to Mirthless')
    debug(frontend.messages.read())
    tilemaps.initialize()

    return screen, frontend.screenlayout(), frontend


class Mapview(object):
    #Remember maps are maximum 30x30 tiles
    def __init__(self, ):
        self.tilemap = tilemap
        self.surface = pygame.Surface((w * tilemap.w, h * tilemap.h))







