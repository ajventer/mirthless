from player import Player
import os
from util import gamedir

class Game(object):
    livecharacters = []
    def __init__():


    def setsavedir(self, slot):
        self.slot = slot
        homedir = os.getenv('HOME')
        savedir = os.path.join(homedir,'.mirthless',slot)
        debug('Game save directory:', savedir)
        if not os.path.exists(directory):
            os.makedirs(directory)
        gamedir.append(savedir)

    def newgame(self, slot):
        self.setsavedir(slot)
        self.player = Player({})
        player.savetoslot(slot)


    def loadgame(self, slot):
        self.setsavedir(slot)
        self.player = Player(load_yaml('player','player.yaml'))
