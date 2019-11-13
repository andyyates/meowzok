import pygame
import os
from pygame.locals import *
import sys

main_dir = os.path.split(os.path.abspath(__file__))[0]

def load_image(name):
    path = os.path.join(main_dir, 'data', name)
    return pygame.image.load(path).convert_alpha()

def high_scores_filename():
    home = os.path.expanduser("~")
    rv = home + "/.meowzok-high-scores.csv"
    return rv


def is_sharp(nn):
    return nn%12 in [1,3,6,8,10]



