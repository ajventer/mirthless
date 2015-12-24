import pygame
from pygame.locals import *
from util import debug, file_list, gamedir, file_path
import os
import sys
from messagebox import MessageBox
from imagecache import ImageCache
from button import Button, render_text, scrn_print, ButtonArrow
from dialog import Dialog, FloatDialog, SettingsDialog
from eventstack import EventStack
from mapview import Mapview
from messages import messages
from yaml_editor import YAMLEditor
from inventory import Inventory
from game import Game

def todo_event():
    messages.warning('Event not yet implemented')

class Frontend(object):
    def __init__(self,screen=None, imagecache=None, eventstack=None, tilemaps=None, mode='game', settingsfile='/etc/mirthless/mirthless.cfg'):
        self.mode = mode
        self.settingsfile = settingsfile
        if screen:
            self.sprites = {}
            self.imagecache = imagecache
            self.eventstack = eventstack
            self.screen = screen
            self.screensize = self.screen.get_rect()
            self.tilemaps = tilemaps
            self.mapw = int(self.screensize.w /2)-180
            dialogx = self.mapw+100
            self.maprect = pygame.Rect(50,65, self.mapw, self.mapw)
            self.mapscale = int(self.mapw /20)
            debug ("Mapwidth: ", self.mapw, "Tile size", self.mapscale)
            self.rightwindow_rect = pygame.Rect(dialogx, 65, self.screensize.w - 50 -dialogx, self.screensize.h - 300)
            self.messagebox_rect = pygame.Rect(0,self.screensize.h - 190,self.screensize.w, self.screensize.h)
            self.bigwindowrect = pygame.Rect(50,65, self.screensize.w -100, self.screensize.h - 300)
            self.layout = {
                "header": [],
                "dialog": None
                } 
            self.sprites['mb'] = MessageBox(messages, self.messagebox_rect,  self)
            if self.mode != 'editor':
                self.game = Game(self)
                self.game_menu = [
                    ("Quit", [sys.exit]),
                    ("Map", [self.mainmenu, Mapview, self, 'mapview']),
                    ("Inventory", [self.mainmenu, Inventory, self.bigwindowrect, self,self.game.player,5,'inventory']),
                    ("Spellbook", [todo_event]),
                    ("Journal", [todo_event]),
                    ("Settings", [self.settings]),
                    ("About", [todo_event]),
                ]
            self.mainmenuitems = []
            self.editor_menu = [
            ("Quit", [self.quit]),
            ("Maps", [self.mainmenu, Mapview, self, 'mapview']),
            ("Items/spells", [self.mainmenu, YAMLEditor, self, 'template_item.yaml', 'Item Editor']),
            ("NPCs", [self.mainmenu, YAMLEditor, self, 'template_character.yaml', 'NPC Editor']),
            ("Quests", [todo_event]),
            ("Settings", [self.mainmenu, SettingsDialog, pygame.Rect(self.screensize.w/2 - 300,self.screensize.h/2 -200,600,400), self, 'Settings']),
            ] 

    def quit(self,*args):
        sys.exit()

    def mainmenu(self, *args):
        obj = args[0]
        key = args[-1]
        args = args[1:]
        for item in self.mainmenuitems:
            if item[1] != key and item[1] in self.sprites:
                self.sprites[item[1]].delete()
                del self.sprites[item[1]]
        if key in self.sprites:
            self.sprites[key].delete()
            del self.sprites[key]
        else:
            self.mainmenuitems = []
            item = obj(*args)
            self.mainmenuitems.append((item, key))
            self.sprites[key] = item

    def settings(self):
        if not 'settingsmenu' in self.sprites:
            settings = SettingsDialog(pygame.Rect(self.screensize.w/2 - 300,self.screensize.h/2 -200,600,400), self,layer=20)
            self.eventstack.unregister_event(self.mapview.clickhash)
            self.sprites['settingsmenu'] = settings 
        else:
            self.mapview.registerclickevent()
            self.sprites['settingsmenu'].delete()

    def screenlayout(self):
        #Header:
        screensize = self.screen.get_rect()
        woodbg = self.imagecache['wood background.png']
        woodbg = pygame.transform.smoothscale(woodbg, (self.screensize.w, 50))
        seperator = self.imagecache['seperator']
        seperator = pygame.transform.smoothscale(seperator, (self.screensize.w, 20))
        self.screen.blit(woodbg, (0,0))
        self.screen.blit(seperator, (0,42))
        debug ('Game mode is', self.mode)
        if self.mode == 'game':
            menu = self.game_menu
        else:
            menu = self.editor_menu
        buttonplacement = self.screensize.w / len(menu)
        for button in menu:
            self.sprites['%s_button' % button[0]] = Button(button[0], button[1][0],button[1][1:], self.eventstack, self.imagecache, (menu.index(button) * buttonplacement,5))
      
        self.screen.blit(seperator, (0,self.screensize.h -205))

        self.background = self.screen.copy()
        self.game.mainwindow()
        return self.screen, self.background


    def draw(self):
        screensize = self.screen.get_rect()
        sprites = pygame.sprite.LayeredUpdates()
        for sprite in self.sprites:
            sprites.add(self.sprites[sprite])
        sprites.clear(self.screen, self.background)
        sprites.update()
        dirty = sprites.draw(self.screen)
        pygame.display.update(dirty)
