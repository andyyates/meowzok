#!/usr/bin/python3

import sys
sys.path.append("..")
import MKMidiFile as MF
from LilyDots import LilyDots as Dots
import MKUtil
import pygame
import MKGame
import time
import random
from MKStyle import style

pygame.init()
style.resize_big()
screen = pygame.display.set_mode(style.screensize)
surface = pygame.Surface(screen.get_size())


f = MF.MKMidiFile("midi/songs/maple_leaf_rag.mid")
rect = pygame.Rect(0,150,1000,300)

s = Dots(game_name = "Tetris", midi_file_path="midi/songs/maple_leaf_rag.mid", bars_per_page=4, notes=f.notes, time_sig=f.time_sig, size=rect)

i=2
while s.pages[i].loaded == False:
    time.sleep(0.4)
    print("waiting for page to load")

s.draw_music(surface, i)
for r in s.pages[i].note_xs:
    color = [random.randint(0,155) for x in range(0,3)]
    pygame.draw.rect(surface, color, r)

screen.blit(surface, (rect.x, rect.y))
pygame.display.update()
MKUtil.wait_key()


