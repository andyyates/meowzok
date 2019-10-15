#!/usr/bin/python3

import sys
sys.path.append("..")
from MKGame import *
from LilyDots import LilyDots as Dots
from SloppyDots import SloppyDots as Dots
import MKUtil
import pygame
import MKGame

pygame.init()
style.resize_big()
screen = pygame.display.set_mode(style.screensize)
surface = pygame.Surface(screen.get_size())
style.resize(screen.get_rect().w,screen.get_rect().h)


game_globs.dot_class = Dots
lvls = load_midi_file("midi/songs/Tetris.mid")
g = Game(lvls)


#rect = pygame.Rect(0,150,1000,300)
#s = Dots(game_name = "Tetris", midi_file_path="midi/songs/Tetris.mid", bars_per_page=4, notes=f.notes, time_sig=f.time_sig, size=rect)


for i in range(0,10):
    g.note_down(50, [50])
    g.draw(surface)
    screen.blit(surface,(0,0))
    pygame.display.update()
    print("Waiting kye")
    MKUtil.wait_key()

    g.pop_active()

    g.note_down(None, [])
    g.draw(surface)
    screen.blit(surface,(0,0))
    pygame.display.update()
    print("Waiting kye")
    MKUtil.wait_key()

    g.pop_active()
