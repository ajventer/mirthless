from util import npc_hash, rolldice, inrange, price_in_copper, convert_money, save_json, load_json, readkey, writekey, debug
from item import Item
from objects import EzdmObject, event
from gamemap import GameMap
import copy
from random import randrange
import operator
import json as simplejson
from graphics import frontend


class Character(EzdmObject):
    """
    >>> char = Character(load_json('characters', 'bardic_rogue.json'))
    >>> char.displayname()
    '[BARDIC ROGUE]'
    """
    json = {}
    weapon = 0

    def __init__(self, json):
        """
        >>> json = load_json('characters', 'bardic_rogue.json')
        >>> char = Character(json)
        >>> char.json == json
        True

        """
        self.json = json
        if self.json:
            self.reset_weapon()

    def roll_hit_dice(self):
        """
        >>> json = load_json('characters', 'bardic_rogue.json')
        >>> char = Character(json)
        >>> hitdice = int(char()['core']['combat']['level-hitdice'])
        >>> max = int(hitdice * 8)
        >>> char.roll_hit_dice()
        >>> char.get('/core/combat/hitpoints', 0) <= max
        True
        >>> char.get('/core/combat/max_hp', 0) == max
        True
        """
        numdice = int(self.get('/core/combat/level-hitdice', '1'))
        self.put('core/combat/hitpoints', rolldice(numdice=numdice, numsides=8)[0])
        self.put('core/combat/max_hp', numdice * 8)

    def handle_death(self):
        loc = self.location()
        debug("Dead character was at %s" % loc)
        chartype = self.character_type()
        if chartype == 'player':
            chartype = 'players'
            todel = self.name()
        else:
            chartype = 'npcs'
            todel = self.get_hash()
            for char in list(frontend.campaign.characterlist):
                if char.character_type() == 'player':
                    frontend.campaign.message(char.give_xp(self.xp_worth()))
                    char.autosave()
            frontend.campaign.chars_in_round()
        gamemap = GameMap(load_json('maps', loc['map']))
        if todel != -1:
            gamemap.removefromtile(loc['x'], loc['y'], todel, chartype)
        debug(chartype)
        if chartype == 'npcs':
            max_gold = self.get('/conditional/loot/gold', 0)
            max_silver = self.get('/conditional/loot/silver', 0)
            max_copper = self.get('/conditional/loot/copper', 0)
            loot_items = self.get('/conditional/loot/items_possible', [])
            max_items = self.get('/conditional/loot/max_items', 1)
            debug('Max Items:', max_items)
            always_drops = self.get('/conditional/loot/always_drops', [])
            gold = rolldice(1, max_gold, 0)[0]
            silver = rolldice(1, max_silver, 0)[0]
            copper = rolldice(1, max_copper, 0)[0]
            if isinstance(loot_items, str):
                try:
                    debug('Trying to convert loot_items from string')
                    loot_items = simplejson.loads(loot_items)
                except:
                    loot_items = []
            debug("Dropping money %s - %s - %s" % (gold, silver, copper))
            for counter in range(0, max_items):
                item = None
                debug("Potential drop: %s of %s" % (counter, max_items))
                drops_item = rolldice(1, 100, 0)[0]
                debug("Drop-roll: %s" % drops_item)
                debug('Loot items:', loot_items)
                if loot_items and drops_item > 50:
                    debug("Select random item from to drop from %s" % loot_items)
                    if len(loot_items) >= 2:
                        item = loot_items[randrange(0, len(loot_items) - 1)]
                    else:
                        item = loot_items[0]
                if item:
                    debug("Item dropped %s" % item)
                    gamemap.addtotile(loc['x'], loc['y'], item, 'items')
            debug("Always drops: %s" % always_drops)
            if isinstance(always_drops, str):
                try:
                    always_drops = simplejson.loads(always_drops)
                except:
                    always_drops = []
            for item in always_drops:
                debug("Dropping %s" % item)
                gamemap.addtotile(loc['x'], loc['y'], item, 'items')
            gamemap.putmoney(loc['x'], loc['y'], gold, silver, copper)
        self.autosave()
        gamemap.save()
        frontend.campaign.chars_in_round()

    def location(self):
        """
        >>> json = load_json('characters', 'bardic_rogue.json')
        >>> char = Character(json)
        >>> char.location()['map'] == 'simple_room.json'
        True
        """
        return self.get('/core/location', {})

    @property
    def lightradius(self):
        base_radius = self.get('/core/lightradius', 0)
        for item in self.inventory_generator(['equiped']):
            base_radius += int(item[1].get('/core/lightradius', 0))
        for item in self.inventory_generator(['pack']):
            if item[1].get('/core/in_use', False):
                base_radius += int(item[1].get('/core/lightradius', 0))
        return base_radius

    def memorized_spells(self):
        result = {}
        spells = self.get('/core/inventory/spells', [])
        for idx in self.get('/core/inventory/spells_memorized', []):
            item = Item(spells[idx])
            print(item())
            level = item.get('/conditional/spell_level', 1)
            print (level)
            if level not in result:
                result[level] = []
            result[level].append(idx)
        debug(result)
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
        debug(current)
        ctype = self.character_type() == 'player' and 'players' or 'npcs'
        if current.get('map') and x and y:
            gamemap = GameMap(load_json('maps', current['map']))
            gamemap.removefromtile(current['x'], current['y'], self.name(), ctype)
            debug("Saving", gamemap.save())
        self.put('/core/location/x', x)
        self.put('/core/location/y', y)
        self.put('/core/location/map', mapname)
        self.save()
        gamemap = GameMap(load_json('maps', mapname))
        gamemap.addtotile(x, y, self.name(), 'players')
        if page:
            tile = gamemap.tile(x, y)
            tile.onenter(self, page)
            gamemap.load_tile_from_json(x, y, tile())
        if self.character_type() == 'player':
            gamemap.reveal(x, y, self.lightradius)
        debug("Saving", gamemap.save())

    def inventory_generator(self, sections=['pack', 'equiped', 'spells']):
        for section in sections:
            items = self.get('/core/inventory/%s' % section, [])
            idx = -1
            if isinstance(items, list):
                for item in items:
                    idx += 1
                    yield (section, Item(item), idx)
            elif isinstance(items, dict):
                for k, v in list(items.items()):
                    yield (k, Item(v), 0)
            else:
                self.put('/core/inventory/%s', [])

    @property
    def is_casting(self):
        """
        Covered by test for interrupt cast
        """
        for item in self.inventory_generator():
            if item[1].get('/core/in_use', False):
                return True
        return False

    def interrupt_cast(self):
        """
        >>> json = load_json('characters', 'bardic_rogue.json')
        >>> char = Character(json)
        >>> tar = Character(load_json('characters', 'tiny_tim.json'))
        >>> spell = Item(load_json('items', 'magic_misile.json'))
        >>> char.acquire_item(spell)
        >>> spell = Item(char.get('/core/inventory/pack', [])[0])
        >>> spell.onuse(char, tar)
        >>> char()['core']['inventory']['pack'][0] = spell()
        >>> print (char.get('/core/inventory/pack', []))
        [...]
        >>> char.is_casting
        True
        >>> char.interrupt_cast()
        >>> char.is_casting
        False
        """
        for item in self.inventory_generator():
            if item[1].get('/core/in_use', False):
                item[1].interrupt()
            if item[0] in ['spells', 'pack']:
                self()['core']['inventory'][item[0]][item[2]] = item[1]()
            else:
                self.put('/core/inventory/equiped_by_type/%s' % item[0], item[1]())
        self.autosave()

    def character_type(self):
        """
        >>> char = Character(load_json('characters', 'tiny_tim.json'))
        >>> char.character_type()
        'player'
        >>> char = Character(load_json('characters', 'random_monster.json'))
        >>> char.character_type()
        'npc'
        """
        return self.get('/core/type', 'player')

    def oninteract(self, target, page):
        event(self, '/conditional/events/oninteract', {'character': self, 'page': page, 'target': target})

    def xp_worth(self):
        xpkey = self.get('core/combat/level-hitdice', 1)
        debug(xpkey)
        xpvalues = load_json('adnd2e', 'creature_xp.json')
        debug(xpvalues)
        if str(xpkey) in list(xpvalues.keys()):
            xp = xpvalues[str(xpkey)]
        elif int(xpkey) > 12:
            xp = 3000 + ((int(xpkey) - 13) * 1000)
        return int(xp)

    def set_hash(self):
        myhash = npc_hash()
        self.put('/hash', myhash)
        return myhash

    def get_hash(self):
        return self.get('/hash', '')

    def save_to_tile(self):
        loc = self.location()
        gamemap = GameMap(load_json('maps', loc['map']))
        if isinstance(gamemap.tile(loc['x'], loc['y'])().get('conditional', {}).get('npcs'), list):
            gamemap.tile(loc['x'], loc['y'])()['conditional']['npcs'] = {}
        gamemap.tile(loc['x'], loc['y'])()['conditional']['npcs'][self.get_hash()] = self()
        return gamemap.save()

    def heal(self, amount):
        """
        >>> char = Character(load_json('characters', 'tiny_tim.json'))
        >>> start = char.get('/core/combat/hitpoints', 1)
        >>> max = char.get('/core/combat/max_hp', 1)
        >>> if max - start < 1:
        ...    expected = max
        ... else:
        ...    expected = start + 1
        ...
        >>> x = char.heal(1)
        >>> char.get('/core/combat/hitpoints', 1) == expected
        True
        >>> x == expected
        True
        """
        hp = int(self.get('/core/combat/hitpoints', 1))
        hp += amount
        if hp > int(self.get('/core/combat/max_hp', 1)):
            self.put('/core/combat/hitpoints', int(self.get('/core/combat/max_hp', 1)))
        else:
            self.put('/core/combat/hitpoints', hp)
        return self.get('/core/combat/hitpoints', 1)

    def take_damage(self, damage):
        """
        >>> char = Character(load_json('characters', 'tiny_tim.json'))
        >>> start = 30
        >>> char.put('/core/combat/hitpoints', start)
        >>> char.take_damage(1)
        (...)
        >>> end = char.get('/core/combat/hitpoints', 1)
        >>> end < start
        True
        """
        frontend.campaign.message('%s takes %s damage' % (self.displayname(), damage))
        debug("[DEBUG] character.take_damage: damage - %s, player - %s" % (damage, self.displayname()))
        out = ''
        currenthitpoints = self.get('/core/combat/hitpoints', 1)
        if damage >= currenthitpoints:
            debug("[DEBUG] character.take_damage, damage MORE than hitpoints: %s, %s" % (damage, currenthitpoints))
            self.put('/core/combat/hitpoints', 0)
            self.handle_death()
            return (False, '%s has died !' % self.displayname())
        else:
            debug("[DEBUG] character take damage, LESS than hitpoints: damage=%s, player=%s, hitpoints=%s" % (damage, self.displayname(), currenthitpoints))
            hp = int(currenthitpoints)
            hp -= damage
            self.put('/core/combat/hitpoints', hp)
            out += "<br>%s takes %s damage. %s hitpoints remaining" % (self.displayname(), damage, self.get('/core/combat/hitpoints', 1))
            frontend.campaign.error(self.autosave())
            return (True, out)

    def name(self):
        """
        >>> char = Character(load_json('characters', 'tiny_tim.json'))
        >>> char.name()
        'tiny_tim.json'
        """
        name = '%s_%s.json' % (self.get('/core/personal/name/first', ''), self.get('/core/personal/name/last', ''))
        return name.lower().replace(' ', '_').replace("'", "")

    def save(self):
        #TODO
        pass

    def autosave(self):
        if self.character_type() == 'player':
            return self.save()
        else:
            return self.save_to_tile()

    def to_hit_mod(self):
        """
        >>> char = Character(load_json('characters', 'tiny_tim.json'))
        >>> isinstance(char.to_hit_mod(), int)
        True
        """
        ability_mods = load_json('adnd2e', 'ability_scores')
        strength = self.get('/core/abilities/str', 1)
        base = int(readkey('/str/%s/hit' % strength, ability_mods, 0))
        bonus = 0
        for weapon in self.weapons:
            debug(weapon())
            try:
                w = int(readkey('/conditional/to_hit', weapon(), 0))
            except ValueError:
                w = 0
            bonus += w
            debug('Adding to_hit bonus %s' % w)
        return base + bonus

    def ppd_mod(self):
        """
        >>> char = Character(load_json('characters', 'tiny_tim.json'))
        >>> isinstance(char.ppd_mod(), int)
        True
        """
        ability_mods = load_json('adnd2e', 'ability_scores')
        con = self.get('/core/abilities/con', 1)
        return int(readkey('/con/%s/ppd' % con, ability_mods))

    def dmg_mod(self):
        """
        >>> char = Character(load_json('characters', 'tiny_tim.json'))
        >>> isinstance(char.dmg_mod(), int)
        True
        """
        ability_mods = load_json('adnd2e', 'ability_scores')
        strength = self.get('/core/abilities/str', 0)
        return int(readkey('/str/%s/dmg' % strength, ability_mods, 0))

    def def_mod(self):
        """
        >>> char = Character(load_json('characters', 'tiny_tim.json'))
        >>> isinstance(char.def_mod(), int)
        True
        """
        ability_mods = load_json('adnd2e', 'ability_scores')
        dex = self.get('/core/abilities/dex', 0)
        return int(readkey('/dex/%s/defense' % dex, ability_mods, 0))

    @property
    def saving_throws(self):
        """
        >>> char = Character(load_json('characters', 'tiny_tim.json'))
        >>> isinstance(char.saving_throws, dict)
        True
        """
        key = self.get('/core/class/parent', '')
        sts = load_json("adnd2e", "saving_throws")[key]
        hitdice = self.get('/core/combat/level-hitdice', 0)
        for key2 in list(sts.keys()):
            if inrange(hitdice, key2):
                st = sts[key2]
                st['ppd'] = int(st['ppd']) + self.ppd_mod()
                return(st)

    def saving_throw(self, against):
        saving = load_json('adnd2e', 'saving_throws') or {}
        prettyname = saving['names'][against]
        race = self.get('/core/personal/race', '')
        con = int(self.get('/core/abilities/con', 0))
        mod = 0
        if race in list(saving.keys()):
            for key in list(saving[race].keys()):
                if inrange(con, key):
                    mod = int(saving[race][key])
                    continue
        target = int(readkey(against, self.saving_throws, 0))
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
        >>> char = Character(load_json('characters', 'tiny_tim.json'))
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
        >>> char = Character(load_json('characters', 'tiny_tim.json'))
        >>> level = char.get('/core/combat/level-hitdice', 1)
        >>> hp = char.get('/core/combat/hitpoints', 1)
        >>> max = char.get('/core/combat/max_hp', 1)
        >>> debug(char.level_up())
        >>> char.get('/core/combat/hitpoints', 1) > hp
        True
        >>> char.get('/core/combat/max_hp', 1) > max
        True
        >>> char.get('/core/combat/level-hitdice', 1) == level + 1
        True
        """
        level = int(self.get('/core/combat/level-hitdice', 1))
        level += 1
        out = '%s has reached level %s !' % (self.displayname(), level)
        self.put('/core/combat/level-hitdice', level)
        ability_scores = load_json('adnd2e', 'ability_scores')
        con = self.get('/core/abilities/con', 1)
        out += '<br>Character constitution: %s' % con
        con_bonus = int(readkey('/con/%s/hit' % con, ability_scores, 0))
        out += '<br>Constitution Bonus: %s' % con_bonus
        xp_levels = load_json('adnd2e', 'xp_levels')
        pclass = self.get('/core/class/parent', '')
        xp_levels = readkey('%s' % (pclass), xp_levels)
        hitdice = str(readkey('/%s/hit_dice' % (level), xp_levels, 1))
        debug("Read hitdice as ", hitdice)
        if '+' not in hitdice:
            hitdice = hitdice + '+0'
        hitdice, bonus = hitdice.split('+')
        dice = int(readkey('/dice', xp_levels, 1))
        more_hp, roll = rolldice(numdice=int(hitdice), numsides=dice, modifier=con_bonus)
        out += '<br>%s' % roll
        more_hp += int(bonus)
        current_max = int(self.get('/core/combat/max_hp', 1))
        new_max = current_max + more_hp
        out += '<br>Maximum hitpoints increased by %s. Maximum hitpoints now: %s' % (more_hp, new_max)
        self.put('core/combat/max_hp', new_max)
        current_hp = int(self.get('/core/combat/hitpoints', 0))
        new_hp = current_hp + more_hp
        out += '<br>Character hitpoints now %s' % new_hp
        self.put('/core/combat/hitpoints', new_hp)
        self.__init__(self())
        return out

    def give_xp(self, xp):
        """
        >>> char = Character(load_json('characters', 'tiny_tim.json'))
        >>> level = char.get('/core/combat/level-hitdice', 1)
        >>> nl = char.next_level()
        >>> debug(char.give_xp(nl + 10))
        >>> char.get('/core/combat/level-hitdice', 1) == level + 1
        True
        """
        current_xp = int(self.get('/core/personal/xp', 0))
        new_xp = current_xp + int(xp)
        self.put('/core/personal/xp', str(new_xp))
        frontend.campaign.message('%s gains %s experience points. XP now: %s' % (self.displayname(), xp, new_xp))
        next_level = self.next_level()
        if new_xp >= next_level and next_level != -1:
            frontend.campaign.warning(self.level_up())
            frontend.campaign.error('Check for and apply manual increases to other stats if needed !')
        else:
            frontend.campaign.message('Next level at %s. %s experience points to go' % (next_level, next_level - new_xp))
        return new_xp

    def next_level(self):
        parentclass = self.get('/core/class/parent', '')
        childclass = self.get('/core/class/class', '')
        if childclass == 'paladin':
            childclass = 'ranger'
        debug('Checking next level for %s' % self.displayname())
        nl = int(self.get('/core/combat/level-hitdice', 1)) + 1
        if nl > 20:
            return -1
        xp_levels = readkey('/%s/%s' % (parentclass, str(nl)), load_json('adnd2e', 'xp_levels'), {})
        if 'all' in xp_levels:
            next_xp = int(xp_levels['all'])
        else:
            next_xp = int(xp_levels[childclass])
        return next_xp

    def is_misile(self):
        try:
            return self.weapons[self.weapon]['conditionals']['weapon_type'] == "misile"
        except IndexError:
            return False

    def attack_roll(self, target, mod):
        self.next_weapon()
        frontend.campaign.message('%s has THAC0 of: %s' % (self.displayname(), self.thac0))
        target_stats = '%s has a defense modifier of %s and armor class %s' % (target.displayname(), target.def_mod(), target.armor_class())

        frontend.campaign.message(target_stats)
        target_roll = self.thac0 - target.armor_class() - target.def_mod()

        frontend.campaign.message('%s needs to roll %s to hit %s' % (self.displayname(), target_roll, target.displayname()))
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
        ability_scores = load_json('adnd2e', 'ability_scores')
        wis = str(self.get('/core/abilities/wis', 0))
        failrate = int(ability_scores["wis"][wis]["spell_failure"].split('%')[0])
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
        spells = self.get('/core/inventory/spells', [])
        if isinstance(spells, str):
            try:
                spells = simplejson.loads(spells)
            except:
                spells = []
        if not isinstance(spells, list):
            self.put('/core/inventory/spells', [])
        spelltype = spellitem.get('/conditional/spell_type', 'wizard spells')
        parentclass = self.get('/core/class/parent', '')
        childclass = self.get('/core/class/class', '')
        canlearn = load_json('adnd2e', 'various.json')["spell progression"]
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
        intelect = str(self.get('/core/abilities/int', 1))
        chance = load_json('adnd2e', 'ability_scores.json')
        chance = readkey('/int/%s/spell_learn' % intelect, chance)
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
        del(self()['core']['inventory']['spells'][index])

    def acquire_item(self, item):
        """
        >>> char = Character({})
        >>> item = Item(load_json('items', 'health_potion.json'))
        >>> char.acquire_item(item)
        >>> Item(char()['core']['inventory']['pack'][0]).displayname() == 'Health Potion'
        True
        """
        if not isinstance(self.get('/core/inventory/pack', ''), list):
            self.put('/core/inventory/pack', [])
        if self.character_type() == 'player':
            item.onpickup(self)
        self()['core']['inventory']['pack'].insert(0, item())

    def equip_item(self, itemname):
        """
        >>> char = Character({})
        >>> mhand = Item(load_json('items', 'mainhand_dagger.json'))
        >>> ohand = Item(load_json('items', 'offhand_dagger.json'))
        >>> twohand = Item(load_json('items', 'halberd.json'))
        >>> char.acquire_item(twohand)
        >>> char.equip_item(0)
        (True, '[ ] has equiped Halberd')
        >>> char.weapons
        [<ezdm_libs.item.Item object at ...>]
        >>> char.weapons[0].name()
        'halberd.json'
        >>> len(char.weapons)
        1
        >>> char.acquire_item(mhand)
        >>> char.equip_item(0)
        (True, '[ ] has equiped Mainhand Dagger')
        >>> char.weapons
        [<ezdm_libs.item.Item object at ...>]
        >>> char.weapons[0].displayname() == 'Mainhand Dagger'
        True
        >>> char.acquire_item(ohand)
        >>> char.equip_item(0)
        (True, '[ ] has equiped Offhand_Dagger')
        >>> char.weapons
        [<ezdm_libs.item.Item object at ...>, <ezdm_libs.item.Item object at ...>]
        >>> len(char.weapons)
        2
        >>> char.acquire_item(twohand)
        >>> char.equip_item(0)
        (True, '[ ] has equiped Halberd')
        >>> char.weapons[0].name()
        'halberd.json'
        >>> len(char.weapons)
        1
        """
        slots = []
        canwear = self.get('/conditional/armor_types', 0)
        armor_types = load_json('adnd2e', 'armor_types.json')
        shields = self.get('/conditional/shields', False)

        if isinstance(itemname, int):
            item = Item(self.get('/core/inventory/pack', [])[itemname])
        else:
            for item in [Item(i) for i in self.get('/core/inventory/pack', [])]:
                if item.displayname() == itemname:
                    break
        if not item.identified():
            item.identify()
        if self.character_type() == 'player':
            item.onequip(self)
        if item:
            if item.armortype() == 'shield' and not shields:
                return (False, "%s cannot wear %s shields like %s" % (self.displayname(), item.armortype(), item.displayname()))
            elif item.armortype() != 'shield' and item.itemtype() == 'armor' and canwear < armor_types[item.armortype()]:
                return (False, "%s cannot wear %s armor like %s" % (self.displayname(), item.armortype(), item.displayname()))
            if item.slot() == 'twohand':
                slots = ['lefthand', 'righthand']
            elif item.slot() == 'finger':
                left = self.get('/core/inventory/leftfinger', {})
                right = self.get('/core/inventory/rightfinger', {})
                if not left:
                    slots = ['leftfinger']
                if not right:
                    slots = ['rightfinger']
                if not slots:
                    slots = ['leftfinger']
            else:
                slots = [item.slot()]
            for slot in slots:
                self.unequip_item(slot)
                self.put('/core/inventory/equiped/%s' % slot.strip(), item())
            self.drop_item(item.displayname())
        return (True, "%s has equiped %s" % (self.displayname(), item.displayname()))

    def unequip_item(self, slot):
        """
        >>> char = Character({})
        >>> twohand = Item(load_json('items', 'halberd.json'))
        >>> char.acquire_item(twohand)
        >>> char.equip_item(twohand)
        (True, '[ ] has equiped Halberd')
        >>> char.unequip_item('lefthand')
        >>> char.get('/core/inventory/equiped/lefthand', {})
        {}
        >>> char.get('/core/inventory/equiped/lefthand', {})
        {}
        >>> char.weapons[0].name()
        'fist.json'
        """
        slot = slot.strip()
        current = Item(self.get('/core/inventory/equiped/%s' % slot, {}))
        debug(current)
        if current():
            if current.name() != 'fist.json':
                self.acquire_item(current)
            if current.get('/conditional/slot', '') == 'twohand':
                debug('Unequipping a twohanded weapon')
                for slot in ['lefthand', 'righthand']:
                    debug('unequiping from %s' % slot)
                    self.put('/core/inventory/equiped/%s' % slot, {})
            else:
                self.put('/core/inventory/equiped/%s' % slot, {})
            if self.character_type() == 'player':
                current.onunequip(self)

    def sell_price(self, gold, copper, silver):
            price = price_in_copper(gold, silver, copper)

            cha = int(self.get('/core/abilities/cha', 1))
            price = (price / 2) + ((price / 100) * cha)
            money = convert_money(price)
            return (int(money['gold']), int(money['silver']), int(money['copper']))

    def sell_item(self, itemname, buyer='shop', gold=0, silver=0, copper=0):
        if isinstance(itemname, int):
            tosell = Item(self.get('/core/inventory/pack', [])[itemname])
        else:
            for item in self.get('/core/inventory/pack', []):
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
        >>> char.acquire_item(Item(load_json('items', 'health_potion.json')))
        >>> char.for_sale()
        [(0, 'Health Potion', 'Gold 4, Silver 10, Copper 10')]
        """
        out = []
        pack = self.get('/core/inventory/pack', [])
        for i in pack:
            try:
                item = Item(i)
                if item.name() != '.json':
                    gold, silver, copper = self.sell_price(*item.price_tuple())
                    moneystr = 'Gold %s, Silver %s, Copper %s' % (int(gold), int(silver), int(copper))
                    out.append((pack.index(i), item.displayname(), moneystr))
            except Exception as e:
                raise Exception('Error loading %s - %s' % (self.displayname(), e))
        return out

    def drop_item(self, itemname, section='pack'):
        """
        >>> char = Character({})
        >>> char.acquire_item(Item(load_json('items','health_potion')))
        >>> char.drop_item('Health Potion')
        >>> len(char.get('/core/inventory/pack', []))
        0
        >>> char.acquire_item(Item(load_json('items','health_potion')))
        >>> char.drop_item(0)
        >>> len(char.get('/core/inventory/pack', []))
        0
        """
        todrop = None
        if isinstance(itemname, str):
            for item in self.get('/core/inventory/%s' % section, []):
                item = Item(item)
                if item.displayname() == itemname:
                    todrop = self.get('/core/inventory/%s' % section, []).index(item())
        else:
            todrop = itemname
        if todrop is None:
            return
        item = Item(self.json['core']['inventory']['pack'][todrop])
        if self.character_type() == 'player':
            item.ondrop(player=self)
        del(self.json['core']['inventory']['pack'][todrop])

    def money_tuple(self):
        gold = self.get('/core/inventory/money/gold', 0)
        silver = self.get('/core/inventory/money/silver', 0)
        copper = self.get('/core/inventory/money/copper', 0)
        return (int(gold), int(silver), int(copper))

    def spend_money(self, gold=0, silver=0, copper=0):
        ihave = price_in_copper(*self.money_tuple())
        price = price_in_copper(gold, silver, copper)
        remains = ihave - price
        if remains < 0:
            return False
        else:
            self.put('/core/inventory/money', convert_money(remains))
            return True

    def buy_item(self, item, page=None):
        if self.spend_money(*item.price_tuple()):
            self.acquire_item(item)
            page.message('You bought a %s' % item.name())
            return True
        else:
            page.error('You cannot afford to buy %s' % item.name())
            return False

    def gain_money(self, gold=0, silver=0, copper=0):
        total_gained = price_in_copper(gold, silver, copper)
        my_total = price_in_copper(*self.money_tuple())
        my_total += total_gained
        self.put('/core/inventory/money', convert_money(my_total))

    def armor_class(self):
        ac = 10.0
        for item in self.inventory_generator(['equiped']):
            ac -= float(item[1].get('/conditional/ac', 0.0))
        return ac

    def equiped_by_type(self, itemtype):
        arm = []
        equiped = self.get('/core/inventory/equiped', {})
        for slot in equiped:
            item = Item(equiped[slot])
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
        >>> char.weapons[0].name()
        'fist.json'
        >>> char.acquire_item(Item(load_json('items','halberd.json')))
        >>> char.equip_item(0)
        (True, '[ ] has equiped Halberd')
        >>> char.weapons[0].name()
        'halberd.json'
        >>> len(char.weapons)
        1
        """
        equipedweapons = self.equiped_by_type('weapon')
        debug(equipedweapons)
        if not equipedweapons:
            debug('No weapons equipped - equipping fist')
            fist = Item(load_json('items', 'fist.json'))
            self.acquire_item(fist)
            self.equip_item(0)
            equipedweapons = self.equiped_by_type('weapon')
        if equipedweapons and equipedweapons[0].get('/conditional/slot', "") == 'twohand':
            return equipedweapons[1:]
        return equipedweapons

    def num_weapons(self):
        return len(self.weapons)

    def num_attacks(self):
        atr_json = load_json('adnd2e', 'various')
        atr = readkey('/various/attacks_per_round', atr_json)
        parentclass = self.get('/core/class/parent', '')
        if parentclass not in atr:
            myatr = 1
        else:
            for key in list(atr[parentclass].keys()):
                if inrange(self.get('/core/combat/level-hitdice', 1), key):
                    myatr = int(atr[parentclass][key])
        return self.num_weapons() * int(myatr)

    def current_xp(self):
        return int(self.get('/core/personal/xp', 0))

    def abilities(self):
        subclass = self.get('/core/class/class', '')
        parentclass = self.get('/core/class/parent', '')
        level = self.get('/core/combat/level-hitdice', '')
        various = load_json('adnd2e', 'various')
        abilities = various['abilities']
        conditionals = self.get('/conditional/abilities', {})
        race = self.get('/core/personal/race', self())
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
        out = "%s %s" % (self.get('/core/personal/name/first', ''), self.get('/core/personal/name/last', ''))
        index = frontend.campaign.characterlist.index(self)
        if self.character_type() == 'npc':
            loc = self.location()
            if index > -1:
                out = "%s (%s)" % (out, index)
            out = '%s @%sx%s' % (out, loc['x'], loc['y'])
        out = "[%s]" % out
        return out

    @property
    def thac0(self):
        if self.get('/core/personal/race', '') == "creature":
            key = "creature"
        else:
            key = self.get('/core/class/parent', '')
        thac0s = load_json("adnd2e", "thac0")[key]
        for key2 in list(thac0s.keys()):
            if inrange(self.get('/core/combat/level-hitdice', 1), key2):
                return int(thac0s[key2])

    def render(self):
        """
        >>> char = Character(load_json('characters','tiny_tim.json'))
        >>> char.render()
        {...}
        >>> char = Character({})
        >>> char.render()
        {}
        """
        out = copy.deepcopy(self())
        if 'hash' in out:
            del(out['hash'])
        if 'core' in out:
            out['core']['lightradius'] = self.lightradius
            if 'saving_throws' in out['core']['combat']:
                del out['core']['combat']['saving_throws']
            prettynames = load_json('adnd2e', 'saving_throws')
            writekey('/conditional/abilities', self.abilities(), out)
            if not self.character_type() == 'player':
                out['XP Worth'] = self.xp_worth()
            for k, v in list(self.saving_throws.items()):
                prettyname = readkey('/names/%s' % k, prettynames, k)
                writekey('/core/combat/saving_throws/%s ' % prettyname, v, out)
            self.reset_weapon()
            out['core']['combat']['armor_class'] = self.armor_class()
            out['core']['combat']['thac0'] = self.thac0
            del(out['core']['inventory'])
            del(out['conditional']['armor_types'])
            out['to_hit_mod'] = self.to_hit_mod()

            if 'index' in out:
                del (out['index'])
            xp = self.get('/core/personal/xp', 0)
            nl = self.next_level()
            out['core']['personal']['xp'] = '%s/%s (%s to go)' % (xp, nl, nl - xp)
            armor_types = load_json('adnd2e', 'armor_types.json')
            armor_types = sorted(iter(armor_types.items()), key=operator.itemgetter(1))
            out['core']['combat']['Armor allowed'] = []
            for atype in armor_types:
                if atype[1] <= self.get('/conditional/armor_types', 0):
                    out['core']['combat']['Armor allowed'].append(atype[0])
        return out
