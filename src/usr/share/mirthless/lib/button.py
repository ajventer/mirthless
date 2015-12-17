import pygame
from pygame.locals import *
from util import debug, file_list, gamedir
from messagebox import MessageBox
from imagecache import ImageCache
from util import file_path

def render_text (text, size=32, color=(0,0,0), font=None):
    #font = pygame.font.SysFont('monospace', size)
    if font is None:
        font = pygame.font.Font(file_path('fonts','BLKCHCRY.TTF'), size)
    return font.render(str(text), 1, color)

def scrn_print(surface, text, x, y, size=32, color=(0,0,0)):
    rendered_text = render_text(text, size=size, color=color)
    textpos = rendered_text.get_rect()
    textpos.centerx = x
    textpos.centery = y      
    surface.blit(rendered_text, textpos)


class Button(pygame.sprite.DirtySprite):
    def __init__(self, label, onclick, onclick_params, eventstack,imagecache, pos=(0,0), layer=2):
        self._layer = layer
        self.registered_events = []
        super(pygame.sprite.DirtySprite, self).__init__()
        button_rest = imagecache['button_rest']
        button_hi = imagecache['button_hi']
        button_click = imagecache['button_click']
        self.pos = pos
        self.onclick = onclick
        self.onclick_params = onclick_params
        self.label = render_text (label, size=16, color=(20,250,20))

        labelrect = self.label.get_rect()
        
        self.button_rest = pygame.transform.smoothscale(button_rest, (labelrect.w + 50, labelrect.h + 12))
        self.button_rest.blit(self.label,(25,6))

        self.button_hi = pygame.transform.smoothscale(button_hi, (labelrect.w + 50, labelrect.h + 12))
        self.button_hi.blit(self.label,(25,6))

        self.button_click = pygame.transform.smoothscale(button_click, (labelrect.w + 50, labelrect.h + 12))
        self.button_click.blit(self.label,(25,6))


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
            self.onclick(*self.onclick_params)

    def delete(self):
        for h in self.registered_events:
            self.eventstack.unregister_event(h)
        self.kill()

class ButtonArrow(Button):
    def __init__(self, onclick, onclick_params, eventstack,imagecache, direction, pos=(0,0), layer=10):
        self._layer = layer
        Button.__init__(self, '', onclick, onclick_params, eventstack, imagecache, pos, layer)
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
        self.label = render_text (label, size=24, color=(255,0,20))

        labelrect = self.label.get_rect()        
                
        self.checkedimg = pygame.Surface((labelrect.w + 30, 31),pygame.SRCALPHA, 32)
        self.uncheckedimg = pygame.Surface((labelrect.w + 30, 31),pygame.SRCALPHA, 32)
        self.checkedimg.convert_alpha()
        self.uncheckedimg.convert_alpha()


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
            self.onclick(*self.onclick_params)

class TextInput(pygame.sprite.DirtySprite):
    def __init__(self, rect, fontsize, eventstack, prompt='', clearprompt=True):
        self.prompt = prompt
        self.clearprompt = clearprompt
        self.text = prompt
        self._layer = 10
        self.registered_events = []
        super(pygame.sprite.DirtySprite, self).__init__()
        self.rect = rect
        self.fontsize = fontsize
        self.eventstack = eventstack
        self.registered_events.append(self.eventstack.register_event("keydown", self, self.kb))
        self.registered_events.append(self.eventstack.register_event("button1", self, self.click))
        self.cur = False
        self.cpos = len(self.text)
        self.counter = 0
        self.capslock = False
        self.has_focus = False

    def get_text(self):
        if self.text == self.prompt:
            return ''
        else:
            return self.text

    @property
    def image(self):
        self.counter += 1
        if (self.counter == 1 or self.counter%10 == 0) and self.has_focus:
            self.cur = not self.cur
        cur = self.cur and '-' or '_'
        out = list(self.text)
        if self.cpos >= len(out):
            out.append(cur)
        else:
            out.insert(self.cpos,cur)
        surface = pygame.Surface((self.rect.w, self.rect.h))
        surface.fill((255,255,255))
        surface.blit(render_text (''.join(out), color=(0,0,0), font=pygame.font.SysFont('monospace',self.fontsize)), (3,3))
        return surface

    def kb(self, event):
        #This method almost certainly could be made a lot better
        if not self.has_focus:
            return
        if event.key == K_BACKSPACE:
            if len(self.text) > 0:
                try:
                    out = list(self.text)
                    del out[self.cpos -1]
                    self.text = ''.join(out)
                except:
                    self.cpos = len(self.text)
        elif event.key == K_DELETE:
            if len(self.text) > 0 and self.cpos < len(self.text):
                try:
                    out = list(self.text)
                    del out[self.cpos]
                    self.text = ''.join(out)
                except:
                    self.cpos = len(self.text)
        elif event.key == K_CAPSLOCK:
            self.capslock = not self.capslock
        elif event.key == K_RETURN:
            self.has_focus = False
        elif event.key == K_SPACE:
            self.text += ' '
        elif event.key == K_LEFT:
            if self.cpos > 0: self.cpos -= 1
        elif event.key == K_RIGHT:
            if self.cpos < len(self.text): self.cpos += 1            
        else:
            if not self.capslock:
                new = event.unicode
            else:
                new = event.unicode.upper()
            out = list(self.text)
            try:
                out.insert(self.cpos, new)
            except:
                out.append(new)
            self.text = ''.join(out)
            self.cpos += 1

    def delete(self):
        for h in self.registered_events:
            self.eventstack.unregister_event(h)
        self.kill()

    def click(self, pos):
        self.has_focus = True
        if self.clearprompt and self.text == self.prompt:
            self.text = ''

