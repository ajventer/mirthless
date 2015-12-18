import pygame
from pygame.locals import *
from item import Item
from util import debug, editsnippet,default_text, load_yaml, realkey
from dialog import FloatDialog
from tempsprites import Tempsprites
from button import render_text, Button, TextInput, Dropdown, checkboxbtn, Label
from animatedsprite import AnimatedSprite
from messages import messages
import os
from flatteneddict import FlattenedDict

class YAMLEditor(FloatDialog, Tempsprites):
    def __init__(self, frontend, template, title):
        self.frontend = frontend
        self.title = title
        self.template = load_yaml('rules', template)
        self.rect = pygame.Rect(0,50, self.frontend.screensize.w, self.frontend.screensize.h - 250)
        FloatDialog.__init__(self, self.rect, frontend)
        Tempsprites.__init__(self)
        self.item = Item({})
        self.conditional_sprites = []
        self.baselayout()
        self.editorlayout()

    def baselayout(self):
        scale = self.frontend.mapscale
        self.previewsprite = AnimatedSprite(self.frontend.tilemaps, pygame.Rect(self.rect.x + 12, self.rect.y +12, scale, scale), self.item.animations, 8, 5)
        self._addtemp('previewsprite', self.previewsprite)
        self.animation = Dropdown(self.frontend.eventstack, 
            self.frontend.imagecache, 
            18,
            pygame.Rect(self.rect.x + 100, self.rect.y + 12, 200, 30),
            self.previewsprite.animations.keys(),
            choice=self.previewsprite.animation,
            onselect=self.changepreview)
        self._addtemp('selectanimation', self.animation)
        self.image.blit(render_text (self.title, size=32, color=(255,0,0)),(self.rect.w/2 - 20,10))
        split = self.frontend.imagecache['seperator']
        split = pygame.transform.smoothscale(split,(self.frontend.screensize.w -20, 10))
        self.image.blit(split,(10,60))
        save_btn = Button('Save Item', self.save, [], self.frontend.eventstack,self.frontend.imagecache, pos=(self.rect.x +  self.rect.w - 150,self.rect.y + self.rect.h - 50), layer=6)
        load_btn = Button('Load Item', self.load, [], self.frontend.eventstack,self.frontend.imagecache, pos=(self.rect.x +  10,self.rect.y + self.rect.h - 50), layer=6)
        self._addtemp('saveitem', save_btn)
        self._addtemp('loaditem', load_btn)

    def make_event(self, key):
        self.save()
        data = self.item.get(keyname, default_text)
        data = editsnippet(data)
        self.item.put(keyname,data)
        self.save()

    def editorlayout(self):
        debug('Building editor layout')
        self._rmtemp()
        self.baselayout()
        col, row = 0, 0
        for key in [i for i in self.template if '__Y' in i]:
            value = self.item.get(realkey(key),False)
            if value is False:
                self.item.put(realkey(key), self.template[key])            
        list1 = sorted([i for i in self.template if not i.startswith('conditional/') and not i.startswith('events/') and not '__Y' in i and not 'animations' in i])
        list3 = sorted([i for i in self.template if  i.startswith('events/')])
        list2 = sorted([i for i in self.conditional_sprites if not 'animations' in i])
        allkeys = list1 + list2 + list3
        for key in allkeys:
            x = col * 450 + self.rect.x + 10
            y = row * 33 + self.rect.y + 75
            if key.startswith('events/'):
                b = Button(realkey(key), 
                    self.make_event, 
                    [realkey(key)],
                    self.frontend.eventstack,
                    self.frontend.imagecache,
                    pos=(x ,y),
                    layer=6,
                    sendself=True,
                    fontsize=14)
                self._addtemp('%s_button' % key, b)
            else: 
                sprites = self.handlekey(key, x,y)
                for sprite in sprites:
                    self._addtemp('%s_%s' % (key,sprites.index(sprite)), sprite)
            row += 1
            if row * 33 + self.rect.y + 75 > self.rect.y + self.rect.h -75:
                row = 0
                col += 1

    def handlekey(self,key, x,y):
        keyname = realkey(key)
        has_label = True
        l = Label(keyname,(x,y))
        lsize = l.rect.w +10
        irect = pygame.Rect(x + lsize, y, 250, 20)
        value = self.item.get(keyname,'')
        if (key.startswith('conditional') or keyname == key) and not '__[' in str(self.template[key]):
            if not value:
                value = self.template[key]
            d = TextInput(
                irect,18, self.frontend.eventstack, prompt=str(value), clearprompt=False, layer=6, name=keyname)
        elif (key.startswith('conditional') or keyname == key) and '__[' in str(self.template[key]):
            liststr = self.template[key]
            items = liststr[3:-1].split(',')
            if sorted([i.upper() for i in items]) == ['FALSE','TRUE']:
                has_label = False
                d = checkboxbtn(keyname, 
                    self.valuechange, 
                    [],
                    self.frontend.eventstack,
                    self.frontend.imagecache, 
                    pos=(x,y), fontsize=16,
                    layer=6, name=key, sendself=True)
                if d.name in self.item():
                    d.checked = self.item.get(d.name)
                else:
                    d.checked = items[0].upper() == 'TRUE'
            else:
                d = Dropdown(
                    self.frontend.eventstack, 
                    self.frontend.imagecache, 
                    16,
                    irect, items,layer=8, 
                    choice=value, 
                    onselect=self.valuechange,
                    name=keyname,
                    sendself=True)
        if has_label:
            return [l, d]
        else:
            return [d]

    def updateconditionals(self):
        self.conditional_sprites = []
        conditional_keys = FlattenedDict(self.template).readsubtree('conditional')
        for key in conditional_keys:
            conditions = [k.replace('.','/') for k in key.split('/') if '=' in k]
            for condition in conditions:
                ckey, cval = condition.split('=')
                if self.item.get(ckey,False) == cval:
                    self.conditional_sprites.append('conditional/%s' % key)
        self.editorlayout()

    def valuechange(self, *args):
        k, v =  args[0].name, args[1]
        self.item.put(k, v)
        self.update_yaml()
        self.updateconditionals()

    def changepreview(self,choice):
        self.previewsprite.setanimation(choice)

    def update_yaml(self):
        for item in self.temp:
            sprite = item[0]
            try:
                k = realkey(sprite.name)
                v = sprite.value
                if k and v:
                    self.item.put(k, v)
            except:
                continue

    def save(self):
        self.update_yaml()
        dirname = None
        if self.title == 'Item Editor':
            dirname = 'items'
        elif self.title == 'NPC Editor':
            dirname = 'characters'
        if dirname:
            debug(dirname)
            filename = self.item.save_to_file(dirname)
            messages.error('Saved to %s' % os.path.basename(filename))

    def load(self):
        pass

    def delete(self):
        self._rmtemp()
        self.kill()
        self.restorebg()