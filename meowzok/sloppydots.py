#!/usr/bin/python3
import pygame
import pygame.gfxdraw
from meowzok.util import *
import math
from meowzok.style import style
from meowzok.midifile import Note
import statistics


class Sprites:
    def __cut(self, x, y):
        rect = pygame.Rect((x*self.height,y*self.height,self.height,self.height))
        image = self.sheet.subsurface(rect)
        return image

    def blit(self, target, src, x, y, right=False):
        w,h = src.get_size()
        if right:
            target.blit(src, (x-w,y-h/2), None)
        else:
            target.blit(src, (x,y-h/2), None)


    def __init__(self, semih):
        self.width = self.height = semih * 18
        self.sheet = load_image("meowzok-sprites.png")
        w,h = self.sheet.get_size()
        self.sheet = pygame.transform.scale(self.sheet, (self.height*16, self.height*3))
        self.lines = []
        for i in range(9,-1,-1):
            image = self.__cut(i,0)
            self.lines.append([ image , pygame.transform.rotate(image,180) ])
        self.life = self.__cut(0,2)
        self.star = self.__cut(1,2)
        self.splat = self.__cut(2,2)
        self.splat_sharp = self.__cut(3,2)
        self.splat_blue = self.__cut(4,2)

        s = load_image("note-head-open.png")
        s = pygame.transform.scale(s, (int(semih*1.5),semih*2))
        self.note_head_open = s
        self.note_head_width = int(semih*1.5)

        s = load_image("note-head-closed.png")
        s = pygame.transform.scale(s, (int(semih*1.5),semih*2))
        self.note_head_closed = s

        s = load_image("sharp.png")
        self.sharp = pygame.transform.scale(s, (semih*4,semih*4))

        s = load_image("flat.png")
        self.flat = pygame.transform.scale(s, (semih*4,semih*4))

        s = load_image("natural.png")
        self.natural = pygame.transform.scale(s, (semih*4,semih*4))


        s = load_image("bass.png")
        self.bass_clef = pygame.transform.scale(s, (semih*5,semih*6))

        s = load_image("treb.png")
        self.treble_clef = pygame.transform.scale(s, (semih*5,semih*13))






        


