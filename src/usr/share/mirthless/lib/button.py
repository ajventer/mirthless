import pygame
from pygame.locals import *
from util import debug, file_list, gamedir
from messagebox import MessageBox
from imagecache import ImageCache

def render_text (text, size=32, color=(0,0,0)):
    font = pygame.font.Font(None, size)
    rendered = font.render(str(text), 1, color)
    return rendered 

def scrn_print(surface, text, x, y, size=32, color=(0,0,0)):
    rendered_text = render_text(text, size=size, color=color)
    textpos = rendered_text.get_rect()
    textpos.centerx = x
    textpos.centery = y      
    surface.blit(rendered_text, textpos)


class Button(pygame.sprite.DirtySprite):
    def __init__(self, label, onclick, onclick_params, eventstack,imagecache, pos=(0,0)):
        self._layer = 10
        self.registered_events = []
        super(pygame.sprite.DirtySprite, self).__init__()
        button_rest = imagecache['button_rest']
        button_hi = imagecache['button_hi']
        button_click = imagecache['button_click']
        self.pos = pos
        self.onclick = onclick
        self.onclick_params = onclick_params
        self.label = render_text (label, size=24, color=(0,0,0))

        labelrect = self.label.get_rect()
        
        self.button_rest = pygame.transform.smoothscale(button_rest, (labelrect.w + 20, labelrect.h + 12))
        self.button_rest.blit(self.label,(10,6))

        self.button_hi = pygame.transform.smoothscale(button_hi, (labelrect.w + 20, labelrect.h + 12))
        self.button_hi.blit(self.label,(10,6))

        self.button_click = pygame.transform.smoothscale(button_click, (labelrect.w + 20, labelrect.h + 12))
        self.button_click.blit(self.label,(10,6))


        rect = self.button_rest.get_rect()

        self.eventstack = eventstack

        self.rect = pygame.Rect(pos[0], pos[1], rect.w, rect.h)

        self.registered_events.append(self.eventstack.register_event("mouseover", self, self.mouseover))
        self.registered_events.append(self.eventstack.register_event("button1", self, self.click))

        self.mouseout()

    def mouseover(self):
        self.image = self.button_hi
        self.eventstack.register_event("mouseout", self, self.mouseout)


    def mouseout(self):
        self.image = self.button_rest
        self.image.convert()
     
    def click(self, pos):
        self.image = self.button_click
        if self.onclick is not None:
            debug(self.onclick_params)
            self.onclick(*self.onclick_params)

    def delete(self):
        for h in self.registered_events:
            self.eventstack.unregister_event(h)
        self.kill()

class ButtonArrow(Button):
    def __init__(self, onclick, onclick_params, eventstack,imagecache, direction, pos=(0,0)):
        Button.__init__(self, '', onclick, onclick_params, eventstack, imagecache, pos)
        self.button_rest = imagecache['arrow_%s' %direction]
        self.button_hi = self.button_rest
        self.button_click = self.button_rest
        self.image = self.button_rest

class checkboxbtn(Button):
    checked = False
    def __init__(self, label, onclick, onclick_params, eventstack,imagecache, pos=(0,0)):
        self._layer = 10
        self.registered_events = []
        super(pygame.sprite.DirtySprite, self).__init__()
        self.pos = pos
        self.onclick = onclick
        self.onclick_params = onclick_params
        self.label = render_text (label, size=24, color=(255,255,255))

        labelrect = self.label.get_rect()        
                
        self.checkedimg = pygame.Surface((labelrect.w + 30, 31))
        self.uncheckedimg = pygame.Surface((labelrect.w + 30, 31))

        self.checkedimg.blit(imagecache['checkbtn_checked'], (0,0))
        self.uncheckedimg.blit(imagecache['checkbtn_unchecked'], (0,0))

        self.checkedimg.blit(self.label,(30,3))
        self.uncheckedimg.blit(self.label,(30,3))
        rect = self.uncheckedimg.get_rect()
        self.rect = pygame.Rect(pos[0],pos[1],rect.w, rect.h)
        self.eventstack = eventstack
        self.registered_events.append(self.eventstack.register_event("button1", self, self.click))

    @property
    def image(self):
        if self.checked:
            return self.checkedimg
        else:
            return self.uncheckedimg

    def click(self, pos):
        self.checked = not self.checked
        if self.onclick is not None:
            debug(self.onclick_params)
            self.onclick(*self.onclick_params)
