import pygame
from pygame.locals import *
from util import file_path, debug
import re
from button import TextInput

def render_text (text, size=32, color=(0,0,0)):
    font = pygame.font.SysFont('monospace', size)
    #font = pygame.font.Font(file_path('fonts','BLKCHCRY.TTF'), size)
    return font.render(str(text), 1, color)

class MessageBox(pygame.sprite.DirtySprite):
    def __init__(self, messages, rect, frontend, defaultcolor=(255,255,255), hasdebugconsole=True, layer=0):
        self._layer=layer
        super(pygame.sprite.DirtySprite, self).__init__()
        self.frontend = frontend
        self.messages = messages
        self.defaultcolor = defaultcolor
        self.up = self.frontend.eventstack.register_event("wheelup", self, messages.scrollup) 
        self.down = self.frontend.eventstack.register_event("wheeldown", self, messages.scrolldown)
        self.rect = rect
        self.has_focus = True
        self.surface = pygame.Surface((self.rect.w, self.rect.h))
        self.background = self.surface.copy()
        self.image = self.surface
        if hasdebugconsole:
            self.frontend.eventstack.register_event("keydown", self, self.toggledebug)

    def toggledebug(self, event):
        if event.key == K_BACKQUOTE:
            if 'debugconsole' in self.frontend.sprites:
                del self.frontend.sprites['debugconsole']
                self.debug_console.delete()
            else:
                debug_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, 25)
                self.debug_console = TextInput(debug_rect, 16,
                    self.frontend.eventstack,
                    prompt='>>>',
                    clearprompt=True,
                    layer=self._layer+1,
                    name='debug',
                    onreturn=self.debugcmd,
                    onreturn_args=[])
                self.frontend.sprites['debugconsole'] = self.debug_console


    def debugcmd(self):
        command = self.debug_console.text
        debug('DEBUG CONSOLE: ', command)
        self.debug_console.text = ''
        try:
            code_locals = locals()
            code_locals.update({'player': self.frontend.game.player, 'game': self.frontend.game, 'frontend':self.frontend, 'messages': self.messages})
            code_globals = globals()
            exec command in code_globals, code_locals
        except Exception as E:
            self.messages.message('')
            self.messages.error('Error executing command: '+str(E))
            self.messages.message('')

    def delete(self):
        self.frontend.eventstack.unregister_event(self.up)
        self.frontend.eventstack.unregister_event(self.down)
        self.kill()

    def update(self):
        self.surface.blit(self.background, (0,0))
        y = self.surface.get_rect().y
        for line in self.messages.read():
            color=self.defaultcolor
            pattern = r'{{(.*)}}'
            m = re.search(pattern, line)
            if m:
                color = tuple([int(i) for i in m.groups()[0].split(',')])
                line = re.sub(pattern, '', line)
            lineimg=render_text(line, 16, color)
            self.surface.blit(lineimg,(10,y))
            y += lineimg.get_rect().h
        self.image = self.surface


