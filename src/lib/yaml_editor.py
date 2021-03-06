import pygame
from pygame.locals import *
from item import Item
from npc import NPC
from util import debug, editsnippet,default_text, load_yaml, realkey, file_list, make_hash
from dialog import FloatDialog, TileSelector, ContainerDialog
from tempsprites import Tempsprites
from button import render_text, Button, TextInput, Dropdown, checkboxbtn, Label, ButtonArrow, BlitButton
from animatedsprite import AnimatedSprite
from messages import messages
import os
from flatteneddict import FlattenedDict
from inventory import Inventory

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
        self.rect = self.frontend.bigwindowrect
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
        if key.startswith('event'):
            default = default_text
        else:
            default = ['']
        data = self.item.get(key, default)
        if not key in data[0]:
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
        list1 = sorted([i for i in self.template if not i.startswith('conditional/') and not i.startswith('events/') and not '__Y' in i and not 'animations' in i and i != 'personal/portrait'])
        list3 = sorted([i for i in self.template if  i.startswith('events/')])
        list2 = sorted([i for i in self.conditional_sprites if not 'animations' in i])
        if [i for i in self.template if 'equiped' in i]:
            list4=['inventory']
        else:
            list4 = []
        allkeys = list1 + list2 + list3 + list4
        for key in allkeys:
            x = col * 450 + self.rect.x + 15
            y = row * 35 + self.rect.y + 75
            if key == 'inventory':
                b = Button('Iventory', 
                    self.showinventory, 
                    [],
                    self.frontend.eventstack,
                    self.frontend.imagecache,
                    pos=(x ,y),
                    layer=6,
                    fontsize=14)
                self._addtemp('%s_button' % key, b)
                row += 1
                continue
            if key.startswith('events/') or key.startswith('__T'):
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
            if row * 35 + self.rect.y + 75 + 128> self.rect.y + self.rect.h -75:
                row = 0
                col += 1
        for key in sorted([i for i in self.conditional_sprites if 'animations' in i])+sorted(i for i in self.template if 'animations' in i and not 'conditional' in i and i != 'personal/portrait'):
            keyname = realkey(key)
            value = self.item.get(keyname,[])
            if not value:
                value = self.template[key]
            self.item.put(keyname, value)
        if self.item.animations:
            x = col * 450 + self.rect.x + 15
            y = row * 35 + self.rect.y + 75
            self.animation_editor(x,y)
        y = y + 75
        for sprite in self.handlekey('personal/portrait', x,y):
            self._addtemp(make_hash(), sprite)

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
            items=[Item(i) for i in items],
            onclose=self.updatelist,
            onclose_parms=[keyname],
            animation='view',
            can_add=True,
            can_remove=True,
            addfrom=itemlist)
        self._addtemp('%s_listmanager' %keyname, c)

    def showinventory(self, *args):
        #rect, frontend, char, layer=5
        self.update_yaml()
        self._rmtemp()
        inventory = Inventory(
            self.rect, 
            self.frontend,
            self.item,
            7,
            self.editorlayout
            )
        self._addtemp('editor_inventory', inventory)

    def updatelist(self, items, keyname):
        if keyname == 'inventory/pack':
            pack = self.item.get(keyname,[])
            for I  in pack:
                self.item.drop_item(Item(I))
            for I in items:
                self.item.acquire_item(I)
        else:
            items = [i() for i in items]
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
            if key in self.template:
                value = self.template[key]
            else:
                return ()
            if str(value).startswith('__'):
                value = ''
        if keyname == 'personal/portrait':
            self.item.put('personal/portrait', value)
            self.portrait = value
            d = BlitButton(
                self.nextportrait, 
                [],
                self.frontend.eventstack,
                self.frontend.imagecache,
                self.portrait,
                pos=(irect.x,y),
                scale=128,
                layer=7
                )
        elif isinstance(value, list):
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

    def nextportrait(self):
        portraitlist = [i for i in self.frontend.imagecache.keys() if i.startswith('portrait_')]
        idx = portraitlist.index(self.portrait)
        idx += 1
        if idx >= len(portraitlist) -1:
            idx = 0
        self.portrait = portraitlist[idx]
        self.item.put('personal/portrait', self.portrait)
        self.editorlayout()

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
        if self.dirname:
            filename = self.item.save_to_file(self.dirname)
            messages.error('Saved to %s' % os.path.basename(filename))

    def load(self):
        self._rmtemp()
        itemlist = []
        for itemfile in file_list(self.dirname):
            itemfile = os.path.basename(itemfile)
            if self.dirname == 'items':
                itemlist.append(Item(load_yaml(self.dirname,itemfile)))
            else:
                itemlist.append(NPC(load_yaml(self.dirname,itemfile)))
        c = ContainerDialog(self.rect,
            self.frontend,
            'Load %s' %self.dirname,
            7,
            items=itemlist,
            onselect=self.loaditem,
            onselect_parms=[],
            animation='view',
            can_add=False,
            can_remove=False
            )
        self._addtemp(make_hash(), c)

    def loaditem(self, item):
        debug('Loading item', item.displayname())
        self.item = item
        self.updateconditionals()

    def delete(self):
        self._rmtemp()
        self.kill()
        self.restorebg()