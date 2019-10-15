import pygame
import os
from pygame.locals import *
import sys
import mido

main_dir = os.path.split(os.path.abspath(__file__))[0]

def load_image(name):
    path = os.path.join(main_dir, 'data', name)
    return pygame.image.load(path).convert_alpha()

def list_dir(name):
    path = os.path.join(main_dir, name)
    return os.listdir(path)

def high_scores_filename():
    home = os.path.expanduser("~")
    rv = home + "/.meowzok-high-scores.csv"
    print (rv)
    return rv


def is_sharp(nn):
    return nn%12 in [1,3,6,8,10]

def wait_key():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN :
                if event.key == 27:
                    pygame.quit()
                    sys.exit()
                print(">>...>>", event)
                return


def format_score(score):   
    return str(int(score)).zfill(6)


def get_midi_input_ports():
    names = mido.get_input_names()
    if len(names) > 0:
        return names
    else:
        return None

def get_midi_output_ports():
    names = mido.get_output_names()
    if len(names) > 0:
        return names
    else:
        return None


