from util import rolldice, inrange, price_in_copper, convert_money, save_yaml, load_yaml, debug
from item import Item
from objects import EzdmObject, event
from gamemap import GameMap
import copy
from random import randrange
import operator
from flatteneddict import FlattenedDict
from messages import messages
from animatedsprite import AnimatedSprite

class Character(EzdmObject):
    """
    >>> char = Character(load_yaml('characters', 'bardic_rogue.yaml'))
    >>> char.displayname()
    '[BARDIC ROGUE]'
    """
    weapon = 0

    def roll_hit_dice(self):
        """
        >>> objdata = load_yaml('characters', 'bardic_rogue.yaml')
        >>> char = Character(objdata)
        >>> hitdice = int(char()['combat/level-hitdice'])
        >>> max = int(hitdice * 8)
        >>> char.roll_hit_dice()
        >>> char.get('combat/hitpoints', 0) <= max
        True
        >>> char.get('combat/max_hp', 0) == max
        True
        """
        numdice = int(self.get('combat/level-hitdice', '1'))
        self.put('combat/hitpoints', rolldice(numdice=numdice, numsides=8)[0])
        self.put('combat/max_hp', numdice * 8)

    # def handle_death(self):
    #     loc = self.location()
    #     debug("Dead character was at %s" % loc)
    #     chartype = self.character_type
    #     if chartype == 'player':
    #         chartype = 'players'
    #         todel = self.name()
    #     else:
    #         chartype = 'npcs'
    #         todel = self.get_hash()
    #         for char in list(frontend.campaign.characterlist):
    #             if char.character_type() == 'player':
    #                 frontend.campaign.message(char.give_xp(self.xp_worth()))
    #                 char.autosave()
    #         frontend.campaign.chars_in_round()
    #     gamemap = GameMap(load_yaml('maps', loc['map']))
    #     if todel != -1:
    #         gamemap.removefromtile(loc['x'], loc['y'], todel, chartype)
    #     debug(chartype)
    #     if chartype == 'npcs':
    #         max_gold = self.get('loot/gold', 0)
    #         max_silver = self.get('loot/silver', 0)
    #         max_copper = self.get('loot/copper', 0)
    #         loot_items = self.get('loot/items_possible', [])
    #         max_items = self.get('loot/max_items', 1)
    #         debug('Max Items:', max_items)
    #         always_drops = self.get('loot/always_drops', [])
    #         gold = rolldice(1, max_gold, 0)[0]
    #         silver = rolldice(1, max_silver, 0)[0]
    #         copper = rolldice(1, max_copper, 0)[0]
    #         if isinstance(loot_items, str):
    #             try:
    #                 debug('Trying to convert loot_items from string')
    #                 loot_items = simpleobjdata.loads(loot_items)
    #             except:
    #                 loot_items = []
    #         debug("Dropping money %s - %s - %s" % (gold, silver, copper))
    #         for counter in range(0, max_items):
    #             item = None
    #             debug("Potential drop: %s of %s" % (counter, max_items))
    #             drops_item = rolldice(1, 100, 0)[0]
    #             debug("Drop-roll: %s" % drops_item)
    #             debug('Loot items:', loot_items)
    #             if loot_items and drops_item > 50:
    #                 debug("Select random item from to drop from %s" % loot_items)
    #                 if len(loot_items) >= 2:
    #                     item = loot_items[randrange(0, len(loot_items) - 1)]
    #                 else:
    #                     item = loot_items[0]
    #             if item:
    #                 debug("Item dropped %s" % item)
    #                 gamemap.addtotile(loc['x'], loc['y'], item, 'items')
    #         debug("Always drops: %s" % always_drops)
    #         if isinstance(always_drops, str):
    #             try:
    #                 always_drops = simpleobjdata.loads(always_drops)
    #             except:
    #                 always_drops = []
    #         for item in always_drops:
    #             debug("Dropping %s" % item)
    #             gamemap.addtotile(loc['x'], loc['y'], item, 'items')
    #         gamemap.putmoney(loc['x'], loc['y'], gold, silver, copper)
    #     self.autosave()
    #     gamemap.save()
    #     frontend.campaign.chars_in_round()

    def location(self):
        """
        >>> objdata = load_yaml('characters', 'bardic_rogue.yaml')
        >>> char = Character(objdata)
        >>> char.location()['map'] == 'simple_room.json'
        True
        """
        return self.getsubtree('location')

    @property
    def lightradius(self):
        base_radius = self.get('lightradius', 0)
        for item in self.inventory_generator(['equiped']):
            base_radius += int(item[1].get('lightradius', 0))
        for item in self.inventory_generator(['pack']):
            if item[1].get('in_use', False):
                base_radius += int(item[1].get('lightradius', 0))
        return base_radius

    def memorized_spells(self):
        result = {}
        spells = self.get('inventory/spells', [])
        for idx in self.get('inventory/spells_memorized', []):
            item = Item(spells[idx])
            print(item())
            level = item.get('spell_level', 1)
            print (level)
            if level not in result:
                result[level] = []
            result[level].append(idx)
        return result

    def moveto(self, mapname, x, y, page=None):
        if not mapname:
            return
        if not isinstance(x, int) or not isinstance(y, int):
            try:
                x = int(x)
                y = int(y)
            except:
                return
        current = self.location()
        ctype = self.character_type == 'player' and 'players' or 'npcs'
        if current.get('map') and x and y:
            gamemap = GameMap(load_yaml('maps', current['map']))
            gamemap.removefromtile(current['x'], current['y'], self.name(), ctype)
        self.put('location/x', x)
        self.put('location/y', y)
        self.put('location/map', mapname)
        self.save()
        gamemap = GameMap(load_yaml('maps', mapname))
        gamemap.addtotile(x, y, self.name(), 'players')
        if page:
            tile = gamemap.tile(x, y)
            tile.onenter(self, page)
            gamemap.load_tile_from_objdata(x, y, tile())
        if self.character_type == 'player':
            gamemap.reveal(x, y, self.lightradius)

    def inventory_generator(self, sections=['pack', 'equiped', 'spells']):
        """
        >>> c = Character({})
        >>> mhand = Item(load_yaml('items', 'mainhand_dagger.yaml'))
        >>> mhand = c.acquire_item(mhand)
        >>> len(list(c.inventory_generator(['pack'])))
        1
        >>> c.equip_item(mhand)
        (True, '[ ] has equiped Dagger')
        >>> len(list(c.inventory_generator(['pack'])))
        0
        >>> len(list(c.inventory_generator(['equiped'])))
        1
        >>> for item in c.inventory_generator(['equiped']): item[1].displayname()
        'Dagger'
        """
        for section in sections:
            if section in ['pack', 'spells']:
                items = self.get('inventory/%s' % section, [])
                idx = -1
                for item in items:
                    idx += 1
                    yield (section, Item(item), idx)
            else:
                item = self.getsubtree('inventory/%s' % section)
                for slot in FlattenedDict(item).subkeys():
                    debug('Getting inventory from ', slot)
                    itemdata =  self.getsubtree('inventory/equiped/%s' %slot)
                    if itemdata:
                        yield(section, Item(itemdata),slot)

    @property
    def is_casting(self):
        """
        Covered by test for interrupt cast
        """
        for item in self.inventory_generator():
            if item[1].get('in_use', False):
                return True
        return False

    def interrupt_cast(self):
        #TODO - rewrite
        pass

    @property
    def character_type(self):
        #Override in subclasses
        return 'npc'

    def oninteract(self, target, page):
        event(self, 'events/oninteract', {'character': self, 'page': page, 'target': target})

    def xp_worth(self):
        xpkey = self.get('combat/level-hitdice', 1)
        xpvalues = load_yaml('adnd2e', 'creature_xp.objdata')
        if str(xpkey) in list(xpvalues.keys()):
            xp = xpvalues[str(xpkey)]
        elif int(xpkey) > 12:
            xp = 3000 + ((int(xpkey) - 13) * 1000)
        return int(xp)

    def save_to_tile(self):
        loc = self.location()
        gamemap = GameMap(load_yaml('maps', loc['map']))
        if isinstance(gamemap.tile(loc['x'], loc['y'])().get('conditional', {}).get('npcs'), list):
            gamemap.tile(loc['x'], loc['y'])()['conditional']['npcs'] = {}
        gamemap.tile(loc['x'], loc['y'])()['conditional']['npcs'][self.get_hash()] = self()
        return gamemap.save()

    def heal(self, amount):
        """
        >>> char = Character(load_yaml('characters', 'bardic_rogue.yaml'))
        >>> start = char.get('combat/hitpoints', 1)
        >>> max = char.get('combat/max_hp', 1)
        >>> if max - start < 1:
        ...    expected = max
        ... else:
        ...    expected = start + 1
        ...
        >>> x = char.heal(1)
        >>> char.get('combat/hitpoints', 1) == expected
        True
        >>> x == expected
        True
        """
        hp = int(self.get('combat/hitpoints', 1))
        hp += amount
        if hp > int(self.get('combat/max_hp', 1)):
            self.put('combat/hitpoints', int(self.get('combat/max_hp', 1)))
        else:
            self.put('combat/hitpoints', hp)
        return self.get('combat/hitpoints', 1)

    def take_damage(self, damage):
        """
        >>> char = Character(load_yaml('characters', 'bardic_rogue.yaml'))
        >>> start = 30
        >>> char.put('combat/hitpoints', start)
        >>> char.take_damage(1)
        (...)
        >>> end = char.get('combat/hitpoints', 1)
        >>> end < start
        True
        """
        messages.message('%s takes %s damage' % (self.displayname(), damage))
        debug("[DEBUG] character.take_damage: damage - %s, player - %s" % (damage, self.displayname()))
        out = ''
        currenthitpoints = self.get('combat/hitpoints', 1)
        if damage >= currenthitpoints:
            debug("[DEBUG] character.take_damage, damage MORE than hitpoints: %s, %s" % (damage, currenthitpoints))
            self.put('combat/hitpoints', 0)
            self.handle_death()
            return (False, '%s has died !' % self.displayname())
        else:
            debug("[DEBUG] character take damage, LESS than hitpoints: damage=%s, player=%s, hitpoints=%s" % (damage, self.displayname(), currenthitpoints))
            hp = int(currenthitpoints)
            hp -= damage
            self.put('combat/hitpoints', hp)
            out += "<br>%s takes %s damage. %s hitpoints remaining" % (self.displayname(), damage, self.get('combat/hitpoints', 1))
            messages.error('')
            return (True, out)

    def name(self):
        """
        >>> char = Character(load_yaml('characters', 'bardic_rogue.yaml'))
        >>> char.name()
        'bardic_rogue.yaml'
        """
        name = '%s_%s.yaml' % (self.get('personal/name/first', ''), self.get('personal/name/last', ''))
        return name.lower().replace(' ', '_').replace("'", "")

    def save(self):
        #TODO
        pass

    def autosave(self):
        if self.character_type == 'player':
            return self.save()
        else:
            return self.save_to_tile()

    def to_hit_mod(self):
        """
        >>> char = Character(load_yaml('characters', 'bardic_rogue.yaml'))
        >>> isinstance(char.to_hit_mod(), int)
        True
        """
        ability_mods = load_yaml('rules', 'ability_scores.yaml')
        strength = self.get('attributes/str', 1)
        base = int(FlattenedDict(ability_mods).get('/str/%s/hit' % strength, 0))
        bonus = 0
        for weapon in self.weapons:
            debug(weapon())
            try:
                w = int(weapon()['to_hit'])
            except ValueError:
                w = 0
            bonus += w
            debug('Adding to_hit bonus %s' % w)
        return base + bonus

    def ppd_mod(self):
        """
        >>> char = Character(load_yaml('characters', 'bardic_rogue.yaml'))
        >>> isinstance(char.ppd_mod(), int)
        True
        """
        ability_mods = FlattenedDict(load_yaml('rules', 'ability_scores.yaml'))
        con = self.get('attributes/con', 1)
        return int(ability_mods['con/%s/ppd' % con])

    def dmg_mod(self):
        """
        >>> char = Character(load_yaml('characters', 'bardic_rogue.yaml'))
        >>> isinstance(char.dmg_mod(), int)
        True
        """
        ability_mods = FlattenedDict(load_yaml('rules', 'ability_scores.yaml'))
        strength = self.get('attributes/str', 0)
        return int(ability_mods.get('/str/%s/dmg' % strength, 0))

    def def_mod(self):
        """
        >>> char = Character(load_yaml('characters', 'bardic_rogue.yaml'))
        >>> isinstance(char.def_mod(), int)
        True
        """
        ability_mods = load_yaml('rules', 'ability_scores.yaml')
        dex = self.get('attributes/dex', 0)
        return int(FlattenedDict(ability_mods).get('/dex/%s/defense' % dex, 0))

    @property
    def saving_throws(self):
        """
        >>> char = Character(load_yaml('characters', 'bardic_rogue.yaml'))
        >>> isinstance(char.saving_throws, dict)
        True
        """
        key = self.get('class/parent', '')
        sts = FlattenedDict(load_yaml("rules", "saving_throws.yaml"))
        sts = FlattenedDict(sts.readsubtree(key))
        hitdice = self.get('combat/level-hitdice', 0)
        for key2 in sts.subkeys():
            if inrange(hitdice, key2):
                st = sts.readsubtree(key2)
                st['ppd'] = int(st['ppd']) + self.ppd_mod()
                return(st)

    def saving_throw(self, against):
        saving = load_yaml('rules', 'saving_throws.yaml') or {}
        prettyname = saving['names'][against]
        race = self.get('personal/race', '')
        con = int(self.get('attributes/con', 0))
        mod = 0
        if race in list(saving.keys()):
            for key in list(saving[race].keys()):
                if inrange(con, key):
                    mod = int(saving[race][key])
                    continue
        target = int(FlattenedDict(self.saving_throws).get(against, 0))
        out = "%s Tries to roll a saving throw against %s" % (self.displayname(), prettyname)
        out += "<br>%s needs to roll %s" % (self.displayname(), target)
        roll = rolldice(numdice=1, numsides=20, modifier=mod)
        out += '<br>%s' % roll[1]
        if roll[0] >= int(target):
            out += '<br>Saved !'
            return (True, out)
        else:
            out += "<br>Did not save !"
            return (False, out)

    def current_weapon(self):
        """
        >>> char = Character(load_yaml('characters', 'bardic_rogue.yaml'))
        >>> isinstance(char.current_weapon(), Item)
        True
        """
        return self.weapons[self.weapon]

    def reset_weapon(self):
        self.weapon = 0

    def next_weapon(self):
        self.weapon += 1
        if self.weapon > self.num_weapons() - 1:
            self.weapon = 0

    def level_up(self):
        """
        >>> char = Character(load_yaml('characters', 'bardic_rogue.yaml'))
        >>> level = char.get('combat/level-hitdice', 1)
        >>> hp = char.get('combat/hitpoints', 1)
        >>> max = char.get('combat/max_hp', 1)
        >>> debug(char.level_up())
        >>> char.get('combat/hitpoints', 1) > hp
        True
        >>> char.get('combat/max_hp', 1) > max
        True
        >>> char.get('combat/level-hitdice', 1) == level + 1
        True
        """
        level = int(self.get('combat/level-hitdice', 1))
        level += 1
        out = '%s has reached level %s !' % (self.displayname(), level)
        self.put('combat/level-hitdice', level)
        ability_scores = load_yaml('rules', 'ability_scores.yaml')
        con = self.get('attributes/con', 1)
        out += '<br>Character constitution: %s' % con
        con_bonus = int(FlattenedDict(ability_scores).get('/con/%s/hit' % con,0))
        out += '<br>Constitution Bonus: %s' % con_bonus
        xp_levels = FlattenedDict(load_yaml('rules', 'xp_levels.yaml'))
        pclass = self.get('class/parent', '')
        xp_levels = xp_levels.readall(pclass)
        hitdice = str(xp_levels.get('%s/%s/hit_dice' % (pclass, level), 1))
        debug("Read hitdice as ", hitdice)
        if '+' not in hitdice:
            hitdice = hitdice + '+0'
        hitdice, bonus = hitdice.split('+')
        dice = int(xp_levels.get('%s/dice' % pclass, 1))
        more_hp, roll = rolldice(numdice=int(hitdice), numsides=dice, modifier=con_bonus)
        out += '<br>%s' % roll
        more_hp += int(bonus)
        current_max = int(self.get('combat/max_hp', 1))
        new_max = current_max + more_hp
        out += '<br>Maximum hitpoints increased by %s. Maximum hitpoints now: %s' % (more_hp, new_max)
        self.put('combat/max_hp', new_max)
        new_hp = new_max
        out += '<br>Character hitpoints now %s' % new_hp
        self.put('combat/hitpoints', new_hp)
        self.__init__(self())
        return out

    def give_xp(self, xp):
        """
        >>> char = Character(load_yaml('characters', 'bardic_rogue.yaml'))
        >>> level = char.get('combat/level-hitdice', 1)
        >>> nl = char.next_level()
        >>> debug(char.give_xp(nl + 10))
        >>> char.get('combat/level-hitdice', 1) == level + 1
        True
        """
        current_xp = int(self.get('personal/xp', 0))
        new_xp = current_xp + int(xp)
        self.put('personal/xp', str(new_xp))
        messages.message('%s gains %s experience points. XP now: %s' % (self.displayname(), xp, new_xp))
        next_level = self.next_level()
        if new_xp >= next_level and next_level != -1:
            messages.warning(self.level_up())
            messages.error('Check for and apply manual increases to other stats if needed !')
        else:
            messages.message('Next level at %s. %s experience points to go' % (next_level, next_level - new_xp))
        return new_xp

    def next_level(self):
        parentclass = self.get('class/parent', '')
        childclass = self.get('class/class', '')
        if childclass == 'paladin':
            childclass = 'ranger'
        debug('Checking next level for %s' % self.displayname())
        nl = int(self.get('combat/level-hitdice', 1)) + 1
        if nl > 20:
            return -1
        xp_levels = FlattenedDict(load_yaml('rules', 'xp_levels.yaml')).readall('/%s/%s' % (parentclass, str(nl)))
        
        if '%s/%s/all' %(parentclass, str(nl)) in xp_levels:
            next_xp = int(xp_levels['%s/%s/all' %(parentclass, str(nl))])
        else:
            next_xp = int(xp_levels['%s/%s/%s' %(parentclass, str(nl),childclass)])
        return next_xp

    def is_misile(self):
        try:
            return self.weapons[self.weapon+'/conditionals/weapon_type'] == "misile"
        except IndexError:
            return False

    def attack_roll(self, target, mod):
        self.next_weapon()
        messages.message('%s has THAC0 of: %s' % (self.displayname(), self.thac0))
        target_stats = '%s has a defense modifier of %s and armor class %s' % (target.displayname(), target.def_mod(), target.armor_class())

        messages.message(target_stats)
        target_roll = self.thac0 - target.armor_class() - target.def_mod()

        messages.message('%s needs to roll %s to hit %s' % (self.displayname(), target_roll, target.displayname()))
        roll = rolldice(numdice=1, numsides=20, modifier=mod)
        if roll[0] == 1:
                return (roll[0], "Critical Miss !", roll[1])
        elif roll[0] == 20:
            return (roll[0], "Critical Hit !", roll[1])
        else:
            if roll[0] >= target_roll:
                return (roll[0], "Hit !", roll[1])
            else:
                return (roll[0], "Miss !", roll[1])

    def spell_success(self):
        ability_scores = load_yaml('rules', 'ability_scores.yaml')
        wis = str(self.get('attributes/wis', 0))
        failrate = int(ability_scores["wis/%s/spell_failure" %(wis)].split('%')[0])
        out = "Spell failure rate: %s percent" % failrate
        roll = rolldice(numdice=1, numsides=100)
        out += '<br>%s' % roll[1]
        if roll[0] > failrate:
            out += '<br>Spell succeeds !'
            return (True, out)
        else:
            out += '<br>Spell fails !'
            return(False, out)

    def learn_spell(self, spellitem):
        spells = self.get('inventory/spells', [])
        if isinstance(spells, str):
            try:
                spells = simpleobjdata.loads(spells)
            except:
                spells = []
        if not isinstance(spells, list):
            self.put('inventory/spells', [])
        spelltype = spellitem.get('spell_type', 'wizard spells')
        parentclass = self.get('class/parent', '')
        childclass = self.get('class/class', '')
        canlearn = load_yaml('rules', 'various.yaml')["spell progression"]
        found = False
        for key in canlearn:
            if key == parentclass or key == childclass:
                debug(key)
                found = True
                break
        if not found:
            return "%s cannot learn spells" % self.displayname()
        oneline = list(canlearn[key].keys())[0]
        if spelltype not in canlearn[key][oneline]:
            return "%s cannot learn %s, failed to learn spell %s" % (self.displayname(), spelltype, spellitem.displayname())
        intelect = str(self.get('attributes/int', 1))
        chance = FlattenedDict(load_yaml('rules', 'ability_scores.yaml'))
        chance = chance['/int/%s/spell_learn' % intelect]
        out = "<strong>%s has a %s chance to learn a new spell</strong>" % (self.displayname(), chance)
        chance = int(chance.replace('%', ''))
        roll = rolldice(numdice=1, numsides=100, modifier=0)
        out += '<br>%s' % roll[1]
        if roll[0] > chance:
            return '%s<br><strong>%s has failed to learn %s!</strong>' % (out, self.displayname(), spellitem.displayname())
        spellitem.identify()
        self()['core']['inventory']['spells'].append(spellitem())
        self.autosave()
        return "%s<br><strong>%s has learned %s</strong>" % (out, self.displayname(), spellitem.displayname())

    def unlearn_spell(self, index):
        del(self()['inventory/spells'][index])

    def acquire_item(self, item):
        """
        >>> char = Character({})
        >>> item = Item(load_yaml('items', 'health_potion.yaml'))
        >>> char.acquire_item(item)
        <item.Item object at ...>
        >>> Item(char()['inventory/pack'][0]).displayname() == 'Health Potion'
        True
        """
        if self.character_type == 'player':
            item.onpickup(self)
        item.set_hash()
        li = self.objdata.get('inventory/pack',[])
        li.insert(0, item())
        self.put('inventory/pack',li)
        return item


    def equip_item(self, item):
        """
        >>> char = Character({})
        >>> mhand = Item(load_yaml('items', 'mainhand_dagger.yaml'))
        >>> twohand = Item(load_yaml('items', 'halberd.yaml'))
        >>> twohand = char.acquire_item(twohand)
        >>> mhand = char.acquire_item(mhand)
        >>> char.equip_item(twohand)
        (True, '[ ] has equiped Halberd')
        >>> char.equip_item(mhand)
        (True, '[ ] has equiped Dagger')
        >>> char.weapons
        [<item.Item object at ...>]
        >>> char.weapons[0].displayname()
        'Dagger'
        >>> mhand = char.acquire_item(mhand)
        >>> char.equip_item(mhand)
        (True, '[ ] has equiped Dagger')
        >>> [i.displayname() for i in char.weapons]
        ['Dagger', 'Dagger']
        """
        slots = []
        canwear = self.get('armor_types', 0)
        armor_types = load_yaml('rules', 'armor_types.yaml')
        shields = self.get('shields', False)

        if item() in self.get('inventory/pack',[]):
            if not item.identified():
                item.identify()
            if self.character_type == 'player':
                item.onequip(self)           
            if item.armortype() == 'shield' and not shields:
                return (False, "%s cannot wear %s shields like %s" % (self.displayname(), item.armortype(), item.displayname()))
            elif item.armortype() != 'shield' and item.itemtype() == 'armor' and canwear < armor_types[item.armortype()]:
                return (False, "%s cannot wear %s armor like %s" % (self.displayname(), item.armortype(), item.displayname()))
            if item.slot() == 'twohand':
                slots = ['lefthand', 'righthand']
            elif item.slot() == 'finger':
                left = self.getsubtree('inventory/equiped/leftfinger')
                right = self.getsubtree('inventory/equiped/rightfinger')
                if not left:
                    slots = ['leftfinger']
                if not right:
                    slots = ['rightfinger']
                if not slots:
                    slots = ['leftfinger']
            elif item.slot() == 'either hand':
                left = self.getsubtree('inventory/equiped/lefthand')
                right = self.getsubtree('inventory/equiped/righthand')
                if not left:
                    slots = ['lefthand']
                if not right:
                    slots = ['righthand']
                if not slots:
                    slots = ['righthand']

            else:
                slots = [item.slot()]
            for slot in slots:
                self.unequip_item(slot)
                self.putsubtree('inventory/equiped/%s' % slot.strip(), item())
            self.drop_item(item)
        return (True, "%s has equiped %s" % (self.displayname(), item.displayname()))

    def unequip_item(self, slot):
        """
        >>> char = Character({})
        >>> twohand = Item(load_yaml('items', 'halberd.yaml'))
        >>> twohand = char.acquire_item(twohand)
        >>> char.equip_item(twohand)
        (True, '[ ] has equiped Halberd')
        >>> char.unequip_item('lefthand')
        >>> char.weapons
        [<item.Item object at ...>]
        >>> char.weapons[0].displayname()
        'Fist'
        """
        itemdata = self.getsubtree('inventory/equiped/%s' % slot)
        if not itemdata:
            return
        item = Item(itemdata)
        currentslot = item.slot()
        pack = self.get('inventory/pack',[])
        pack.append(item())
        self.put('inventory/pack', pack)
        if currentslot.strip() == 'twohand':
            slots = ['lefthand','righthand']
        else:
            slots = [slot]
        for s in slots:
            self().deltree('inventory/equiped/%s' %s)
            self.put('inventory/equiped/%s' %s, {})


    def sell_price(self, gold, copper, silver):
            price = price_in_copper(gold, silver, copper)

            cha = int(self.get('attributes/cha', 1))
            price = (price / 2) + ((price / 100) * cha)
            money = convert_money(price)
            return (int(money['gold']), int(money['silver']), int(money['copper']))

    def sell_item(self, itemname, buyer='shop', gold=0, silver=0, copper=0):
        if isinstance(itemname, int):
            tosell = Item(self.get('inventory/pack', [])[itemname])
        else:
            for item in self.get('inventory/pack', []):
                if item.displayname() == itemname:
                    tosell = Item(item)
                    break
        if buyer != 'shop':
            buyer.spend_money(gold, silver, copper)
            buyer.acquire_item(tosell)
            buyer.autosave()
        else:
            gold, silver, copper = self.sell_price(*tosell.price_tuple())

        self.drop_item(itemname)
        self.gain_money(gold, silver, copper)

    def for_sale(self):
        """
        >>> char = Character({})
        >>> char.for_sale()
        []
        >>> hp = char.acquire_item(Item(load_yaml('items', 'health_potion.yaml')))
        >>> char.for_sale()
        [(0, 'Health Potion', 'Gold 4, Silver 10, Copper 10')]
        """
        out = []
        pack = self.get('inventory/pack', [])
        for i in pack:
            try:
                item = Item(i)
                gold, silver, copper = self.sell_price(*item.price_tuple())
                moneystr = 'Gold %s, Silver %s, Copper %s' % (int(gold), int(silver), int(copper))
                out.append((pack.index(i), item.displayname(), moneystr))
            except Exception as e:
                raise Exception('Error loading %s - %s' % (self.displayname(), e))
        return out

    def drop_item(self, item, section='pack'):
        """
        >>> char = Character({})
        >>> item = char.acquire_item(Item(load_yaml('items','health_potion.yaml')))
        >>> char.drop_item(item)
        >>> len(char.get('inventory/pack', []))
        0
        """
        pack = self.get('inventory/pack',[])
        for i in pack:
            if Item(i).get_hash() == item.get_hash():
                todrop = pack.index(i)
        if self.character_type == 'player':
            item.ondrop(player=self)
        del(self.objdata['inventory/pack'][todrop])

    def money_tuple(self):
        gold = self.get('inventory/money/gold', 0)
        silver = self.get('inventory/money/silver', 0)
        copper = self.get('inventory/money/copper', 0)
        return (int(gold), int(silver), int(copper))

    def spend_money(self, gold=0, silver=0, copper=0):
        ihave = price_in_copper(*self.money_tuple())
        price = price_in_copper(gold, silver, copper)
        remains = ihave - price
        if remains < 0:
            return False
        else:
            self.put('inventory/money', convert_money(remains))
            return True

    def buy_item(self, item, page=None):
        if self.spend_money(*item.price_tuple()):
            self.acquire_item(item)
            page.message('You bought a %s' % item.displayname())
            return True
        else:
            page.error('You cannot afford to buy %s' % item.displayname())
            return False

    def gain_money(self, gold=0, silver=0, copper=0):
        total_gained = price_in_copper(gold, silver, copper)
        my_total = price_in_copper(*self.money_tuple())
        my_total += total_gained
        self.put('inventory/money', convert_money(my_total))

    def armor_class(self):
        ac = 10.0
        for item in self.inventory_generator(['equiped']):
            ac -= float(item[1].get('ac', 0.0))
        return ac

    def equiped_by_type(self, itemtype):
        arm = []
        equiped = self.getsubtree('inventory/equiped')
        for slot in FlattenedDict(equiped).subkeys():
            itemdata = self.getsubtree('inventory/equiped/%s' % slot)
            if not itemdata:
                continue
            item = Item(itemdata)
            if item.itemtype() == itemtype:
                arm.append(item)
        return arm

    @property
    def armor(self):
        return self.equiped_by_type('armor')

    @property
    def weapons(self):
        """
        >>> char = Character({})
        >>> char.weapons[0].displayname()
        'Fist'
        >>> halberd = char.acquire_item(Item(load_yaml('items','halberd.yaml')))
        >>> item = Item(char.get('inventory/pack')[0])
        >>> char.equip_item(item)
        (True, '[ ] has equiped Halberd')
        >>> char.weapons[0].displayname()
        'Halberd'
        >>> len(char.weapons)
        1
        """
        equipedweapons = self.equiped_by_type('weapon')
        if not equipedweapons:
            debug('No weapons equipped - equipping fist')
            fist = Item(load_yaml('items', 'fist.yaml'))
            fist = self.acquire_item(fist)
            self.equip_item(fist)
            equipedweapons = self.equiped_by_type('weapon')
        if equipedweapons and equipedweapons[0].get('slot', "") == 'twohand':
            return [equipedweapons[0]]
        debug('Equipped weapons', equipedweapons)
        return equipedweapons

    def num_weapons(self):
        return len(self.weapons)

    def num_attacks(self):
        atr_objdata = FlattenedDict(load_yaml('rules', 'various.yaml'))
        atr = atr_objdata['various/attacks_per_round']
        parentclass = self.get('class/parent', '')
        if parentclass not in atr:
            myatr = 1
        else:
            for key in list(atr[parentclass].keys()):
                if inrange(self.get('combat/level-hitdice', 1), key):
                    myatr = int(atr[parentclass][key])
        return self.num_weapons() * int(myatr)

    def current_xp(self):
        return int(self.get('personal/xp', 0))

    def abilities(self):
        subclass = self.get('class/class', '')
        parentclass = self.get('class/parent', '')
        level = self.get('combat/level-hitdice', '')
        various = load_yaml('rules', 'various.yaml')
        abilities = various['abilities']
        conditionals = self.get('abilities', {})
        race = self.get('personal/race', self())
        for ability in abilities:
            base = 0
            if ability in conditionals:
                if isinstance(conditionals[ability], str) and len(conditionals[ability]) > 0:
                    base = int(conditionals[ability])
            if subclass in abilities[ability]:
                for key in abilities[ability][subclass]:
                    if inrange(level, key):
                        base += int(abilities[ability][subclass][key])
                        continue
            elif parentclass in abilities[ability]:
                for key in abilities[ability][parentclass]:
                    if inrange(level, key):
                        base += int(abilities[ability][parentclass][key])
                        continue
            if base > 0:
                if race in abilities[ability]:
                    base += int(abilities[ability][race])
                conditionals[ability] = base
        for key in conditionals:
            racial_bonus = 0
            dex_bonus = 0
            if key in various['abilities']:
                if "racial_bonus" in various['abilities'][key] and race in various['abilities'][key]["racial_bonus"]:
                    racial_bonus = int(various['abilities'][key]["racial_bonus"][race])
                dex = int(self.get('/abilities/dex', 0))
                if "dexterity bonus" in various['abilities'][key]:
                    for d in various['abilities'][key]["dexterity bonus"]:
                        if inrange(dex, d):
                            dex_bonus = int(various['abilities'][key]["dexterity bonus"][d])
                            continue
            if isinstance(conditionals[key], str) and len(conditionals[key]) == 0:
                conditionals[key] = 0
            if int(conditionals[key]) > 0:
                conditionals[key] = int(conditionals[key]) + dex_bonus + racial_bonus
        return conditionals

    def displayname(self):
        out = "[%s %s]" % (self.get('personal/name/first', ''), self.get('personal/name/last', ''))
        return out

    @property
    def thac0(self):
        if self.get('personal/race', '') == "creature":
            key = "creature"
        else:
            key = self.get('class/parent', '')
        thac0s = load_yaml("rules", "thac0.yaml")[key]
        for key2 in list(thac0s.keys()):
            if inrange(self.get('combat/level-hitdice', 1), key2):
                return int(thac0s[key2])

    # def render(self):
    #     """
    #     >>> char = Character(load_yaml('characters','bardic_rogue.yaml'))
    #     >>> char.render()
    #     {...}
    #     >>> char = Character({})
    #     >>> char.render()
    #     {}
    #     """
    #     out = copy.deepcopy(self())
    #     if 'hash' in out:
    #         del(out['hash'])
    #     if 'core' in out:
    #         out['core']['lightradius'] = self.lightradius
    #         if 'saving_throws' in out['core']['combat']:
    #             del out['core']['combat']['saving_throws']
    #         prettynames = load_yaml('rules', 'saving_throws.yaml')
    #         writekey('abilities', self.abilities(), out)
    #         if not self.character_type == 'player':
    #             out['XP Worth'] = self.xp_worth()
    #         for k, v in list(self.saving_throws.items()):
    #             prettyname = readkey('/names/%s' % k, prettynames, k)
    #             writekey('combat/saving_throws/%s ' % prettyname, v, out)
    #         self.reset_weapon()
    #         out['core']['combat']['armor_class'] = self.armor_class()
    #         out['core']['combat']['thac0'] = self.thac0
    #         del(out['core']['inventory'])
    #         del(out['conditional']['armor_types'])
    #         out['to_hit_mod'] = self.to_hit_mod()

    #         if 'index' in out:
    #             del (out['index'])
    #         xp = self.get('personal/xp', 0)
    #         nl = self.next_level()
    #         out['core']['personal']['xp'] = '%s/%s (%s to go)' % (xp, nl, nl - xp)
    #         armor_types = load_yaml('rules', 'armor_types.yaml')
    #         armor_types = sorted(iter(armor_types.items()), key=operator.itemgetter(1))
    #         out['core']['combat']['Armor allowed'] = []
    #         for atype in armor_types:
    #             if atype[1] <= self.get('armor_types', 0):
    #                 out['core']['combat']['Armor allowed'].append(atype[0])
    #     return out
