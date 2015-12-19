# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from util import debug, file_list, gamedir, file_path, imagepath
import os
import sys
from messagebox import MessageBox
from imagecache import ImageCache
from button import Button, render_text, scrn_print, ButtonArrow
from dialog import Dialog
from eventstack import EventStack
from mapview import Mapview
from frontend import Frontend
from messages import Messages, messages

imagecache = ImageCache()
eventstack = EventStack()
frontend = Frontend()

#Holds a single tilemap
class Tilemap(object):
    def __init__(self, filename):
        width, height = 16, 16
        #Credit - this came almost directly from the tutorial at: https://qq.readthedocs.org/en/latest/tiles.html
        image = imagecache(filename)
        image_width, image_height = image.get_size()
        tile_table = []
        tile_y = 0
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
                yield((x,y))

    def size(self):
        return (self.x, self.y)

    def table(self):
        return self.tile_table

    def tile(self, x, y, rot=0):
        if rot == 0:
            return self.tile_table[x][y]
        else:
            img = self.tile_table[x][y].copy()
            img = pygame.transform.rotate(img, float(rot))
            return img        

#Holds all the tilemaps in a collection
class Tilemaps(dict):
    def initialize(self):
        self.lastpage = 0
        keyfilter = list(imagecache.gui_map.keys())
        keyfilter.append('RPG_GUI_v1.png')
        keyfilter.append('wood background.png')
        keyfilter.append('paper background.png')
        keyfilter.append('landscape.png')
        for key in imagecache:
            if not key in keyfilter and not key.startswith('portrait_'):
                self[key] = Tilemap(key)
        return self

    #Get all tiles in a specific map sequentially
    def iterall(self, key):
        self.lastpage = sorted(list(self.keys())).index(key)
        tilemap = self[key]
        for image in tilemap.iterall():
            yield '%s:%s:%s' % (key, image[0], image[1])


    def tile(self,mapname,x,y, rot=0):
        return self[mapname].tile(x,y, rot)

    def get_by_path(self, path):
        backgroundpath = imagepath(path)
        return self.tile(backgroundpath[0], backgroundpath[1], backgroundpath[2], backgroundpath[3])

tilemaps = Tilemaps()

def get_screen(resx, resy, hardware, fullscreen):
    flags = DOUBLEBUF
    if hardware:
        flags = flags | HWSURFACE
    if fullscreen:
        flags = flags | FULLSCREEN

    return  pygame.display.set_mode((resx, resy), flags)


def initpygame(settings, caption, settingsfile):
    pygame.init()
    screen = get_screen(settings['res_x'], settings['res_y'], settings['hardware_buffer'], settings['fullscreen'])
    mode = 'game'
    if '--editor' in sys.argv:
        mode = 'editor'
        debug ('Loading game editor')    
    global imagecache
    imagecache = ImageCache()
    global frontend
    frontend = Frontend(mode=mode, settingsfile=settingsfile)
    global tilemaps
    tilemaps = Tilemaps()
    global messages
    imagecache.load()
    wallpaper = imagecache['landscape.png']
    wallpaper = pygame.transform.smoothscale(wallpaper, (settings["res_x"], settings["res_y"]))
    screen.blit(wallpaper,(0,0))    
    pygame.display.set_caption(caption)  
    frontend = Frontend(screen,imagecache,eventstack, tilemaps, mode=mode, settingsfile=settingsfile)
    messages = Messages(screen, eventstack)
    messages.error('Welcome to Mirthless')    
    tilemaps.initialize()

    return screen, frontend.screenlayout(), frontend





