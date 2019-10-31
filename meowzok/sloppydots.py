#!/usr/bin/python3
import pygame
from meowzok.util import *
import math
from meowzok.style import style

class Sprites:
    def __cut(self, x, y):
        rect = pygame.Rect((x*self.height,y*self.height,self.height,self.height))
        image = self.sheet.subsurface(rect)
        return image

    def __init__(self, semih):
        self.width = self.height = semih * 18
        self.sheet = load_image("meowzok-sprites.png")
        w,h = self.sheet.get_size()
        self.sheet = pygame.transform.scale(self.sheet, (self.height*16, self.height*3))
        self.lines = []
        for i in range(9,-1,-1):
            image = self.__cut(i,0)
            self.lines.append([ image , pygame.transform.rotate(image,180) ])
        self.note_images = []
        for i in range(10,16):
            self.note_images.append([self.__cut(i,0), self.__cut(i,1)])
        self.treble_clef = self.__cut(0,1)
        self.bass_clef = self.__cut(1,1)
        self.sharp = self.__cut(2,1)
        self.flat = self.__cut(3,1)
        self.natural = self.__cut(4,1)
        self.life = self.__cut(0,2)
        self.star = self.__cut(1,2)
        self.splat = self.__cut(2,2)
        self.splat_sharp = self.__cut(3,2)
        self.splat_blue = self.__cut(4,2)

class Layout:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.colw = colw = int(self.w/10)
        self.semih = semih = int(self.h/56)
        self.rowh = rowh = semih*8
        self.sprites = Sprites(semih)
        self.treb = pygame.Rect((0,semih*16,self.w,rowh))
        self.bass = pygame.Rect((0,semih*32,self.w,rowh))



