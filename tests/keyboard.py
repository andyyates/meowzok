#!/usr/bin/python3

import sys
sys.path.append("..")
import MKMidiFile as MF
from LilyDots import LilyDots as Dots
from MKUtil import *
import pygame
import MKGame
import random

from MKKeyboard import *

pygame.init()
screen = pygame.display.set_mode((1000,600))
surface = pygame.Surface(screen.get_size())




kbd = Keyboard()
kbd.right_keys = [random.randint(21,109) for x in range(0,5)]
kbd.wrong_keys = [random.randint(21,109) for x in range(0,5)]
kbd.draw(surface, pygame.Rect(200,300,1500,100))
kbd.draw(surface, pygame.Rect(0,0,surface.get_rect().width, 100))

screen.blit(surface, (0,0))
pygame.display.update()
wait_key()


