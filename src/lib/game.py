from player import Player
import os
from util import gamedir, debug, load_yaml
from tempsprites import Tempsprites
from dialog import FloatDialog
import pygame
from pygame.locals import *
from button import Button, Dropdown, render_text, Label



class Game(Tempsprites):
    livecharacters = []
    def __init__(self, frontend):
        self.frontend = frontend
        Tempsprites.__init__(self)
        self.homedir = os.path.join(os.getenv('HOME'), '.mirthless')
        self.player = Player({})


    def mainwindow(self):
        rect = self.frontend.screensize
        main = FloatDialog(rect, self.frontend, layer=5)
        self._addtemp('MainMenu',main)
        newgame = Button('New Game',
            self.newgame,
            [],
            self.frontend.eventstack,
            self.frontend.imagecache,
            pos=(20,20),
            layer=6,
            fontsize=16)
        self._addtemp('newgamebtn', newgame)
        loadgamelbl = Label('Load Game:',(20,50), layer=6)
        self._addtemp('loadgamelbl', loadgamelbl)
        rect = pygame.Rect(20,80, 300, 30)
        loadslots = Dropdown(
            self.frontend.eventstack,
            self.frontend.imagecache,
            16,
            rect,
            os.listdir(self.homedir),
            layer=6,
            onselect=self.loadgame)
        self._addtemp('loadgame', loadslots)


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
        for sprite in ['newgamebtn', 'loadgamelbl', 'loadgame']:
            if sprite in self.frontend.sprites:
                self.frontend.sprites[sprite].delete()
                del self.frontend.sprites[sprite]


    def loadgame(self, slot):
        self.setsavedir(slot)
        self.player = Player(load_yaml('player','player.yaml'))
        debug(self.player.get_hash())
        self._rmtemp()
