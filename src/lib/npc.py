from character import Character
from util import rolldice, load_yaml
from messages import messages

class NPC(Character):
    def __init__(self, data, level=1):
        Character.__init__(self, data)
        #Scale up the NPC to match the player level
        self.put('combat/level-hitdice', level)
        self.roll_hit_dice()
        self.weapons

    @property
    def character_type(self):
        return 'npc'

    def moveto(self, map, x, y):
        if not mapname:
            return
        if not isinstance(x, int) or not isinstance(y, int):
            try:
                x = int(x)
                y = int(y)
            except:
                return
        if not map.tile(x,y).canenter():
            return
        current = self.location()
        if current.get('map') and x and y:
            gamemap = GameMap(load_yaml('maps', current['map']))
            gamemap.removefromtile(current['x'], current['y'],self,'npc')
        map.addtotile(x, y, 'npc', self)
        if map.tile(x,y).revealed():
            messages.warning('%s moves to %sx%s' %(self.displayname(),x, y))


