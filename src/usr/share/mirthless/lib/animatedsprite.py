import pygame
from pygame.locals import *
from messages import messages
from util import debug

class AnimatedSprite(pygame.sprite.DirtySprite):
    animations = {
        "stand": ['Aquatic0.png:4:1:0','Aquatic0.png:5:1:90','Aquatic0.png:4:1:180','Aquatic0.png:5:1:270'],
        'walkleft': [],
        'walkright': [],
        'walkup': [],
        'walkdown': []
    }
    def __init__(self, tilemaps, rect, animations={}, layer=2, fps=60):
        self._layer = layer
        self.framerate = 60/fps
        self.counter = 0
        self.pause = False
        super(pygame.sprite.DirtySprite, self).__init__()
        self.tilemaps = tilemaps
        if animations:
            self.animations = animations
        if 'stand' in self.animations:
            self.setanimation('stand')
        else:
            self.setanimation(self.animations.keys()[0])
        self.rect = rect
        self.image = self.currentimage()

    def setanimation(self, newanimation):
        self.animation = newanimation
        self.frame =0

    def currentframe(self):
        try:
            return self.animations[self.animation][self.frame]
        except:
            return 'NoFrameSpecified'

    def nextframe(self):
        debug('Nextframe called. Animation:', self.animation)
        if self.frame < len(self.animations[self.animation]) -1:
            self.frame += 1
        else:
            self.frame = 0
        debug ('Frame now ', self.frame)

    def currentimage(self):
        imgpath = self.currentframe()
        if imgpath == 'NoFrameSpecified':
            return pygame.Surface((self.rect.w, self.rect.h))
        img = self.tilemaps.get_by_path(imgpath)
        img = pygame.transform.smoothscale(img, (self.rect.w, self.rect.h))
        return img

    def update(self):
        self.counter += 1
        if not self.pause and self.counter%self.framerate == 0:
            self.nextframe()
        self.image = self.currentimage()

    def delete(self):
        self.kill()


