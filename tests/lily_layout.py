#!/usr/bin/python3

import sys
sys.path.append("..")
import MKMidiFile as MF
from LilyDots import LilyDots as Dots
import MKUtil
import pygame
import MKGame

pygame.init()
screen = pygame.display.set_mode((1000,600))
surface = pygame.Surface(screen.get_size())


f = MF.MKMidiFile("midi/songs/Tetris.mid")
rect = pygame.Rect(0,150,1000,300)

s = Dots(game_name = "Tetris", midi_file_path="midi/songs/Tetris.mid", bars_per_page=4, notes=f.notes, time_sig=f.time_sig, size=rect)

for i in range(0,4):
    s.draw_music(surface, i)
    screen.blit(surface, (rect.x, rect.y))
    pygame.display.update()
    MKUtil.wait_key()


