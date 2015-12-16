from glyph import Editor, Glyph, Macros
from pygame import display
from pygame import draw
from pygame import event
from pygame.font import Font
from pygame import image
from pygame import mouse
from pygame import transform
from pygame.locals import *
from util import file_path
# DEFAULT_CURSOR = mouse.get_cursor()

# #the hand cursor
# _HAND_CURSOR = (
# "     XX         ",
# "    X..X        ",
# "    X..X        ",
# "    X..X        ",
# "    X..XXXXX    ",
# "    X..X..X.XX  ",
# " XX X..X..X.X.X ",
# "X..XX.........X ",
# "X...X.........X ",
# " X.....X.X.X..X ",
# "  X....X.X.X..X ",
# "  X....X.X.X.X  ",
# "   X...X.X.X.X  ",
# "    X.......X   ",
# "     X....X.X   ",
# "     XXXXX XX   ")
# _HCURS, _HMASK = pygame.cursors.compile(_HAND_CURSOR, ".", "X")
# HAND_CURSOR = ((16, 16), (5, 1), _HCURS, _HMASK)

DEFAULT = {
    'bkg'       : (11, 11, 11),
    'color'     : (201, 192, 187),
    'font'      : Font(file_path('fonts','BLKCHCRY.TTF'), 16),
    'spacing'   : 0, #FONT.get_linesize(),
    }

class MessageBox():
    def __init__(self, CLIP):
        self.glyph = Glyph(CLIP, ncols=2, **DEFAULT)

    def image(self, text):
        glyph = self.glyph
        glyph_rect = glyph.rect
        glyph.input(text, justify = 'justified')
        glyph.update()
        return glyph.image, glyph_rect

    def clear(self, screen, background):
    	self.glyph.clear(screen, background)

