import pygame
from pygame.locals import *
from item import Item
from npc import NPC
from util import debug, editsnippet,default_text, load_yaml, realkey, file_list
from dialog import FloatDialog, TileSelector, ContainerDialog
from tempsprites import Tempsprites
from button import render_text, Button, TextInput, Dropdown, checkboxbtn, Label, ButtonArrow, BlitButton
from animatedsprite import AnimatedSprite
from messages import messages
import os
from flatteneddict import FlattenedDict

class YAMLEditor(FloatDialog, Tempsprites):
    def __init__(self, frontend, template, title):
        self.frontend = frontend
        self.title = title
        self.template = load_yaml('rules', template)
        self.dirname = None
        if self.title == 'Item Editor':
            self.dirname = 'items'
        elif self.title == 'NPC Editor':
            self.dirname = 'characters'
        self.rect = pygame.Rect(0,50, self.frontend.screensize.w, self.frontend.screensize.h - 250)
        FloatDialog.__init__(self, self.rect, frontend)
        Tempsprites.__init__(self)
        if self.title == 'Item Editor':
            self.item = Item({})
        elif self.title == 'NPC Editor':
            self.item = NPC({},1)
        debug (self.item.animations)
        self.conditional_sprites = []
        self.currentanimation = None
        self.baselayout()
        self.editorlayout()

    def baselayout(self):
        self.lastlayer = 18
        self.image.blit(render_text (self.title, size=32, color=(255,0,0)),(self.rect.w/2 - 20,10))
        split = self.frontend.imagecache['seperator']
        split = pygame.transform.smoothscale(split,(self.frontend.screensize.w -20, 10))
        self.image.blit(split,(10,60))
        save_btn = Button('Save Item', self.save, [], self.frontend.eventstack,self.frontend.imagecache, pos=(self.rect.x +  self.rect.w - 150,self.rect.y + self.rect.h - 50), layer=6)
        load_btn = Button('Load Item', self.load, [], self.frontend.eventstack,self.frontend.imagecache, pos=(self.rect.x +  10,self.rect.y + self.rect.h - 50), layer=6)
        self._addtemp('saveitem', save_btn)
        self._addtemp('loaditem', load_btn)

    def make_event(self, sender, key):
        self.update_yaml()
        data = self.item.get(key, default_text)
        data.insert(0,'#%s' % key)
        data = editsnippet('\n'.join(data))
        self.item.put(key,data.split('\n'))
        self.update_yaml()

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
            x = col * 450 + self.rect.x + 15
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
        for key in sorted([i for i in self.conditional_sprites if 'animations' in i])+sorted(i for i in self.template if 'animations' in i and not 'conditional' in i):
            keyname = realkey(key)
            value = self.item.get(keyname,[])
            if not value:
                value = self.template[key]
            self.item.put(keyname, value)
        if self.item.animations:
            x = col * 450 + self.rect.x + 15
            y = row * 33 + self.rect.y + 75
            self.animation_editor(x,y)

    def animation_editor(self, x, y):
        l = Label('Animations', (x,y))
        y += l.rect.h
        self._addtemp('animations_label', l)
        scale = self.frontend.mapscale
        self.previewsprite = AnimatedSprite(self.frontend.tilemaps, pygame.Rect(x, y, scale, scale), self.item.animations, 8, 5)
        if self.currentanimation is None:
            self.currentanimation = self.previewsprite.animation
            self.previewsprite.pause = True
        else:
            self.previewsprite.setanimation(self.currentanimation)
            self.previewsprite.pause = self.paused.checked
        self._addtemp('previewsprite', self.previewsprite)
        self.animation = Dropdown(self.frontend.eventstack, 
            self.frontend.imagecache, 
            18,
            pygame.Rect(x + scale + 2, y, 200, 20),
            self.previewsprite.animations.keys(),
            choice=self.currentanimation,
            onselect=self.changeanimation,
            layer = self.lastlayer)
        self.lastlayer -= 1
        self._addtemp('selectanimation', self.animation)
        self.paused = checkboxbtn('Paused', 
                    self.togglepause, 
                    [],
                    self.frontend.eventstack,
                    self.frontend.imagecache, 
                    pos=(x + 150,y+22), fontsize=16,
                    layer=6, sendself=True)
        self.paused.checked = self.previewsprite.pause
        self._addtemp('AnimationPauseButton', self.paused)
        if self.paused.checked:
            nextframebtn = ButtonArrow(self.previewsprite.nextframe, 
                [],
                self.frontend.eventstack,
                self.frontend.imagecache,
                'right',
                pos=(x + scale,y+22),
                layer=6)
            self._addtemp('nextframebtn', nextframebtn)
            delframebtn = BlitButton(self.delframe, 
                [],
                self.frontend.eventstack,
                self.frontend.imagecache,
                'minusarrow',
                pos=(nextframebtn.rect.x + nextframebtn.rect.w,y+22),
                layer=6)
            self._addtemp('delete frame button',delframebtn)
            addframebtn = BlitButton(self.addframe,[],
                self.frontend.eventstack,
                self.frontend.imagecache,
                'plusarrow',
                pos=(delframebtn.rect.x + delframebtn.rect.w,y+22),
                layer=6)
            self._addtemp('add frame button',addframebtn)
    
    def togglepause(self,pausbtn, *args):
        self.previewsprite.pause = pausbtn.checked
        self.editorlayout()

    def changeanimation(self,animation):
        self.previewsprite.setanimation(animation)
        self.currentanimation = animation

    def delframe(self):
        key = 'animations/%s' % self.currentanimation
        idx = self.previewsprite.frame
        messages.warning('Deleted frame %s' % (idx))
        try:
            del self.item()[key][idx]
        except IndexError:
            debug('Tried to delete from an already empty list.')

    def addframe(self):
        self.updateconditionals()
        self._rmtemp()
        self.tileselector = TileSelector(self.rect, self.frontend, self.newframe,[])
        self._addtemp('ye_tileselector', self.tileselector)

    def newframe(self, framepath):
        self._rmtemp()
        key = 'animations/%s' % self.currentanimation
        idx = self.previewsprite.frame
        animations = self.item.get(key)
        animations.insert(idx, '%s:0' %framepath)
        self.item.put(key, animations)
        self.editorlayout()

    def listmanager(self,keyname, items):
        self._rmtemp()
        itemlist = []
        for itemfile in file_list('items'):
            itemfile = os.path.basename(itemfile)
            itemlist.append(Item(load_yaml('items',itemfile)))
        c = ContainerDialog(self.rect,
            self.frontend,
            keyname,
            7,
            items=itemlist,
            onselect=self.updatelist,
            onselect_parms=[keyname],
            animation='view',
            can_add=True,
            can_remove=True,
            can_select=False,
            addfrom=itemlist)
        self._addtemp('%s_listmanager' %keyname, c)
        #self.editorlayout()

    def updatelist(self, items, keyname):
        self.item.put(keyname, items)
        self.editorlayout()

    def handlekey(self,key, x,y):
        keyname = realkey(key)
        has_label = True
        l = Label(keyname,(x,y))
        lsize = l.rect.w +10
        irect = pygame.Rect(x + lsize, y, 250, 20)
        value = self.item.get(keyname,'')
        if not value:
            value = self.template[key]
            if str(value).startswith('__'):
                value = ''
        if isinstance(value, list):
            d = Button('Manage list', 
                self.listmanager,
                [keyname, value],
                self.frontend.eventstack,
                self.frontend.imagecache,
                pos=(irect.x, irect.y),
                layer=self._layer +1)
        elif (key.startswith('conditional') or keyname == key) and not '__[' in str(self.template[key]):
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
                if not value and len(items) == 1:
                    value = items[0]
                d = Dropdown(
                    self.frontend.eventstack, 
                    self.frontend.imagecache, 
                    16,
                    irect, items,layer=self.lastlayer, 
                    choice=value, 
                    onselect=self.valuechange,
                    name=keyname,
                    sendself=True)
                self.lastlayer -= 1
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
        debug(self.item())

    def save(self):
        self.update_yaml()
        if self.dirname:
            filename = self.item.save_to_file(self.dirname)
            messages.error('Saved to %s' % os.path.basename(filename))

    def load(self):
        pass

    def delete(self):
        self._rmtemp()
        self.kill()
        self.restorebg()