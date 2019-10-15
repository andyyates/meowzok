#!/usr/bin/python3
import pygame
from meowzok.util import *

class Key:
    def __init__(self, nn, black, rect):
        self.nn  = nn
        self.black = black
        self.rect = rect



class Keyboard:
    def __init__(self):
        self.right_keys = []
        self.wrong_keys = []
        self.keys = []
        for i in range(21, 109):
            if is_sharp(i):
                self.keys.append(Key(i, 1 , None))
            else:
                self.keys.append(Key(i, 0, None))
        self.__resize(pygame.Rect(0,0,500,100))

    def __resize(self, offset):
        self.offset = offset
        w = offset.width
        h = offset.height
        self.w = w
        self.key_w = key_w = int(w/52)
        self.key_h = h
        self.h = h
        x = (w - (self.key_w*52)) / 2
        for k in self.keys:
            if is_sharp(k.nn):
                k.rect = pygame.Rect(x-key_w/3+offset.left, offset.top, key_w*2/3, h * 0.6)
            else:
                k.rect = pygame.Rect(x+offset.left, offset.top, self.key_w, h)
                x+= self.key_w

    def __draw_key(self, surface, k):
        if k.nn in self.right_keys:
            pygame.draw.rect(surface, (0,200,200), k.rect)
        else:
            if k.black == 1:
                pygame.draw.rect(surface, (0,0,0), k.rect)
        pygame.draw.rect(surface, (100,100,100), k.rect, 1)
        if k.nn in self.wrong_keys:
            pygame.draw.rect(surface, (200,0,0), (k.rect.left, k.rect.bottom-self.key_w, k.rect.width, self.key_w))

    def draw(self, surface, offset):
        if offset != self.offset:
            self.__resize(offset)
        pygame.draw.rect(surface, (255,255,255), (offset.x, offset.y, self.w, self.h))
        for k in self.keys:
            if k.black == 0:
                self.__draw_key(surface, k)
        for k in self.keys:
            if k.black == 1:
                self.__draw_key(surface, k)

