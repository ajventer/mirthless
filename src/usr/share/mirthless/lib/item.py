from util import save_yaml, debug
from objects import EzdmObject, event
import copy
from messages import messages
from animatedsprite import AnimatedSprite


class Item(EzdmObject):
    def __init__(self, data):
        EzdmObject.__init__(self, data)
        self.animations = self.get('animations', {})

    def displayname(self):
        name = self.get('/core/name', '')
        if not self.identified():
            name = name.split('of')[0]
        return name

    def save(self):
        #TODO
        pass

    def slot(self):
        return self.get('conditional/slot', '')

    def identified(self):
        return self.get('core/identified', False)

    def identify(self):
        self.put('core/identified', True)

    def price_tuple(self):
        gold = self.get('core/price/gold', 0)
        silver = self.get('core/price/silver', 0)
        copper = self.get('core/price/copper', 0)
        try:
            gold = int(gold)
        except ValueError:
            gold = 0
        try:
            silver = int(silver)
        except ValueError:
            silver = 0
        try:
            copper = int(copper)
        except ValueError:
            copper = 0
        return (gold, silver, copper)

    def itemtype(self):
        return self.get('core/type', '')

    def armortype(self):
        return self.get('/conditional/material', 'plate')

    def onpickup(self, player):
        event(self, "/events/onpickup", {'item': self, 'player': player, 'messages': messages})
        player.autosave()

    def onequip(self, player):
        event(self, "/events/onequip", {'item': self, 'player': player, 'messages': messages})

    def onunequip(self, player):
        event(self, "/events/onunequip", {'item': self, 'player': player, 'messages': messages})

    def onstrike(self, player, target):
        event(self, "/conditional/events/onstrike", {'item': self, 'player': player, 'target': target, 'messages': messages})
        debug("Item.onstrike save: %s" % target.autosave())

    def onuse(self, player, target):
        debug("[DEBUG] Item.onuse: player %s, target %s" % (player.displayname(), target.displayname()))
        charges = self.get('/core/charges', 0)
        if charges == 0:
            return
        if self.itemtype() == 'spell':
            success = player.spell_success()
            messages.message(success[1])
            if not success[0]:
                return
        self.put('/core/in_use', True)
        #TODO - expect the next line to break in use. Needs to be redone once the 
        #new game class is finished
        self.put('/core/target', target)
        event(self, "/events/onuse", {'item': self, 'player': player, 'target': target, 'messages': messages})
        try:
            target = messages.characterlist[target.index]
            debug("Item.onround save: %s" % target.autosave())
        except:
            return
        messages.error("Item.onuse save: %s" % target.autosave())

    def onround(self, player):
        targetindex = self.get('/core/target', 0)
        try:
            target = messages.characterlist[targetindex]
        except:
            return
        debug("[DEBUG] Item.onround: self: %s, player: %s, target: %s" % (self.displayname(), player.displayname(), target))
        if self.get('/core/in_use', False):
            rounds = self.get('/core/rounds_per_charge', 0)
            current_rounds_performed = self.get('/core/current_rounds_performed', 0)
            debug("[DEBUG] item.onround: current_rounds_performed: %s, round: %s" % (current_rounds_performed, rounds))
            if current_rounds_performed < rounds:
                current_rounds_performed += 1
            self.put('/core/current_rounds_performed', current_rounds_performed)
            if current_rounds_performed < rounds:
                debug("[DEBUG] item.onround: run onround event")
                event(self, "/events/onround", {'item': self, 'player': player, 'target': target, 'messages': messages})
            else:
                debug("[DEBUG] item.onround: running onfinish")
                self.onfinish(player=player)
        try:
            target = messages.characterlist[targetindex]
            debug("Item.onround save: %s" % target.autosave())
        except:
            return

    def onfinish(self, player):
        debug("[DEBUG] item.onfinish player %s" % player.displayname())
        targetindex = self.get('/core/target', 0)
        debug("[DEBUG] item.onfinish target %s" % targetindex)
        try:
            target = messages.characterlist[targetindex]
        except:
            return
        debug("[DEBUG] item.onfinish target %s" % target.displayname())
        self.put('/core/in_use', False)
        self.put('/core/target', None)
        charges = self.get('/core/charges', 0)
        debug("[DEBUG] item.onfinish charges %s" % charges)
        if charges > 0:
            charges -= 1
            self.put('/core/charges', charges)
        self.put('/core/current_rounds_performed', 0)
        debug("[DEBUG] item.onfinish before event")
        event(self, "/events/onfinish", {'item': self, 'player': player, 'target': target, 'messages': messages})
        try:
            target = messages.characterlist[targetindex]
            debug("Item.onfinish save: %s" % target.autosave())
        except:
            return

    def ondrop(self, player):
        event(self, "events/ondrop", {'item': self, 'player': player, 'messages': messages})
        player.autosave()

    def interrupt(self):
        self.put('core/in_use', False)
