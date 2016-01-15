import pygame
from pygame.locals import *
from messages import messages
from util import debug, make_hash
from button import MouseOver

class AnimatedSprite(pygame.sprite.DirtySprite):
    animations = {
        "stand": ['Aquatic0.png:4:1:0','Aquatic0.png:5:1:90','Aquatic0.png:4:1:180','Aquatic0.png:5:1:270'],
        'walkleft': [],
        'walkright': [],
        'walkaway': [],
        'walktoward': []
    }
    def __init__(self, tilemaps, rect, animations={}, layer=2, fps=60, onarive=None):
        self._layer = layer
        self.framerate = 60/fps
        self.counter = 0
        self.pause = False
        super(pygame.sprite.DirtySprite, self).__init__()
        self.tilemaps = tilemaps
        self.animation = None
        if animations:
            self.animations = animations
        if 'stand' in self.animations:
            self.setanimation('stand')
        else:
            self.setanimation(self.animations.keys()[0])
        self.goto = (0,0)
        self.onarive = onarive
        self.onarive_params = []
        self.rect = rect
        self.image = self.currentimage()

    def setanimation(self, newanimation):
        if self.animation != newanimation:
            self.animation = newanimation
            self.frame =0

    def currentframe(self):
        if self.goto != (0,0):
            x, y = self.goto
            if y > self.rect.y:
                self.setanimation('walktoward')
                self.rect.y += 1
            elif y < self.rect.y:
                self.setanimation('walkaway')
                self.rect.y -= 1
            elif x > self.rect.x:
                self.setanimation('walkright')
                self.rect.x += 1
            elif x < self.rect.x:
                self.setanimation('walkleft')
                self.rect.x -= 1
            else:
                self.setanimation('stand')
                if self.onarive is not None:
                    self.goto = (0,0)
                    self.onarive(*self.onarive_params)
        try:
            return self.animations[self.animation][self.frame]
        except:
            return 'NoFrameSpecified'

    def nextframe(self):
        if self.frame < len(self.animations.get(self.animation,[])) -1:
            self.frame += 1
        else:
            self.frame = 0

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


class ButtonSprite(AnimatedSprite):
    def __init__(self, tilemaps, rect, eventstack, onclick=None, onclick_params=[], animations={}, layer=2, fps=60,sendself=False, mouseover='', frontend=None):
        self._layer = layer
        AnimatedSprite.__init__(self, tilemaps, rect, animations, layer, fps)
        self.registered_events = []
        self.eventstack = eventstack
        self.onclick = onclick
        self.onclick_params = onclick_params
        self.sendself = sendself
        self.registered_events.append(self.eventstack.register_event("button1", self, self.click))
        self.mouseover_text = mouseover
        if mouseover:
            self.mo_hash = make_hash()
            self.frontend = frontend
            self.registered_events.append(self.eventstack.register_event("mouseover", self, self.mouseover))

    def click(self, pos):
         if self.onclick is not None:
            if not self.sendself:
                self.onclick(*self.onclick_params)
            else:
                self.onclick(self, *self.onclick_params)

    def mouseover(self, pos):
        self.m = MouseOver(self.mouseover_text, pos, layer=self._layer +1)
        self.frontend.sprites[self.mo_hash] = self.m
        self.eventstack.register_event("mouseout", self, self.mouseout)

    def mouseout(self, pos):
        self.m.delete()
        if self.mo_hash in self.frontend.sprites:
            del self.frontend.sprites[self.mo_hash]

    def delete(self):
        for h in self.registered_events:
            self.eventstack.unregister_event(h)
        if self.mouseover_text and self.mo_hash in self.frontend.sprites:
            del self.frontend.sprites[self.mo_hash]
        self.kill()
