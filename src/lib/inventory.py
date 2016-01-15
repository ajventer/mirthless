import pygame
from pygame.locals import *
from item import Item
from dialog import FloatDialog, ContainerDialog
from util import file_list, debug, load_yaml, make_hash
from animatedsprite import ButtonSprite
import os
from messages import messages

class Inventory(FloatDialog):
    def __init__(self, rect, frontend, char, layer=5, onclose=None, title=''):
        self._layer = layer
        FloatDialog.__init__(self, rect, frontend, layer)
        self.rect = rect
        self.frontend = frontend
        self.char = char
        if self.char is None:
            self.char = self.frontend.game.player
        self.npc = self.char.character_type == 'npc'
        self.onclose = onclose
        self.layout()

    def layout(self):
        self._rmtemp()

        itemlist = []
        for itemfile in file_list('items'):
            itemfile = os.path.basename(itemfile)
            itemlist.append(Item(load_yaml('items',itemfile)))
        inventory_rect = pygame.Rect(self.rect.x,self.rect.y, self.rect.w - 523, self.rect.h)
        pack = ContainerDialog(
            inventory_rect,
            self.frontend,
            'Pack:',
            layer=self._layer +1,
            items=[Item(i) for i in self.char.get('inventory/pack',[])],
            onclose=self.update_inventory,
            onselect=self.equip_item,
            onselect_parms=[],
            can_add=False,
            can_remove=False,
            addfrom=itemlist
            )
        self._addtemp('Inventory_pack_dialog', pack)
        image_x = self.rect.w - 522
        image_y = 10
        self.image.blit(self.frontend.imagecache['inventory_background.png'], (image_x, image_y))
        rects = load_yaml('images','gui_rects.yaml')
        debug(self.char())
        portrait = self.frontend.imagecache[self.char.get('personal/portrait')]
        portrait = pygame.transform.smoothscale(portrait, (256,256))
        prect = rects['inventory_portrait']
        self.image.blit(portrait,(image_x + prect['x'],image_y + prect['y']))
        image_x += self.rect.x
        image_y += self.rect.y
        for itemtuple in self.char.inventory_generator(['equiped']):
            debug(itemtuple)
            item, slot = itemtuple[1], itemtuple[2]
            irect = rects[slot]
            irect = pygame.Rect(image_x + irect['x'], image_y + irect['y'], irect['w'], irect['h'])
            debug(slot, irect)
            sprite = ButtonSprite(
                self.frontend.tilemaps,
                irect,
                self.frontend.eventstack,
                onclick=self.unequip_item,
                onclick_params=[slot],
                animations=item.getsubtree('animations'),
                layer=self._layer + 2,
                fps=5,
                mouseover=item.displayname(),
                frontend=self.frontend,
                sendself=True
                )
            sprite.setanimation('view')
            self._addtemp(make_hash(), sprite)

    def update_inventory(self, items, *args):
        self.char.put('inventory/pack', items)
        self.onclose()

    def equip_item(self, item):
        status = self.char.equip_item(item)
        if status[0]:
            messages.message(status[1])
        else:
            messages.error(status[1])
        self.layout()

    def unequip_item(self, sprite, slot):
        debug('Unequiping item from ', slot)
        self.char.unequip_item(slot)
        self.char.weapons
        self.layout()


