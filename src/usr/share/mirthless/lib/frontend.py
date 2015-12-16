import pygame
from pygame.locals import *
from util import debug, file_list, gamedir, file_path
import os
import sys
from messagebox import MessageBox
from imagecache import ImageCache
from button import Button, render_text, scrn_print, ButtonArrow
from dialog import Dialog, FloatDialog
from eventstack import EventStack
from mapview import Mapview
from messages import messages

def todo_event():
    messages.warning('Event not yet implemented')

class Frontend(object):
    def __init__(self,screen=None, imagecache=None, eventstack=None, tilemaps=None, mode='game'):
        self.game_menu = [
        ("Main Menu", todo_event),
        ("Inventory", todo_event),
        ("Spellbook", todo_event),
        ("About", todo_event),
        ("Quit", sys.exit)
        ]
        self.editor_menu = [
        ("Main Menu", self.editormain),
        ("Items/spells", todo_event),
        ("NPCs", todo_event),
        ("Quests", todo_event),
        ("Quit", sys.exit)
        ]
        self.mode = mode
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
            self.layout = {
                "header": [],
                "dialog": None
                } 
            self.sprites['mb'] = MessageBox(self.messagebox_rect, messages, self)

    def editormain(self):
        mainmenu = FloatDialog(pygame.Rect(100,100,100,100), self.imagecache)
        self.sprites['mainmenu'] = mainmenu

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
        for button in menu:
            self.sprites[button[0]] = Button(button[0], button[1], [], self.eventstack, self.imagecache, (menu.index(button) * 220,5))
      
        #Messagebox
        self.screen.blit(seperator, (0,self.screensize.h -205))
        #Mainwindow
        #20+10+640+10+20
        dialog = Dialog(self.rightwindow_rect, self.imagecache)
        self.screen.blit(dialog.image, (self.rightwindow_rect.x, self.rightwindow_rect.y))
        self.sprites['rightwindow'] = dialog

        mapview = Mapview(self)
        mapview.loadmap({})
        self.screen.blit(mapview.image, (50,65))

        self.background = self.screen.copy()
        return self.screen, self.background


    def draw(self):
        screensize = self.screen.get_rect()
        sprites = pygame.sprite.LayeredUpdates()
        #self.sprites['mb'].clear(self.screen, self.background)
        #self.sprites['mb'].image
        #self.screen.blit(g, r)
        for sprite in self.sprites:
            sprites.add(self.sprites[sprite])
        sprites.clear(self.screen, self.background)
        dirty = sprites.draw(self.screen)
        pygame.display.update(dirty)
