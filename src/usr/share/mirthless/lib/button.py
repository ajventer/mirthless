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

class Label(pygame.sprite.DirtySprite):
    def __init__(self, text,pos, layer=6):
        self._layer = layer
        super(pygame.sprite.DirtySprite, self).__init__()
        self.image = render_text (text, size=16, color=(255,0,0), font=None)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.name = ''
        self.value = text

    def delete(self):
        self.kill()

class Button(pygame.sprite.DirtySprite):
    def __init__(self, label, onclick, onclick_params, eventstack,imagecache, pos=(0,0), layer=2, name='', sendself=False, fontsize=16):
        self._layer = layer
        self.registered_events = []
        self.name = name
        super(pygame.sprite.DirtySprite, self).__init__()
        button_rest = imagecache['button_rest']
        button_hi = imagecache['button_hi']
        button_click = imagecache['button_click']
        self.pos = pos
        self.onclick = onclick
        self.onclick_params = onclick_params
        self.sendself = sendself
        #self.label = render_text (label, size=fontsize, color=(20,250,20))
        self.label = render_text (label, size=fontsize, color=(255,255,255))

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

        self.mouseout(None)

    def mouseover(self, pos):
        self.image = self.button_hi
        self.eventstack.register_event("mouseout", self, self.mouseout)


    def mouseout(self, pos):
        self.image = self.button_rest
        self.image.convert()
     
    def click(self, pos):
        self.image = self.button_click
        if self.onclick is not None:
            if not self.sendself:
                self.onclick(*self.onclick_params)
            else:
                self.onclick(self, *self.onclick_params)

    def delete(self):
        for h in self.registered_events:
            self.eventstack.unregister_event(h)
        self.kill()

class BlitButton(Button):
    def __init__(self, onclick, onclick_params, eventstack,imagecache, imagekey, pos=(0,0), layer=10, scale=0):
        self._layer = layer
        Button.__init__(self, '', onclick, onclick_params, eventstack, imagecache, pos, layer)
        self.button_rest = imagecache[imagekey].copy()
        if scale:
            self.button_rest = pygame.transform.smoothscale(self.button_rest, (scale, scale))
        self.button_hi = self.button_rest
        self.button_click = self.button_rest
        self.image = self.button_rest
        self.rect = self.button_rest.get_rect()
        self.rect.x, self.rect.y = pos

class ButtonArrow(BlitButton):
    def __init__(self, onclick, onclick_params, eventstack,imagecache, direction, pos=(0,0), layer=10):
        self._layer = layer
        BlitButton.__init__(self, onclick, onclick_params, eventstack, imagecache,'arrow_%s' %direction, pos, layer)

class checkboxbtn(Button):
    checked = False
    def __init__(self, label, onclick, onclick_params, eventstack,imagecache, pos=(0,0),fontsize=16, layer=6, name='', sendself=False):
        self._layer = layer
        self.registered_events = []
        self.name = name
        super(pygame.sprite.DirtySprite, self).__init__()
        self.pos = pos
        self.sendself = sendself
        self.onclick = onclick
        self.onclick_params = onclick_params
        self.label = render_text (label, size=fontsize, color=(255,0,20))

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
    def value(self):
        return self.checked

    @property
    def image(self):
        if self.checked:
            return self.checkedimg
        else:
            return self.uncheckedimg

    def click(self, pos):
        self.checked = not self.checked
        if self.onclick is not None:
            if not self.sendself:
                self.onclick(*self.onclick_params)
            else:
                self.onclick(self, self.checked, *self.onclick_params)

class TextInput(pygame.sprite.DirtySprite):
    def __init__(self, rect, fontsize, eventstack, prompt='', clearprompt=True, layer=1, name=''):
        self.prompt = prompt
        self.clearprompt = clearprompt
        self.text = prompt
        self._layer = layer
        self.registered_events = []
        self.name = name
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
    def value(self):
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

class Dropdown(pygame.sprite.DirtySprite):
    def __init__(self, eventstack, imagecache, fontsize, rect, choices,layer=7, choice='',onselect=None,name='', sendself=False):
        self._layer = layer
        super(pygame.sprite.DirtySprite, self).__init__()
        self.name = name
        self.sendself = sendself
        self.onselect = onselect
        self.choicerects = {}
        self.eventstack = eventstack
        self.fontsize = fontsize
        self.imagecache = imagecache
        self.uprect = pygame.Rect(rect.x, rect.y, rect.w, rect.h)
        self.downrect = pygame.Rect(rect.x, rect.y, rect.w, rect.h * (len(choices) + 1))
        self.rect = self.uprect
        self.choices = choices
        self.choice = choice
        self.font=pygame.font.SysFont('monospace',self.fontsize)
        self.upsurface = pygame.Surface((self.uprect.w, self.uprect.h))
        self.dnsurface = pygame.Surface((self.downrect.w, self.downrect.h))
        self.upsurface.fill((255,255,255))
        self.arrow_down = pygame.transform.smoothscale(imagecache['arrow_down'],(32,self.rect.h))
        self.upsurface.blit(self.arrow_down,(rect.w - 30, 0))
        counter = 1
        self.image = self.upsurface
        self.registered_events = []
        self.registered_events.append(self.eventstack.register_event("button1", self, self.click))
        self.registered_events.append(self.eventstack.register_event("mouseover", self, self.mouseover))
        self.mouseover('force')
        self.down = False
        self.upsurface.blit(render_text (self.choice, font=self.font, color=(0,0,0)),(0,0))

    @property
    def value(self):
        return self.choice

    def itemsurface(self, choice, highlight=False):
        surface = pygame.Surface((self.uprect.w, self.uprect.h))
        if highlight:
            surface.fill((170,178,255))
        else:
            surface.fill((170,178,181))
        surface.blit(render_text (choice, font=self.font, color=(0,0,0)),(0,0))
        return surface

    def delete(self):
        for h in self.registered_events:
            self.eventstack.unregister_event(h)
        self.kill()

    def mouseover(self, pos):
        x,y = 0,0
        if not isinstance(pos, str):
            x, y = pos
        counter = 1
        if isinstance(pos, str) or (self.down and y > self.uprect.y + self.uprect.h):
            for c in self.choices:
                choicerect = pygame.Rect(self.uprect.x,self.uprect.y + self.uprect.h*counter, self.downrect.w, self.uprect.h)
                if choicerect.collidepoint(x,y):
                    choicesurface = self.itemsurface(c, True)
                else:
                    choicesurface = self.itemsurface(c)
                self.dnsurface.blit(choicesurface,(0,self.uprect.h*counter))
                self.choicerects[c] = choicerect
                counter += 1


    def click(self, pos):
        x, y = pos
        if self.down and y > self.uprect.y + self.uprect.h:
            for k,v in self.choicerects.items():
                if v.collidepoint(x,y):
                    self.choice = k
                    self.upsurface.fill((255,255,255))
                    self.upsurface.blit(render_text (k, font=self.font, color=(0,0,0)),(0,0))
                    self.upsurface.blit(self.arrow_down,(self.uprect.w - 30, 0))
                    if self.onselect is not None:
                        if not self.sendself:
                            self.onselect(self.choice)
                        else:
                            self.onselect(self, self.choice)
                    break
        self.down = not self.down

    def update(self):
        self.dnsurface.blit(self.upsurface,(0,0))
        if self.down:
            self.image = self.dnsurface
            self.rect = self.downrect
        else:
            self.image = self.upsurface
            self.rect = self.uprect


