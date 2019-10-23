#!/usr/bin/python3

from pathlib import Path
import csv
import math
import pygame
import random
import re
import subprocess
import threading 
import time
import traceback

from meowzok.style import style
from meowzok.util import *
from meowzok.midifile import Note

debug_always_load_cache = False
print_debug_msgs = False


note_names = []
has_sharp = [1,1,0,1,1,1,0]
i = 0
note_name_i = 0
octave_i = 0
octaves = [","*n for n in range(5,0,-1)] + ["'"*n for n in range(0,6)] 
while i < 128:
    note_names.append("cdefgab"[note_name_i]+octaves[octave_i])
    i += 1
    if has_sharp[note_name_i]:
        note_names.append("cdefgab"[note_name_i]+"is"+octaves[octave_i])
        i += 1
    note_name_i += 1
    if note_name_i == 7:
        note_name_i = 0
        octave_i += 1

cache_path = os.path.expanduser("~/.cache/meowzok/")
if not os.path.exists(cache_path):
    os.makedirs(cache_path)

class Page():
    def __init__(self,i):
        self.notes = []
        self.i = i
        self.loaded = False
        pass


class LilyDots():
    def __init__(self, midifile):#game_name, midi_file_path, bars_per_page, notes, time_sig):
        #self.bars_per_page = bars_per_page
        #self.notes = notes
        #self.time_sig = time_sig
        #self.game_name = game_name
        #self.midi_file_path = midi_file_path
        self.midifile = midifile
        self.pages = []
        self.left_pad = 0
        self.top_pad = 0
        self.info_csv_header = ["page_no","left","top","width","height"]
        self.thread_died = threading.Event()
        self.thread_error = ""

        self.key_sigs = {-7:"ces",-6:"ges",-5:"des",-4:"aes",-3:"ees",-2:"bes",-1:"f",0:"c",1:"g",2:"d",3:"a",4:"e",5:"es",6:"fis",7:"cis" }

        self.split_notes_into_pages()
        #check for cache images
        if not self.load_from_cache():
            print("load from cache failed..")
        #    exit()
            #build images 

            
            thread = threading.Thread(target = self.__run_generate_images)
            thread.start()
            #self.generate_images()
            #scan images to find notes

    def __run_generate_images(self):
        try:
            self.generate_images()
        except :
            #todo signal main thread that we died
            self.thread_died.set()
           # self.thread_error = traceback.print_exc()
            raise
            exit()

    def split_notes_into_pages(self):
        page_len = self.midifile.time_sig.get_bar_len()*style.bars_per_page
        left_time = 0
        right_time = page_len
        cpage = Page(0)
        cpage.left_time = left_time
        cpage.right_time = right_time
        for nl in self.midifile.active_notes:
            t = nl[0].time
            if t >= right_time:
                self.pages.append(cpage)
                left_time += page_len
                right_time += page_len
                cpage = Page(len(self.pages))
                cpage.left_time = left_time
                cpage.right_time = right_time
            cpage.notes.append(nl)
        if len(cpage.notes)>0:
            self.pages.append(cpage)
        for p in self.pages:
            for i,nl in enumerate(p.notes):
                for n in nl:
                    n.page_no = p.i
                    n.number_in_page = i


        #print("Found %d pages" % (len(self.pages)))
        

    def load_from_cache(self):
        print("loading from cache")
        out_of_date = False
        if not os.path.exists(self.midifile.path):
            print("", self.midifile.path, " not exist")
            return False

        midi_file_mtime = os.path.getmtime(self.midifile.path)

