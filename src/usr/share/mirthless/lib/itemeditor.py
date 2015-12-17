import pygame
from pygame.locals import *
from item import Item
from util import debug
from dialog import FloatDialog
from tempsprites import Tempsprites
from button import render_text, Button, TextInput, Dropdown, checkboxbtn
from animatedsprite import AnimatedSprite
from messages import messages

class ItemEditor(FloatDialog, Tempsprites):
    def __init__(self, frontend):
        self.frontend = frontend
        self.rect = pygame.Rect(0,50, self.frontend.screensize.w, self.frontend.screensize.h - 250)
        FloatDialog.__init__(self, self.rect, frontend)
        Tempsprites.__init__(self)
        self.item = Item({})
        self.baselayout()
        self.editlayout()
        self.conditionals = []
        self.conrestore = self.image.copy()

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
        self.image.blit(render_text ('Item Editor:', size=32, color=(255,0,0)),(self.rect.w/2 - 20,10))
        split = self.frontend.imagecache['seperator']
        split = pygame.transform.smoothscale(split,(self.frontend.screensize.w -20, 10))
        self.image.blit(split,(10,60))
        save_btn = Button('Save Item', self.save, [], self.frontend.eventstack,self.frontend.imagecache, pos=(self.rect.x +  self.rect.w - 150,self.rect.y + self.rect.h - 50), layer=6)
        load_btn = Button('Load Item', self.load, [], self.frontend.eventstack,self.frontend.imagecache, pos=(self.rect.x +  10,self.rect.y + self.rect.h - 50), layer=6)
        self._addtemp('saveitem', save_btn)
        self._addtemp('loaditem', load_btn)

    def editlayout(self):
        self.itemtypes = {
        "armor": self.armorfields,
        "weapon": self.weaponfields,
        "spell": self.spellfields,
        "other": None
        }
        self.image.blit(render_text ('Name:', size=24, color=(255,0,0)),(10,70))
        self.name = TextInput(pygame.Rect(self.rect.x + 100, self.rect.y + 70, 200, 30), 18, self.frontend.eventstack, prompt=self.item.displayname() or 'new item', clearprompt=False, layer=7)
        self.name._layer = 6
        self._addtemp('itemname',self.name)
        self.itemtype = Dropdown(self.frontend.eventstack,
            self.frontend.imagecache,
            18,
            pygame.Rect(self.rect.x + 100, self.rect.y + 110, 200, 30),
            self.itemtypes.keys(),
            layer=8,
            choice=self.item.itemtype(),
            onselect=self.set_type)
        self._addtemp('itemtype', self.itemtype)
        self.image.blit(render_text ('Type:', size=24, color=(255,0,0)),(10,110))
        self.item_identified = checkboxbtn('Item identified ?', self.identified, [], self.frontend.eventstack,self.frontend.imagecache, pos=(self.rect.x + 10,self.rect.y + 140))
        self.item_identified.checked = self.item.identified()
        self._addtemp('item_identified', self.item_identified)
        g, s, c = self.item.price_tuple()
        self.image.blit(render_text ('Price:    Gold           Silver           Copper', size=24, color=(255,0,0)),(10,170))
        self.goldprice = TextInput(pygame.Rect(self.rect.x + 150, self.rect.y + 170, 50, 30), 18, self.frontend.eventstack, prompt=str(g), clearprompt=False, layer=7)
        self.silverprice = TextInput(pygame.Rect(self.rect.x + 275, self.rect.y + 170, 50, 30), 18, self.frontend.eventstack, prompt=str(s), clearprompt=False, layer=7)
        self.copperprice = TextInput(pygame.Rect(self.rect.x + 410, self.rect.y + 170, 50, 30), 18, self.frontend.eventstack, prompt=str(c), clearprompt=False, layer=8)
        self._addtemp('goldprice', self.goldprice)
        self._addtemp('silverprice', self.silverprice)
        self._addtemp('copperprice', self.copperprice)
        self.image.blit(render_text ('Charges (magic items only)', size=24, color=(255,0,0)),(10,210))
        self.charges = TextInput(pygame.Rect(self.rect.x + 300, self.rect.y + 210, 50, 30), 18, self.frontend.eventstack, prompt=str(self.item.get('core/charges',0)), clearprompt=False, layer=8)
        self._addtemp('charges', self.charges)

    def add_con(self, key, obj):
        self.conditionals.append((key,obj))
        self._addtemp(key,obj)

    def set_type(self, choice):
        for sprite in self.conditionals:
            sprite[1].delete()
            if sprite[0] in self.frontend.sprites:
                del self.frontend.sprites[sprite[0]]
        confields = self.itemtypes[choice]
        if confields != None:
            confields()

    def armorfields(self):
        slots = ["head","chest","legs","feet","wrists","hands","finger","neck"]
        materials = ["shield","cloth","leather","mail","plate"]
        self.image.blit(render_text ('Slot:', size=24, color=(255,0,0)),(10,250))
        self.slot = Dropdown(self.frontend.eventstack,
            self.frontend.imagecache,
            18,
            pygame.Rect(self.rect.x + 100, self.rect.y + 250, 200, 30),
            slots,
            layer=7,
            choice=self.item.get('conditional/slot',''),
            )
        self.add_con('itemslot', self.slot)
        self.image.blit(render_text ('Material', size=24, color=(255,0,0)),(10,290))
        self.material = Dropdown(self.frontend.eventstack,
            self.frontend.imagecache,
            18,
            pygame.Rect(self.rect.x + 100, self.rect.y + 290, 200, 30),
            materials,
            layer=7,
            choice=self.item.get('conditional/slot',''),
            )
        self.add_con('itermmaterial', self.material)
        self.image.blit(render_text ('Armor Class', size=24, color=(255,0,0)),(10,330))
        self.ac = TextInput(pygame.Rect(self.rect.x + 200, self.rect.y + 330, 50, 30), 18, self.frontend.eventstack, prompt=str(self.item.get('conditional/ac',0)), clearprompt=False, layer=6)
        self.add_con('armorclass', self.ac)



    def weaponfields(self):
        self.image.blit(render_text ('Slot', size=24, color=(255,0,0)),(10,200))

    def spellfields(self):
        pass



    def identified(self):
        self.item.put('core/identified', self.item_identified.checked)
        debug(self.item())

    def changepreview(self,choice):
        self.previewsprite.setanimation(choice)

    def save(self):
        if self.itemtype.choice != '':
            self.item.put('core/name', self.name.text)
            self.item.put('core/type', self.itemtype.choice)
            self.item.put('core/price/gold', int(self.goldprice.text))
            self.item.put('core/price/silver', int(self.silverprice.text))
            self.item.put('core/price/copper', int(self.copperprice.text))
        else:
            messages.error('ERROR: Not enough information')
        debug(self.item())

    def load(self):
        pass

    def delete(self):
        self._rmtemp()
        del self.frontend.sprites['npc']
        self.kill()
        self.restorebg()