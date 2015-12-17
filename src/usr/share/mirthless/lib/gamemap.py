from objects import EzdmObject, event
from item import Item
from util import save_yaml, load_yaml,debug
import copy
from flatteneddict import FlattenedDict

class Tile(EzdmObject):
    """
    >>> t = Tile({})
    """
    def revealed(self):
        return self.get('core/revealed', False) is True

    def tiletype(self):
        return self.get('core/type', 'floor')

    def linktarget(self, target=None, x=0, y=0):
        if not target:
            return self.get('conditional/newmap', {})
        else:
            self.put('conditional/newmap', {'mapname': target, "x": x, "y": y})

    def background(self):
        return self.get('core/background',False)

    def canenter(self, new=None):
        if new is None:
            return self.get('conditional/canenter', False)
        self.put('conditional/canenter', new)

    def add(self, name, objtype):
        if isinstance(name, str) and not name.endswith('.yaml'):
            name = '%s.yaml' % name
        current = self.get('conditional/%s' % objtype, {})
        if objtype == 'npcs':
            if isinstance(name, str):
                name = Character(load_yaml('characters',name))
        else:
            if isinstance(name, str):
                name = Item(name)
        name.set_hash()
        current[name.get_hash()] = name()
        self.writesubtree('/conditional/%s' % objtype, current)

    def remove(self, hash, objtype):
        del self()['conditional/%s/%s' %(objtype, hash) ]

    def list(self, objtype):
        return self.get('/conditional/%s' % objtype, [])

    def onenter(self, player, page):
        event(self, "conditional/events/onenter", {'tile': self, 'page': page, 'player': player})


class GameMap(EzdmObject):
    """
    >>> g = GameMap({})
    >>> 'hash' in g()
    True
    >>> g.initialize()
    """
    max_x = 20
    max_y = 20
    def initialize(self, data={}, name='',lightradius=1):
        if not data:
            self.new()

        if not 'lightradius' in self():
            self()['lightradius'] = lightradius
        for y in range(0, self.max_y):
            for x in range(0, self.max_x):
                tile = self.tile(x, y)

    def new(self):
        self()['tiles'] = [[{}] * self.max_x for _ in range(self.max_y)]

    def load_tile_from_dict(self, x, y, dic):
        self()['tiles'][y][x] = dic

    def load_tile(self, x, y, tile):
        self.load_tile_from_dict(x, y, dict(tile()))

    def copy_tile(self, src_x, src_y, dest_x, dest_y):
        #Copies the tile definition
        #Does not copy items, npcs or monsters !
        source = self.tile(src_x, src_y)()
        dest = copy.deepcopy(source)
        filtered_keys = ['conditional/npcs', 'conditional/items', ['conditional/copper'], ['condition/silver'], ['conditional/gold']]
        for key in filtered_keys:
            del dest[key]
        self.load_tile_from_dict(dest_x, dest_y, dest)

    def tile(self, x, y):
        return Tile(self()['tiles'][y][x])

    def putmoney(self, x, y, gold, silver, copper):
        tile = self.tile(x, y)
        tile.put('conditional/gold', gold)
        tile.put('conditional/silver', silver)
        tile.put('conditional/copper', copper)
        self.load_tile_from_dict(tile())

    def getmoney(self, x, y):
        tile = self.tile(x, y)
        return (int(tile.get('conditional/gold', 0)), int(tile.get('conditional/silver', 0)), int(tile.get('conditional/copper', 0)))

    def addtotile(self, x, y, name, objtype):
        tile = self.tile(x, y)
        tile.add(name, objtype)
        self.load_tile_from_json(x, y, tile())
        self.save()

    def removefromtile(self, x, y, name, objtype):
        tile = self.tile(x, y)
        tile.remove(name, objtype)
        self.load_tile_from_json(x, y, tile())
        self.save()

    def tile_icons(self, x, y, unique=False):
        tile = self.tile(x, y)
        if not tile():
            return {}
        out = []
        for thingy in tile.get('/conditional/items', []):
            data = FlattenedDict(load_yaml('items', thingy))
            if data:
                i = Item(data)
                out.append((data.get('/core/icon', ''), 'items'))
        money = self.getmoney(x, y)
        if money[0] or money[1] or money[2]:
            #TODO - select a new gold icon and put here in the proper format.
            out.append(('money', 'tilemap:x:y', 'money'))
        if not unique:
            return out
        else:
            return list(set(out))

    def name(self):
        return self.get('name', '')

    def reveal(self, x, y, xtraradius=0):
        radius = int(self.get('lightradius', 1)) + xtraradius
        #TODO prevent looking through walls
        max_x = self.max_x
        max_y = self.max_y
        has_revealed = False
        debug("x", x, "max_x", max_x, "y", y, "max_y", max_y)
        left = x - radius
        if left < 0:
            left = 0
        right = x + radius + 1
        if right > max_x:
            right = max_x
        top = y - radius
        if top < 0:
            top = 0
        bottom = y + radius + 1
        if bottom > max_y:
            bottom = max_y
        debug("left", left, "top", top, "right", right, "bottom", bottom)
        for pt_y in range(top, bottom):
            for pt_x in range(left, right):
                tile = self.tile(pt_x, pt_y)
                if not tile.get('core/revealed', False):
                    has_revealed = True
                tile.put('/core/revealed', True)
                self.load_tile_from_json(pt_x, pt_y, tile())
        if has_revealed:
            #TODO - revealing may have included an enemy and started combat
            pass
        self.save()