#        for src_dirs in [Path().absolute()]:
#            for f in os.listdir(src_dirs):
#                print("Check date on ", f)
#                if f.endswith(".py"):
#                    this_file_mtime = os.path.getmtime(f)
#                    midi_file_mtime = max(midi_file_mtime, this_file_mtime)

        for p in self.pages:
            p.png_path = self.make_cache_file_name(p.i)+".png"
            p.csv_path = self.make_cache_file_name(p.i)+".csv"
            for c in [p.png_path, p.csv_path]:
                if not os.path.exists(c):
                    return False
                mtime = os.path.getmtime(c)
                if mtime < midi_file_mtime:
                    out_of_date = True

        if debug_always_load_cache == False:
            if out_of_date:
                return False


        for p in self.pages:
            p.png_path = self.make_cache_file_name(p.i)+".png"
            p.csv_path = self.make_cache_file_name(p.i)+".csv"

            p.img = pygame.image.load(p.png_path)

            with open(p.csv_path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for lin,row in enumerate(csv_reader):
                    if lin == 0:
                        if len(row) != len(self.info_csv_header):
                            print("csv header does not match len=%d should be len=%d" % (len(row), len(self.info_csv_header)))
                            return False
                        for i,v in enumerate(self.info_csv_header):
                            if row[i] != v:
                                print("csv header does not match %d %s!=%s" % (i, row[i], v))
                                return False
                    else:
                        ints = []
                        for v in row:
                            try:
                                ints.append(int(v))
                            except:
                                print("Could not convert %s to an int (at load from cache row %d)" % (v, lin))
                        if ints[0] != p.i:
                            print("loaded csv from different page ? wtf")
                            return False
                        if not hasattr(p, 'note_xs'):
                            p.note_xs = []
                        p.note_xs.append(pygame.Rect(*ints[1:]))

            p.loaded = True
        print("Loaded from cache")

        return True




    def draw_music(self, surface, page_i):
        page = self.pages[page_i]
        while not page.loaded:
            if self.thread_died.isSet():
                print("Rendering thread died")
                return
            time.sleep(0.1)
            print("Waiting for images to load")
        dim = surface.get_rect()
        img = page.img
        img_dim = img.get_rect()
        scaled = self.pages[page_i].img

        if img_dim.width > dim.width:
            self.scale = dim.width / img_dim.width 
            w = int(img_dim.width*self.scale)
            h = int(img_dim.height*self.scale)
            scaled = pygame.transform.scale(scaled, (w,h))
            img_dim = scaled.get_rect()
        else:
            self.scale = 1

        self.left_pad = int((dim.width - img_dim.width)/2)
        self.top_pad = int((dim.height - img_dim.height)/2)

        surface.fill((255,255,255))
        surface.blit(scaled, (self.left_pad,self.top_pad))


        if print_debug_msgs:
            for r in self.pages[page_i].note_xs:
                #color = [random.randint(0,155) for x in range(0,3)]
                color = (200,200,200)
                pygame.draw.rect(surface, color, (r.left+self.left_pad, r.top+self.top_pad, 2, r.height), 1)



        #copy current frame to rect
        #draw time line on
        #draw notes down on
#        for n in self.pages[page_i].note_xs:
 #           pygame.draw.circle(surface, (244,0,230), (n.centerx+self.left_pad, n.centery+self.top_pad), 4)



    def draw_time_line(self, surface, offset, page_i, time):
        xo = offset.x
        yo = offset.y
        bar_len_ticks = self.midifile.time_sig.get_bar_len()
        left_bar = page_i * style.bars_per_page
        left_time = left_bar * bar_len_ticks
        right_time = left_time + (style.bars_per_page * bar_len_ticks)
        if (time > 0 and time < left_time) or time > right_time:
            return
        time_to_px = (surface.get_rect().width - self.left_pad*2) / (bar_len_ticks*style.bars_per_page) * self.scale
        l = (time - left_time) * time_to_px + self.left_pad + 120
        pygame.draw.rect(surface, style.time_line, (l+xo, offset.y, 2, offset.height))


    def blob_note(self, surface, active_note_i, nn, color, offset):
        if not len(self.midifile.active_notes) > active_note_i:
            return 
        nl = self.midifile.active_notes[active_note_i]
        n = nl[0]
        p = self.pages[n.page_no]
        if not p.loaded:
            return
        xpos = p.note_xs[n.number_in_page]
        x = xpos.left*self.scale + offset.left + self.left_pad
        y = xpos.top*self.scale + offset.top + self.top_pad
        #print(active_note_i, n.number_in_page)
        pygame.draw.rect(surface, color, (x,y,xpos.width,xpos.height))





    def generate_images(self):
        lily_template = r"""
        \version "2.19.82"
#(set! paper-alist (cons '("my size" . (cons (* 12 in) (* 3 in))) paper-alist))

        \paper{
          #(set-paper-size "my size")
          indent=0\mm
          line-width=120000\mm
          oddFooterMarkup=##f
          oddHeaderMarkup=##f
          bookTitleMarkup = ##f
          scoreTitleMarkup = ##f
          top-margin = 10
        }


         \layout {
            \context {
              \Score
              proportionalNotationDuration = #(ly:make-moment 1/16)
            }
          }

        \fixed c' {
        <<
        %s
        >>
        }
        """ 

        staff_template = """
                \n\n\\new Staff { \\clef "%s" \\key %s \\time %d/%d 
                \\override Voice.NoteHead.color = #(x11-color 'red)
                \\override Voice.Stem.color = #(x11-color 'red)
                %s
                }
                """

        


        def print_times(*argv):  
            if not print_debug_msgs:
                return
            op= []
            op.append(argv[0])
            for arg in argv[1:]:
                op.append(arg)
                op.append(arg/480)
            print(op)

        for p in self.pages:
            print("Page ", p.i)

            #insert bars as notes with zero length - bit hacky
            tmp_notes = p.notes.copy()
            print_times("Page %d" %(p.i), len(tmp_notes), p.left_time, p.right_time)


            for i in range(p.left_time, p.right_time+1, self.midifile.time_sig.get_bar_len()):
                if i == 0:
                    continue
                nl = []
                for j in range(0,2):
                    rest = Note()
                    rest.nn = -1
                    rest.time = i
                    rest.length_ticks = 0
                    rest.clef = j
                    nl.append(rest)
                tmp_notes.append(nl)
            #sort notes make sure bars breaks appear before notes
            tmp_notes.sort(key=lambda x:(x[0].time, x[0].length_ticks))

            note_body = ["",""]

            for clef in range(0,2):
                lily_time = p.left_time
                #print("clef ",clef)
                for nl in tmp_notes:
                    if nl[0].time < p.left_time:
                        print(nl, nl[0].time, p.left_time)
                        raise "Wtf?"
                        continue
                    tnl = [l for l in nl if l.clef == clef]
                    if len(tnl) == 0:
                        print_times("Skip empty notes")
                        continue
                    quantizer = int(self.midifile.time_sig.ticks_per_beat / 4)  
                    qtime = round(tnl[0].time/quantizer,0)*quantizer
                    if qtime >= p.right_time:
                        d = p.right_time - lily_time
                        if d>0:
                            rest_name = self.midifile.time_sig.get_length_name(d)
                            print_times ("eopr>", qtime, lily_time)
                            note_body[clef] += "r" + rest_name + " "
                        break
                    diff = qtime - lily_time
                    if diff > 0:
                        print_times ("rest>", qtime, lily_time)

                        ndiff = self.midifile.time_sig.quantize_length(diff)
                        if ndiff != diff:
                            print("Wierd stuff in diff time ..")
                        rest_name = self.midifile.time_sig.get_length_name(ndiff)
                        note_body[clef] += "r" + rest_name + " "
                        lily_time += ndiff
                    if tnl[0].length_ticks == 0:
                        print_times ("bar >", qtime, lily_time)
                        #bar break
                        note_body[clef] += " | "
                        #print("BAR")
                    elif len(tnl) > 1:
                        for l in tnl:
                            print_times ("note>", qtime, lily_time, l.length_ticks)
                        l = min(tnl, key=lambda x:x.length_ticks)
                        note_body[clef] += "<" + " ".join([note_names[n.nn] for n in tnl]) + ">" + l.length_name + " "
                        lily_time += l.length_ticks
                        qtime += l.length_ticks
                    elif len(tnl) == 1:
                        l = tnl[0]
                        print_times ("note>", qtime, lily_time, l.length_ticks)

                        note_body[clef] += note_names[tnl[0].nn] + l.length_name + " "
                        lily_time += l.length_ticks
                        qtime += l.length_ticks

                    #if lily_time != qtime:
                    #    print("LILY TIME OUT oF WhacK>", lily_time, qtime, "<")

            
            
            keysig = self.key_sigs[self.midifile.time_sig.key_sig_sharps]
            if self.midifile.time_sig.key_sig_is_major:
                keysig += " \\major"
            else:
                keysig += " \\minor"

            body = ""
            if note_body[0]!="":
                body += staff_template % ("treble", keysig, self.midifile.time_sig.numerator,self.midifile.time_sig.denominator, note_body[0])
            if note_body[1]!="":
                body +=staff_template % ("bass", keysig, self.midifile.time_sig.numerator,self.midifile.time_sig.denominator, note_body[1])
            body = lily_template % (body) 

            opfn = self.make_cache_file_name(p.i)
            f = open(opfn+".ly", "w")
            f.write(body)
            f.close()

            cmd = "lilypond --png -o " + opfn + " " + opfn + ".ly "
            process = os.popen(cmd)
            cmd_output = process.read()
            process.close()



            FNULL = open(os.devnull, 'w')
            process = subprocess.Popen(['lilypond', '--png', '-o', opfn, opfn+".ly"], stdout=FNULL, stderr=subprocess.PIPE)
            output, err = process.communicate()
            rc = process.returncode


            #print("-"*80)
            #print(output)
            #print(err)
            #print("-"*80)



            p.png_path = opfn+".png"
            p.img = pygame.image.load(p.png_path)



            #exit()
            self.inspect_images(p.i)



    def make_cache_file_name(self, i):
        gn = re.sub("[^a-zA-Z0-9]","_",self.midifile.name)
        fn = cache_path + gn + "/"
        if not os.path.exists(fn):
            os.makedirs(fn)
        fn += str(i).zfill(2)
        return fn


    def inspect_images(self, page_i):
        p = self.pages[page_i]
        dim = p.img.get_rect()

        step = 1
        max_notes_per_page = 64 * 4
        x_quantize = int(dim.w/max_notes_per_page)
            
        note_heads = []
        note_xs = []

        meld = 3

        def stash(x,y):
            head_rect  = pygame.Rect(x,y,meld,meld)
            x_rect  = pygame.Rect(x,0,meld,6)

            i = head_rect.collidelist(note_heads)
            if i==-1:
                note_heads.append(head_rect)
            else:
                n = note_heads[i]
                n.union_ip(head_rect)

            i = x_rect.collidelist(note_xs)
            if i==-1:
                note_xs.append(x_rect)
            else:
                n = note_xs[i]
                n.union_ip(x_rect)




        color_freq = {}
        for y in range(0,dim.h,step):
            last_found = 0
            for x in range(0,dim.w,step):
                v = p.img.get_at((x,y))
                if v[0] != v[1]:
                    #print(v)
                #if not (v[0] < 100 and v[1] < 100 and v[2] > 100):
                    p.img.set_at((x,y), pygame.Color(0,0,0))
                    stash(x,y)
        note_xs = [n for n in note_xs if n.width>meld*3]

        if print_debug_msgs:
            for n in note_heads:
                pygame.draw.rect(p.img, (0,200,200), n, 1)
            x = 1
            for n in note_xs:
                x += 10
#            n.top+=x
                pygame.draw.rect(p.img, (0,000,200,100), n, 1)

        p.note_heads = note_heads
        p.note_xs = note_xs
        p.note_xs.sort(key=lambda x:x.x)
        pygame.image.save(p.img, p.png_path)

        with open(self.make_cache_file_name(page_i)+".csv",'w') as fd:
            writer = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(self.info_csv_header)
            for n in p.note_xs:
                row = [p.i, n.left, n.top, n.width, n.height]
                writer.writerow(row)

        #check each pages has the right number of note-group type events on it and send out a warning on the command line if so
        if len(p.notes) != len(p.note_xs):
            print("Error on page %d - there should be %d NOT %d" % (p.i, len(p.notes), len(p.note_xs)))

        p.loaded = True




