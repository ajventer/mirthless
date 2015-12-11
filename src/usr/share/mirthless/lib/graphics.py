# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *


def get_screen(resx, resy, hardware, fullscreen):
	flags = DOUBLEBUF
	if hardware:
		flags = flags | HWSURFACE
	if fullscreen:
		flags = flags | FULLSCREEN

	return  pygame.display.set_mode((resx, resy), flags)