class SloppyDots():
    def __init__(self, midifile):
        #game_name, midi_file_path, bars_per_page, notes, time_sig, size):
        self.w, self.h = 0,0
        self.resize(100,100)
        self.midifile = midifile

        self.key_signatures = [
            [["C","Am"],[],False],
            [["G","Em"],["F"],False],
            [["D","Bm"],["F","C"],False],
            [["A","F#m"],["F","C","G"],False],
            [["E","C#m"],["F","C","G","D"],False],
            [["B","G#m"],["F","C","G","D","A"],False],
            [["F#","D#m"],["F","C","G","D","A","E"],False],
            [["C#","A#m"],["F","C","G","D","A","E","B"],False],
            [["F","Dm"],["B"],True],
            [["Bb","Gm"],["B","E"],True],
            [["Eb","Cm"],["B","E","A"],True],
            [["Ab","Fm"],["B","E","A","D"],True],
            [["Db","Bbm"],["B","E","A","D","G"],True],
            [["Gb","Ebm"],["B","E","A","D","G","C"],True],
            [["Cb","Abm"],["B","E","A","D","G","C","F"],True]
            ]

        
        ks = [x[1:] for x in self.key_signatures if midifile.time_sig.key_sig in x[0]]
        if len(ks) == 0:
            print( "Can't find key sig ", midifile.time_sig.key_sig)
            self.keysig = []
            self.keysig_is_flat = 0
        else:
            self.keysig = ks[0][0]
            self.keysig_is_flat = ks[0][1]
            print("Keysig ", self.keysig, self.keysig_is_flat)

        self.accidentals = [[],[]]
        self.naturals = [[],[]]
        self.keysig_is_flat = 0


    def get_accidental(self, nn, clef):
        note_name = "CDEFGAB"[self.get_note_row(nn) % 7]
        #print("Get note ", nn, note_name, is_black(nn), self.keysig)
        c = set(self.keysig + self.accidentals[clef]).difference(self.naturals[clef])
        if is_black(nn):
            if note_name in self.naturals[clef]:
                self.naturals[clef].remove(note_name)
            elif note_name not in c:
                self.accidentals[clef].append(note_name)
            else:
                return ""
            return ['sharp','flat'][self.keysig_is_flat]
        else:
            if note_name in c:
                self.naturals[clef].append(note_name)
                return "natural"
            return ""
        return ""

    def clear_accidental(self):
        self.accidentals = [[],[]]
        self.naturals = [[],[]]


    def resize(self, w, h):
        if self.w == w and self.h == h:
            return
        self.w = w
        self.h = h
        self.rows = 50
        self.sh = int(h / self.rows)
        self.sprites = Sprites(self.sh)
        fs = int(h/30)
        self.font = pygame.font.SysFont(style.fonts[0], fs)



    class Clef:
        def __init__(self, middle_row, sh):
            #row zero is the bottom line of the cleff (so G or E)
            self.low = 1270
            self.hi = 0
            self.middle_y = 0
            self.middle_row = middle_row
            self.sh = sh

        def r2y(self, r):
            return (self.middle_row - r) * self.sh + self.middle_y

    #def draw(self, surface, active_i=None, notes=[], time_sig=None, time=None):
    def draw_music(self, surface, page_i):
        print("DRAW MUSIC", page_i)
        self.dim = dim = surface.get_rect()
        self.resize(dim.width, dim.height)
        surface.fill(style.stave_bg) #(1,200,2))
        bar_len_ticks = self.midifile.time_sig.get_bar_len()
        left_pad = self.sprites.width
        time_to_px = (self.w - left_pad) / (bar_len_ticks*style.bars_per_page)
        left_bar = page_i * style.bars_per_page
        left_time = left_bar * bar_len_ticks
        right_time = left_time + (style.bars_per_page * bar_len_ticks)

        display_notes = []
        for nl in self.midifile.active_notes:
            for n in nl:
                if n.time >= left_time - 50 and n.time < right_time:
                    display_notes.append(nl)
                    break
        
        #min max by clef
        self.clefs = [self.Clef(41,self.sh), self.Clef(29,self.sh)]
        for nl in display_notes:
            for n in nl:
                self.clefs[n.clef].low = min(self.clefs[n.clef].low, self.get_note_row(n.nn))
                self.clefs[n.clef].hi = max(self.clefs[n.clef].hi, self.get_note_row(n.nn))
        self.clefs[0].middle_y = int(self.h * 1/4)
        self.clefs[1].middle_y = int(self.h * 3/4)

        #bass = 25,33
        #treb = 35,43
        self.clefs[0].top_row = 46
        self.clefs[0].bottom_row = 37
        self.clefs[1].top_row = 34
        self.clefs[1].bottom_row = 25

        c = self.clefs[0]
        for r in range(c.bottom_row,c.top_row+1,2):
            pygame.draw.rect(surface, style.stave_lines, (0, self.clefs[0].r2y(r), self.w, 2))
        surface.blit(self.sprites.treble_clef, (self.sh,self.clefs[0].r2y(46)), None)

        c = self.clefs[1]
        for r in range(c.bottom_row,c.top_row+1,2):
            pygame.draw.rect(surface, style.stave_lines, (0, self.clefs[1].r2y(r), self.w, 2))
        surface.blit(self.sprites.bass_clef, (self.sh,self.clefs[1].r2y(32)), None)

        #draw key sig
        k = 7
        for i in range(0,7):
            if 'CDEFGAB'[i] in self.keysig:
                for j in range(0,2):
                    c = self.clefs[j]
                    row = (c.top_row // 7)*7 + i
                    if self.keysig_is_flat:
                        self.sprites.blit(surface, self.sprites.flat, self.sh*k, c.r2y(row))
                    else:
                        self.sprites.blit(surface, self.sprites.sharp, self.sh*k, c.r2y(row))
                    k += 1




        #draw bar lines & numbers
        for i in range(left_time, right_time+1, bar_len_ticks):
            bar_no = int(i/bar_len_ticks)+1
            l = (i-left_time) * time_to_px + left_pad - self.sh*2
            if i < right_time:
                text = self.font.render(str(bar_no), 1, (10, 10, 10))
                textpos = text.get_rect()
                textpos.left = l
                textpos.bottom= self.clefs[0].r2y(43)
                surface.blit(text, textpos)
            pygame.draw.rect(surface, style.stave_fg, (l, self.clefs[0].r2y(45), 2, self.sh*8))
            pygame.draw.rect(surface, style.stave_fg, (l, self.clefs[1].r2y(33), 2, self.sh*8))



 



        last_time = -1
        for nl in display_notes:
            #nudge heads that overlap
            for clef in [0,1]:
                prev_row = None
                for n in reversed(nl):
                    if n.clef == clef:
                        self.__set_note_y(n)
                        if prev_row != None:
                            n.nudge = abs(prev_row - n.row) < 2
                        else:
                            n.nudge = 0
                        prev_row = n.row

        #group notes for beaming
        beams = [[[]],[[]]]
        if self.midifile.time_sig.numerator % 3 == 0:
            half_bar_len_ticks = bar_len_ticks//3
        else:
            half_bar_len_ticks = bar_len_ticks//2
        for nl in display_notes:
            for n in nl:
                if n.time < left_time - 50 or n.time > right_time:
                    continue
                pg = beams[n.clef][-1]
                if n.time in [n.time for n in pg]:
                    pg.append(n)
                    continue

                #start a new group when
                if len(pg)>0:
                    #more than 4 things in a group
                    if len(set([n.time for n in pg]))>3:
                        pg = []
                        beams[n.clef].append(pg)
                    else: 
                        ln = pg[-1]
                        #on a bar or half bar
                        if ln.time // half_bar_len_ticks != n.time // half_bar_len_ticks:
                            pg = []
                            beams[n.clef].append(pg)
                        #when an unbeamer appears
                        elif (n.beamy == 0 or ln.beamy == 0) and ln.time != n.time:
                            pg = []
                            beams[n.clef].append(pg)
                        #when previous note is above n ticks prior
                        elif n.time - ln.time > bar_len_ticks/4:
                            pg = []
                            beams[n.clef].append(pg)

#                if n.beamy == 0:
#w                    continue
                pg.append(n)


        for grp in beams[0]+beams[1]:
            if len(grp) == 0:
                continue
            print(grp[0].clef, len(grp), " ".join([n.length_name for n in grp]))
            avgnn = statistics.mean([n.nn for n in grp])
            stickup = (grp[0].clef == 0 and avgnn < 70 ) or (grp[0].clef == 1 and avgnn < 49)

            #draw note heads
            for n in grp:
                print(n.nn, n.clef)
                if n.time >= left_time - 50 and n.time < right_time:
                    n.x = (n.time - left_time) * time_to_px + left_pad 
                    if last_time // bar_len_ticks != n.time // bar_len_ticks:
                        self.clear_accidental()
                    last_time = n.time
                    self.__draw_note(n, surface, stickup)




            if len(set([n.time for n in grp])) == 1:
                if stickup :
                    avgy = min([n.y for n in grp])
                else:
                    avgy = max([n.y for n in grp])
            else:
                avgy = statistics.mean([n.y for n in grp])

            stemlen = self.sh*6
            tw = self.sh//2
            #draw tails first
            if len(set([n.time for n in grp])) == 1:
                #just a single one
                d = self.sh*2
                for l in range(0,grp[0].beamy):
                    if stickup:
                        pygame.draw.rect(surface, style.stave_fg, (grp[0].x+self.sprites.note_head_width-2,avgy-stemlen+self.sh*l,d, tw))
                    else:
                        pygame.draw.rect(surface, style.stave_fg, (grp[0].x,avgy+stemlen-self.sh*l,d, tw))
            else:
                #an actual group
                for i,n in enumerate(grp[:-1]):
                    d = int((grp[i+1].time - n.time ) * time_to_px + 2)
                    for l in range(0,n.beamy):
                        if stickup:
                            pygame.draw.rect(surface, style.stave_fg, (n.x+self.sprites.note_head_width-2,avgy-stemlen+self.sh*l,d, tw))
                        else:
                            pygame.draw.rect(surface, style.stave_fg, (n.x,avgy+stemlen-self.sh*l,d, tw))
            #draw stems
            for n in grp:
                if stickup == 1:
                    h = avgy-stemlen-n.y
                    pygame.draw.rect(surface, style.stave_fg, (n.x+self.sprites.note_head_width-2,n.y,2,h))
                else:
                    h = avgy+stemlen-n.y
                    pygame.draw.rect(surface, style.stave_fg, (n.x,n.y,2,h))



    def __draw_note(self, note, surface, stickup):
        note.x = x = int(note.x)
        note.y = y = int(note.y) 
        color = (0,0,0)
        note.length_name = n = self.midifile.time_sig.get_length_name(note.length)
        dotted = n[-1] == "."
        c = self.clefs[note.clef]

        #draw dash above and below staves
        if note.row > c.top_row:
            for r in range(c.top_row+1, note.row+1, 2):
                pygame.draw.rect(surface, style.stave_fg, (note.x-self.sh*0.25, c.r2y(r), self.sh*2, 2))
        elif note.row < c.bottom_row:
            for r in range(c.bottom_row-2, note.row-1, -2):
                pygame.draw.rect(surface, style.stave_fg, (note.x-self.sh*0.25, c.r2y(r), self.sh*2, 2))

        #draw note head
        if dotted:
            n = n[:-1]
            #todo - blit the dot
        if note.nudge :
            if stickup:
                x += self.sprites.note_head_width-2
            else:
                x -= self.sprites.note_head_width-2
        if n== "1":
            self.sprites.blit(surface, self.sprites.note_head_open, x, y)
            note.beamy = -1
        elif n== "2":
            self.sprites.blit(surface, self.sprites.note_head_open, x, y)
            note.beamy = 0
        elif n== "4":
            self.sprites.blit(surface, self.sprites.note_head_closed, x, y)
            note.beamy = 0
        elif n== "8":
            self.sprites.blit(surface, self.sprites.note_head_closed, x, y)
            note.beamy = 1
        elif n== "16":
            self.sprites.blit(surface, self.sprites.note_head_closed, x, y)
            note.beamy = 2
        elif n== "32":
            self.sprites.blit(surface, self.sprites.note_head_closed, x, y)
            note.beamy = 3
        elif n== "64":
            self.sprites.blit(surface, self.sprites.note_head_closed, x, y)
            note.beamy = 4

        


        accident = self.get_accidental(note.nn, note.clef)
        if accident == "sharp":
            self.sprites.blit(surface, self.sprites.sharp, x, y, right=True)
        elif accident == "flat":
            self.sprites.blit(surface, self.sprites.flat, x, y, right=True)
        elif accident == "natural":
            self.sprites.blit(surface, self.sprites.natural, x, y, right=True)


    

    def blob_note(self, surface, active_note_i, nn, offset):
        nl = self.midifile.active_notes[active_note_i] 

        if not nn:
            for note in nl:
                x = int(note.x) + offset.left
                y = offset.top
                w = 10
                pygame.draw.polygon(surface, style.blob_pointer, ((x,y),(x+w,y),(x+w/2,y+w),(x,y)))
                break
            return

        

        
        clefs = set([n.clef for n in nl])
        for clef in clefs:
            for note in nl:
                nn.clef = clef
                self.__set_note_y(nn)
                x = int(note.x) + offset.left - self.sh
                y = int(nn.y) + offset.top
                pygame.draw.circle(surface, style.blob_blob, (x,y), self.sh, 1)
                break




    def get_note_row(self, nn):
        octave = nn // 12
        nn %= 12
        #is there a one liner to do this?
        if self.keysig_is_flat:
            if nn < 1:
                row = 0
            elif nn < 3:
                row = 1
            elif nn < 5:
                row = 2
            elif nn == 5:
                row = 3
            elif nn < 8:
                row = 4
            elif nn < 10:
                row = 5
            else:
                row = 6
        else:
            if nn < 2:
                row = 0
            elif nn < 4:
                row = 1
            elif nn == 4:
                row = 2
            elif nn < 7:
                row = 3
            elif nn < 9:
                row = 4
            elif nn < 11:
                row = 5
            else:
                row = 6
        row += octave * 7

        return row



    def __set_note_y(self, note):
        note.row = self.get_note_row(note.nn)
        note.y = self.clefs[note.clef].r2y(note.row)





    def draw_time_line(self, surface, offset, page_i, time, active_i):
        xo = offset.x
        yo = offset.y
        bar_len_ticks = self.midifile.time_sig.get_bar_len()
        left_bar = page_i * style.bars_per_page
        left_time = left_bar * bar_len_ticks
        right_time = left_time + (style.bars_per_page * bar_len_ticks)
        if time < left_time or time > right_time:
            return
        left_pad = self.sprites.width
        time_to_px = (self.w - left_pad) / (bar_len_ticks*style.bars_per_page)
        l = (time - left_time) * time_to_px + left_pad
        pygame.draw.rect(surface, style.time_line, (l+xo, 0, 2, self.dim.height))


