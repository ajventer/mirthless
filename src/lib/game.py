from player import Player
import os
from util import gamedir, debug, load_yaml
from tempsprites import Tempsprites
from dialog import FloatDialog
import pygame
from pygame.locals import *
from button import Button, Dropdown, render_text, Label, TextInput, BlitButton
from item import Item



class Game(Tempsprites):
    livecharacters = []
    def __init__(self, frontend):
        self.frontend = frontend
        Tempsprites.__init__(self)
        self.homedir = os.path.join(os.getenv('HOME'), '.mirthless')
        self.player = Player({})
        self.cleanuplist = []
        template = load_yaml('rules','template_character.yaml')
        self.portrait = template['personal/portrait']

    def mainwindow(self):
        rect = self.frontend.screensize
        self.main = FloatDialog(rect, self.frontend, layer=5)
        self._addtemp('MainMenu',self.main)
        self.cleanuplist = []
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

    def clearwindow(self):
        for sprite in self.cleanuplist:
            if sprite in self.frontend.sprites:
                self.frontend.sprites[sprite].delete()
                del self.frontend.sprites[sprite]

    def _addtemp(self, title, obj):
        self.cleanuplist.append(title)
        Tempsprites._addtemp(self, title, obj)

    def newgame(self):
        self.clearwindow()
        self.player = Player({})
        self.main.image.blit(render_text('Nyrac City Jail: Prisoner Record',64),(20,20))
        firstnamelbl = Label('First name:', (20, 150), layer=6)
        self._addtemp('firstnamelbl', firstnamelbl)
        firstname = TextInput(pygame.Rect(100,150,100,30), 16, self.frontend.eventstack, layer=6)
        self._addtemp('firstname', firstname)
        lastnamelbl = Label('Last name:', (20, 190), layer=6)
        self._addtemp('lastnamelbl', lastnamelbl)
        lastname = TextInput(pygame.Rect(100,190,100,30), 16, self.frontend.eventstack, layer=6)
        self._addtemp('lastname', lastname)
        portrait = BlitButton(
                self.nextportrait, 
                [],
                self.frontend.eventstack,
                self.frontend.imagecache,
                self.portrait,
                pos=(210,150),
                scale=128,
                layer=7
                )
        self._addtemp('portrait', portrait)
        sexlbl = Label('Sex', (20,230))
        self._addtemp('sexlbl', sexlbl)
        sex = Dropdown(self.frontend.eventstack,
            self.frontend.imagecache,
            16,
            pygame.Rect(100,230,100,30),
            ['male','female'],
            layer=18)
        self._addtemp('sex', sex)
        pclasslbl = Label('Class:',(340,150))
        self._addtemp('pclasslbl', pclasslbl)
        playerclass = Dropdown(self.frontend.eventstack,
            self.frontend.imagecache,
            16,
            pygame.Rect(420,150,200,30),
            ['warrior:fighter','warrior:ranger','wizard:mage','rogue:thief','rogue:bard','priest:druid', 'priest:cleric'],
            layer=17)
        self._addtemp('playerclass', playerclass)
        racelbl = Label('Race:',(340,190))
        self._addtemp('racelbl',racelbl)
        race = Dropdown(self.frontend.eventstack,
            self.frontend.imagecache,
            16,
            pygame.Rect(420,190,200,30),
            ['human','elf','dwarf','half-elf','halfling','gnome','orc','goblin'],
            layer=16)
        self._addtemp('race', race)
        alignmentlbl = Label('Alignment', (340,230))
        self._addtemp('alignmentlbl', alignmentlbl)
        alignment = Dropdown(self.frontend.eventstack,
            self.frontend.imagecache,
            16,
            pygame.Rect(420,230,200,30),
            ['lawful-evil', 'neutral-evil', 'chaotic-evil'],
            layer=15)
        self._addtemp('alignment', alignment)
        create = Button('Create Character',
            self.createchar,
            [],
            self.frontend.eventstack,
            self.frontend.imagecache,
            pos=(210,350),
            layer=6,
            fontsize=16)
        self._addtemp('createchar', create)

    def createchar(self):
        def value(key):
            return self.frontend.sprites[key].value

        self.player.put('personal/name/first', value('firstname'))
        self.player.put('personal/name/last', value('lastname'))
        self.player.put('personal/portrait', self.portrait)
        self.player.put('personal/sex', value('sex'))
        playerclass = value('playerclass').split(':')
        debug(playerclass)
        self.player.put('class/parent', playerclass[0])
        self.player.put('class/class', playerclass[1])
        template = load_yaml('rules','template_character.yaml')
        for key in template:
            k = None
            if key.startswith('conditional/class.parent=%s/' %playerclass[0]):
                k = key.replace('conditional/class.parent=%s/' %playerclass[0],'')
            elif key.startswith('conditional/class.class=%s/' %playerclass[1]):
                k = key.replace('conditional/class.class=%s/' %playerclass[1],'')
            if k is not None and k != 'class.class':
                self.player.put(k, template[key])
            if key.startswith('inventory'):
                self.player.put(key, template[key])
            if key.startswith('__Yinventory'):
                k = key.replace('__Y', '')
                self.player.put(k, template[key])
        armor = Item(load_yaml('items', 'ab7ed2a7e93bae020aeaab893902702fc0727b0079ecd3a14aa4a57c.yaml'))
        armor = self.player.acquire_item(armor)
        self.player.equip_item(armor)
        debug(self.player())
        slot = str(len(os.listdir(self.homedir)))
        self.setsavedir(slot)
        self.player.savetoslot()
        self._rmtemp()

    def nextportrait(self):
        portraitlist = [i for i in self.frontend.imagecache.keys() if i.startswith('portrait_')]
        idx = portraitlist.index(self.portrait)
        idx += 1
        if idx >= len(portraitlist) -1:
            idx = 0
        self.portrait = portraitlist[idx]
        self.player.put('personal/portrait', self.portrait)
        self.newgame()

    def loadgame(self, slot):
        self.setsavedir(slot)
        self.player = Player(load_yaml('player','player.yaml'))
        debug(self.player.get_hash())
        self._rmtemp()
