from character import Character
from util import rolldice

class NPC(Character):
    def __init__(self, data, level):
        Character.__init__(self, data)
        #Scale up the NPC to match the player level
        self.put('combat/level-hitdice', level)
        if int(self.get('combat/hitpoints', 0)) == 0:
            maxhp = rolldice(numdice=level, numsides=8, modifier=0)
            self.put('combat/hitpoints', maxhp)
            self.put('combat/maxhp', maxhp)

    @property
    def character_type(self):
        return 'npc'
    
