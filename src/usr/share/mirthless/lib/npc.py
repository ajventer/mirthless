from character import Character
from util import rolldice

class NPC(Character):
    def __init__(self, data, level):
        Character.__init__(self, data)
        #Scale up the NPC to match the player level
        self.put('combat/level-hitdice', level)
        self.roll_hit_dice()
        self.weapons

    @property
    def character_type(self):
        return 'npc'
    
