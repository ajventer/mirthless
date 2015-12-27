from character import Character
from util import gamedir, load_yaml
import json
from messages import messages
import os
from gamemap import GameMap

class Player(Character):

    @property
    def character_type(self):
        return 'player'


    def savetoslot(self):
        savedir = gamedir[0]
        filename = os.path.join(savedir,'player','player.yaml')
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        open(filename, 'w').write(json.dumps(self(),indent=4))

    def moveto(self, map, x, y):
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
            gamemap.removefromtile(current['x'], current['y'],self,'player')
        self.put('location/x', x)
        self.put('location/y', y)
        self.put('location/map', map.get_hash())
        map.addtotile(x, y, 'player', True)
        messages.warning('%s moves to %sx%s' %(self.displayname(),x, y))
        map.reveal(x, y, self.lightradius)
