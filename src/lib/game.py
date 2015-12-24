from player import Player
import os
from util import gamedir, debug
from tempsprites import Tempsprites
from dialog import FloatDialog
import pygame
from pygame.locals import *
from button import Button, Dropdown



class Game(Tempsprites):
    livecharacters = []
    def __init__(self, frontend):
        self.frontend = frontend
        Tempsprites.__init__(self)
        self.mainwindow()
        self.homedir = os.path.join(os.getenv('HOME'), '.mirthless')


    def mainwindow(self):
        rect = pygame.Rect(self.frontend.screensize.w/2 - 200,self.frontend.screensize.h/2 -200, 400, 400)
        main = FloatDialog(rect, self.frontend, layer=5)
        self._addtemp('MainMenu',main)
        newgame = Button('New Game',
            self.newgame,
            [],
            self.frontend.eventstack,
            self.frontend.imagecache,
            pos=(self.frontend.screensize.w/2 - 180,self.frontend.screensize.h/2 -180),
            layer=6,
            fontsize=16)
        self._addtemp('newgamebtn', newgame)

    def setsavedir(self, slot):
        self.slot = slot
        self.savedir = os.path.join(self.homedir,slot)
        debug('Game save directory:', self.savedir)
        if not os.path.exists(self.savedir):
            os.makedirs(self.savedir)
        gamedir.insert(0,self.savedir)

    def newgame(self):
        slot = str(len(os.listdir(self.homedir)))
        self.setsavedir(slot)
        self.player = Player({})
        self.player.savetoslot()
        self._rmtemp()


    def loadgame(self, slot):
        self.setsavedir(slot)
        self.player = Player(load_yaml('player','player.yaml'))
