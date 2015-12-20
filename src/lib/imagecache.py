import pygame
from pygame.locals import *
from util import debug, file_list, gamedir, load_yaml
import os



class ImageCache(dict):
    def load(self):
        for image in file_list('images', '*.png'):
            debug('Loading: ',image)
            key = os.path.basename(image)
            self[key] = pygame.image.load(image).convert_alpha()
        for image in file_list('portraits', '*.png'):
            key = 'portrait_%s' % os.path.basename(image)
            debug ('Loading: ', key)
            self[key] = pygame.image.load(image).convert_alpha()
        gui_map = load_yaml('images', 'gui_rects.yaml')
        for key in gui_map:
            rect = pygame.Rect(gui_map[key]['x'], gui_map[key]['y'], gui_map[key]['w'], gui_map[key]['h'])
            try:
                self.assign(key, 'RPG_GUI_v1.png', rect)
            except:
                debug(key, rect)
                raise
        self.gui_map = gui_map

    def __call__(self, key):
        return self[key]

    def assign(self, keyname, filename, rect):
        debug ('Loading subsurface ', keyname)
        self[keyname] = self[filename].subsurface(rect)