class SloppyDots():
    def __init__(self, midifile):
        #game_name, midi_file_path, bars_per_page, notes, time_sig, size):
        #self.layout.resize(size.w,size.h)
        self.layout = Layout(100,100)
        self.midifile = midifile
        self.note_names = {0:"C",1:"C#/Db",2:"D",3:"D#/Eb",4:"E",5:"F",6:"F#/Gb",7:"G",8:"G#/Ab",9:"A",10:"A#/Bb",11:"B",12:"C",13:"C#/Db",14:"D",15:"D#/Eb",16:"E",17:"F",18:"F#/Gb",19:"G",20:"G#/Ab",21:"A",22:"A#/Bb",23:"B",24:"C",25:"C#/Db",26:"D",27:"D#/Eb",28:"E",29:"F",30:"F#/Gb",31:"G",32:"G#/Ab",33:"A",34:"A#/Bb",35:"B",36:"C",37:"C#/Db",38:"D",39:"D#/Eb",40:"E",41:"F",42:"F#/Gb",43:"G",44:"G#/Ab",45:"A",46:"A#/Bb",47:"B",48:"C",49:"C#/Db",50:"D",51:"D#/Eb",52:"E",53:"F",54:"F#/Gb",55:"G",56:"G#/Ab",57:"A",58:"A#/Bb",59:"B",60:"C",61:"C#/Db",62:"D",63:"D#/Eb",64:"E",65:"F",66:"F#/Gb",67:"G",68:"G#/Ab",69:"A",70:"A#/Bb",71:"B",72:"C",73:"C#/Db",74:"D",75:"D#/Eb",76:"E",77:"F",78:"F#/Gb",79:"G",80:"G#/Ab",81:"A",82:"A#/Bb",83:"B",84:"C",85:"C#/Db",86:"D",87:"D#/Eb",88:"E",89:"F",90:"F#/Gb",91:"G",92:"G#/Ab",93:"A",94:"A#/Bb",95:"B",96:"C",97:"C#/Db",98:"D",99:"D#/Eb",100:"E",101:"F",102:"F#/Gb",103:"G",104:"G#/Ab",105:"A",106:"A#/Bb",107:"B",108:"C",109:"C#/Db",110:"D",111:"D#/Eb",112:"E",113:"F",114:"F#/Gb",115:"G",116:"G#/Ab",117:"A",118:"A#/Bb",119:"B",120:"C",121:"C#/Db",122:"D",123:"D#/Eb",124:"E",125:"F",126:"F#/Gb",127:"G"}

        self.note_length_images = {
                "1":0,
                "1.":0,
                "2":1,
                "2.":1,
                "4":2,
                "4.":2,
                "8":3,
                "8.":3,
                "16":4,
                "16.":4,
                "32":5,
                "32.":5,
                "64":5,
                "64.":5
        }

    def resize(self, w, h):
        if self.layout.w == w and self.layout.h == h:
            return

        self.layout = Layout(w,h)
        self.treb_pos = {}
        prev = "C"
        j = self.layout.treb[1]+self.layout.treb[3]+28*self.layout.semih
        for i in range(0,127):
            n = self.note_names[i]
            if n.find(prev) == -1:
                j -= self.layout.semih
            self.treb_pos[i] = j
            prev = n

        self.bass_pos = {}
        prev = "C"
        j = self.layout.bass[1]+self.layout.bass[3]+16*self.layout.semih
        for i in range(0,127):
            n = self.note_names[i]
            if n.find(prev) == -1:
                j -= self.layout.semih
            self.bass_pos[i] = j
            prev = n


    


    def __draw_st(self, stave, surface, icon):
        #pygame.draw.rect(surface, color.stave_bg, stave)
        l,t,w,h=stave
        w = surface.get_rect().w
        for i in range(0,9,2):
            pygame.draw.rect(surface, style.stave_fg, (0, t+self.layout.semih*i, w, 1))
        surface.blit(icon, (l,t-self.layout.rowh/2), None)


    #def draw(self, surface, active_i=None, notes=[], time_sig=None, time=None):
    def draw_music(self, surface, page_i):
        dim = surface.get_rect()
        self.resize(dim.width, dim.height)

        #copy current frame to rect
        #draw time line on
        #draw notes down on

        surface.fill(style.bg)
        self.__draw_st(self.layout.treb, surface, self.layout.sprites.treble_clef)
        self.__draw_st(self.layout.bass, surface, self.layout.sprites.bass_clef)

        bar_len_ticks = self.midifile.time_sig.get_bar_len()
        left_pad = self.layout.sprites.width
        time_to_px = (self.layout.treb.width - left_pad) / (bar_len_ticks*style.bars_per_page)
        #print("calc next page")
        #print(time, style.bars_per_page, self.bar_len_ticks)
        left_bar = page_i * style.bars_per_page
        #print(left_bar)
        left_time = left_bar * bar_len_ticks
        right_time = left_time + (style.bars_per_page * bar_len_ticks)
        #print("Drawing new staves", left_time, right_time, time, left_bar)
        for nl in self.midifile.active_notes:
            for n in nl:
                if n.time >= left_time - 50 and n.time < right_time:
                    n.x = (n.time - left_time) * time_to_px + left_pad - self.layout.sprites.width/2
                    #print(n.time, right_time, self.layout.note_names[n.nn], n.clef)
                    self.__draw_note(n, surface)
        for i in range(left_time, right_time+1, bar_len_ticks):
            bar_no = int(i/bar_len_ticks)+1
            
            #text = self.layout.font.render(str(bar_no), 1, (10, 10, 10))
            l = (i-left_time) * time_to_px + left_pad - self.layout.semih*2
            #textpos = text.get_rect()
            #textpos.left = l
            #textpos.bottom= self.layout.treb.top
            #surface.blit(text, textpos)
            pygame.draw.rect(surface, style.stave_fg, (l, self.layout.treb.top, 2, self.layout.semih * 8))
            pygame.draw.rect(surface, style.stave_fg, (l, self.layout.bass.top, 2, self.layout.semih * 8))

    def draw_time_line(self, surface, offset, page_i, time):
        xo = offset.x
        yo = offset.y
        bar_len_ticks = self.midifile.time_sig.get_bar_len()
        left_bar = page_i * style.bars_per_page
        left_time = left_bar * bar_len_ticks
        right_time = left_time + (style.bars_per_page * bar_len_ticks)
        if time < left_time or time > right_time:
            return
        left_pad = self.layout.sprites.width
        time_to_px = (self.layout.treb.width - left_pad) / (bar_len_ticks*style.bars_per_page)
        l = (time - left_time) * time_to_px + left_pad
        pygame.draw.rect(surface, style.time_line, (l+xo, self.layout.treb.top+yo, 2, self.layout.semih * 8))
        pygame.draw.rect(surface, style.time_line, (l+xo, self.layout.bass.top+yo, 2, self.layout.semih * 8))



    def blob_note(self, surface, active_note_i, nn, color, offset):
        nl = self.midifile.active_notes[active_note_i]
        for note in nl:
            self.__set_note_y(note)
            c = self.layout.sprites.width/2
            x = int(note.x+c) + offset.left
            y = int(note.y+c) + offset.top
            pygame.draw.circle(surface, color, (x,y), self.layout.semih)


    def __set_note_y(self, note):
        if note.clef == 0:
            c = self.layout.treb
            note.y = self.treb_pos[note.nn]
        else:
            c = self.layout.bass
            note.y = self.bass_pos[note.nn]



    def __draw_note(self, note, surface, alt_sprite = None, alt_sprite_sharp = None):

        self.__set_note_y(note)
        if note.clef == 0:
            l,t,w,h = self.layout.treb
        else:
            l,t,w,h = self.layout.bass
        y = note.y+self.layout.semih*8

        if_flip = 0
        has_lines = -1

        if alt_sprite:
            note.sprite = alt_sprite
            surface.blit(alt_sprite, (note.x, note.y), None)
            if is_sharp(note.nn):
                surface.blit(alt_sprite_sharp, (note.x-self.layout.semih*2, note.y), None)
        else:
            sprite = self.layout.sprites.note_images[self.note_length_images[note.length_name]]
            if y < t - self.layout.semih*2:
                i = int((t-y)/self.layout.semih)-3
                if i > 9:
                    i = 9
                if i < 0:
                    i = 0
                is_flip = 1
                has_lines = i
            elif y < t+h/2:
                is_flip = 1
            elif y <= t+h:
                is_flip = 0
            else:
                i = int((y-t-h)/self.layout.semih)-1
                if (i>9):
                    i = 9
                if i < 0:
                    i = 0
                is_flip = 0
                has_lines = i

            if has_lines > -1:
                surface.blit(self.layout.sprites.lines[has_lines][is_flip], (note.x, note.y), None)
            note.sprite = sprite[is_flip]
            surface.blit(sprite[is_flip], (note.x, note.y), None)

            if(is_sharp(note.nn)):
                surface.blit(self.layout.sprites.sharp, (note.x-self.layout.semih*2, note.y), None)



