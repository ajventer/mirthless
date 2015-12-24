from player import Player
import os

class Game(object):
    def __init__(slot):
        self.slot = slot
        homedir = os.getenv('HOME')
        savedir = os.path.join(homedir,'.mirthless',slot)
        debug('Game save directory:', savedir)
