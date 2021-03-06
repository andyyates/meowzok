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
debug_never_load_cache = False
print_debug_msgs = False
use_threading = True


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
        self.notes = [[] for i in range(0,2)]
        self.i = i
        self.loaded = False
        pass

_thread_handle = None
_stop_event = threading.Event()
def _tstop():
    print("STOP called")
    _stop_event.set()
def _tstopped():
    return _stop_event.is_set()

def print_note(n):
    if not print_debug_msgs:
        return
    print(n.type, n.time, n.length, " ".join([note_names[nn] for nn in n.nns]))

class Lilnote:
    def __init__(self, time, length, nns, t):
        self.time = time
        self.length = length
        self.nns = nns
        self.type = t

class LilyDots():
    def __init__(self, midifile):#game_name, midi_file_path, bars_per_page, notes, time_sig):
        #self.bars_per_page = bars_per_page
        #self.notes = notes
        #self.time_sig = time_sig
        #self.game_name = game_name
        #self.midi_file_path = midi_file_path
        self.scale = 1
        self.midifile = midifile
        self.pages = []
        self.left_pad = 0
        self.top_pad = 0
        self.info_csv_header = ["page_no","left","top","width","height"]
        self.thread_died = threading.Event()
        self.thread_error = ""

        #self.key_sigs = {-7:"ces",-6:"ges",-5:"des",-4:"aes",-3:"ees",-2:"bes",-1:"f",0:"c",1:"g",2:"d",3:"a",4:"e",5:"es",6:"fis",7:"cis" }

        self.split_notes_into_pages()
        #check for cache images
        if midifile.cacheable == False or not self.load_from_cache():
            print("load from cache failed..")
        #    exit()
            #build images 
            if use_threading:
                global _thread_handle
                if _thread_handle:
                    _tstop()
                    _thread_handle.join()
                    _stop_event.clear()

                
                _thread_handle = threading.Thread(target = self.__run_generate_images)
                _thread_handle.start()
                #self.generate_images()
                #scan images to find notes
            else:
                self.__run_generate_images()

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
        ts = self.midifile.time_sig
        bar_len = ts.get_bar_len()
        page_len = bar_len * style.bars_per_page
        min_gap = bar_len / 4
        
        if print_debug_msgs:
            print ("-"*100)
            print("arrange notes for score...")

        #split notes into lists for each clef, group into lilnote
        tnotes = [[],[]]
        for anl in self.midifile.active_notes:
            for i,tnl in enumerate(tnotes):
                cnl = [n for n in anl if n.clef == i]
                if len(cnl) > 0:
                    #cnl[0].inspect()
                    #print("bar ", cnl[0].time//bar_len)
                    n = Lilnote(ts.quantize_time(cnl[0].time), ts.quantize_length(cnl[0].length), [o.nn for o in cnl], "note")
                    tnl.append(n)

#
#        mln = 99999
#        for n in tnl:
#            mln = min(mln, n.length)
#            if n.length == 0:
#                print ("FOUNDiTHEiCULPRIT")
#
#                exit()
        #print("MIn length = ", mln)

        #insert bar checks
        for clef,notes in enumerate(tnotes):
            t = 0
            i = 0
            while True:
                t += bar_len
                bar_check = Lilnote(t, 0, [], "bar")
                while i<len(notes) and notes[i].time < t:
                    i += 1
                if i<len(notes):
                    notes.insert(i,bar_check)
                else:
                    notes.append(bar_check)
                    break

        #close up gaps and insert rests
        for clef,notes in enumerate(tnotes):
            i = 0
            while i < len(notes):
                n = notes[i]
                if(i>0):
                    prev = notes[i-1]
                else:
                    prev = Lilnote(0, 0, [], "bar")
                gap = n.time - (prev.time+prev.length)
                if gap > 0:
                    if prev.type != "bar" and gap < min_gap and ts.is_valid_length(n.time-prev.time):
                        prev.length = n.time-prev.time #extend previous note to avoid tiddly rests everywhere
                        if prev.length == 0:
                            print("EEEEEEEEEEEEEEEEEEEEk")
                            exit()
                        if print_debug_msgs:
                            print("close gap")
                    else:
                        t = prev.time+prev.length
                        if print_debug_msgs:
                            print("Filling a gap of ", gap)
                        while(gap > 0):
                            max_rest = ts.get_biggest_valid_length(gap)
                            if print_debug_msgs:
                                print("Best is ", max_rest)
                            if max_rest == 0:
                                if print_debug_msgs:
                                    print(">>>>>best is rubbish")
                                break
                            rest = Lilnote(t, max_rest, [], "rest") #insert a rest where the gap is big enough
                            t += max_rest
                            gap -= max_rest
                            if print_debug_msgs:
                                print("INSert rest")
                            notes.insert(i,rest)
                            i+=1
                elif gap < 0:
                    pl = prev.length
                    #trim previous note if they overlap in clef, polyphonic scores will display wrong, but at least playable
                    if n.time-prev.time > 0:
                        nl = ts.get_biggest_valid_length(n.time-prev.time)
                        prev.length = nl
                        remaining = pl-prev.length
                        if n.type == "bar" and remaining>=ts.smallest_length(): #if we trimmed the note because of a bar line, stick the rest of the note in here, and tie it
                            prev.type = "note-tie-l"
                            nl = ts.get_biggest_valid_length(remaining)
                            if nl== 0:
                                print("C EEEEEEEEEEEEEEEEEEEEk")
                                exit()
                            nu = Lilnote(n.time, nl, prev.nns, "note-tie-r") 
                        #backup to allow rests to be inserted
                        i-=1
                i += 1


        for cler,notes in enumerate(tnotes):
            for n in notes:
                if n.type != "bar" and n.length == 0:
                    print_note(n)
                    print ("FOUNDiTHEiCULPRIT")
                    exit()

        #split into pages
        end_time = max([n[-1].time+n[-1].length for n in tnotes])
        page_count = math.ceil(end_time / page_len)
        for i in range(0,page_count):
            p = Page(i)
            p.left_time = page_len*i
            p.right_time = p.left_time + page_len
            self.pages.append(p)
        for clef, notes in enumerate(tnotes):
            for n in notes:
                pgno = int(n.time/page_len)
                if pgno < len(self.pages):
                    self.pages[pgno].notes[clef].append(n)
                else:
                    if n.type != "bar":
                        print("OVERFLOW")
                        print_note(n)
                        print("OVERFLOW")

        for p in self.pages:
            p.nc = 0

        for nl in self.midifile.active_notes:
            for n in nl:
                qt = ts.quantize_time(n.time)
                n.page_no = int( qt / page_len) 
                if n.page_no < len(self.pages):
                    p = self.pages[n.page_no]
                    n.number_in_page = p.nc
                else:
                    print("Overflow note in page")
            p.nc += 1

        if print_debug_msgs:
            for clef, notes in enumerate(tnotes):
                print("Clef ", clef)
                for n in notes:
                    if n.length > 0:
                        print(n.type, n.nns, ts.get_length_name(n.length), n.time, n.length)
                    else:
                        print(n.type, n.nns, "0", n.time, n.length)

        if print_debug_msgs:
            print ("-"*100)


        #exit()

        

    def load_from_cache(self):
        #print("loading from cache", self.midifile.path, self.make_cache_file_name(0))
        out_of_date = False
        if not os.path.exists(self.midifile.path):
            print("", self.midifile.path, " not exist")
            return False

        if debug_never_load_cache == True:
            print("debug never load cache is true")
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
                    #print("path ", c, " not exist")
                    return False
                mtime = os.path.getmtime(c)
                if mtime < midi_file_mtime:
                    out_of_date = True

        if debug_always_load_cache == False:
            if out_of_date:
                print("debug always, but your cache out of date mate")
                return False


        for p in self.pages:
            p.png_path = self.make_cache_file_name(p.i)+".png"
            p.csv_path = self.make_cache_file_name(p.i)+".csv"

            p.img = pygame.image.load(p.png_path)

            with open(p.csv_path, newline='') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for lin,row in enumerate(csv_reader):
                    if len(row) != len(self.info_csv_header):
                        print("csv header does not match len=%d should be len=%d" % (len(row), len(self.info_csv_header)))
                    else:
                        if lin == 0:
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
        if page_i >= len(self.pages):
            return

        page = self.pages[page_i]
        while not page.loaded:
            if self.thread_died.isSet():
                print("Rendering thread died")
                return
            time.sleep(0.1)
            print(".", end='')
        dim = surface.get_rect()
        img = page.img
        img_dim = img.get_rect()
        scaled = self.pages[page_i].img

        #print("Dim ", dim)

        #if img_dim.width > dim.width:
        #    self.scale = dim.width / img_dim.width 
        #    w = int(img_dim.width*self.scale)
        #    h = int(img_dim.height*self.scale)
        #    scaled = pygame.transform.scale(scaled, (w,h))
        #    img_dim = scaled.get_rect()
        #else:
        #    self.scale = 1

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



    def draw_time_line(self, surface, offset, page_i, time, active_i):
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

        #check crash
        xpos = self.get_note_pos(active_i)
        if xpos == None:
            return 
        x = xpos.left*self.scale + offset.left + self.left_pad
        return x < l+xo

    def get_note_pos(self, active_note_i):
        if not len(self.midifile.active_notes) > active_note_i:
            return None
        nl = self.midifile.active_notes[active_note_i]
        n = nl[0]
        p = self.pages[n.page_no]
        if not p.loaded:
            return None
        #print("---get note pos---")
        #print(n.page_no, n.number_in_page)
        xpos = p.note_xs[n.number_in_page]
        #print(p.note_xs)
        return xpos


    def blob_note(self, surface, active_note_i, nn, color, offset):
        xpos = self.get_note_pos(active_note_i)
        if not xpos:
            return
        x = xpos.left*self.scale + offset.left + self.left_pad
        y = xpos.top*self.scale + offset.top + self.top_pad - 40
        #print(active_note_i, n.number_in_page)
        #pygame.draw.rect(surface, color, (x,y,xpos.width,xpos.height))
        w = xpos.width

        pygame.draw.polygon(surface, color, ((x,y),(x+w,y),(x+w/2,y+w),(x,y)))





    def generate_images(self):
        lily_template = r"""
        \version "2.19.82"
#(set! paper-alist (cons '("my size" . (cons (* 12 in) (* 3 in))) paper-alist))
        \include "lilypond-book-preamble.ly"

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
                \n\n\\new Staff { \\numericTimeSignature \\clef "%s" \\key %s \\time %d/%d  
                \\override Score.BarNumber.break-visibility = ##(#t #t #t)
                \\set Score.currentBarNumber = #%d
                \\override Voice.NoteHead.color = #(x11-color 'red)
                %s
                }
                """

        
                #\\override Voice.Stem.color = #(x11-color 'red)


        html_debug = ""

        
        ts = self.midifile.time_sig
        for p in self.pages:
            note_body = ["",""]
            if _tstopped():
                print("lilypond thread stoping")
                return
            print("gen ", self.midifile.name, " page ", p.i)

            has_notes = [False,False]
            for clef, notes in enumerate(p.notes):
                for n in notes:
                    #print_note(n)
                    if n.type == "bar":
                        note_body[clef] += " | "
                    elif n.type == "rest":
                        note_body[clef] += "r"+ts.get_length_name(n.length)
                    elif n.type.startswith("note"):
                        has_notes[clef] = True
                        if len(n.nns) > 1:
                            t = "<" + " ".join([note_names[nn] for nn in n.nns]) + ">" + ts.get_length_name(n.length) 
                        else:
                            t = note_names[n.nns[0]] + ts.get_length_name(n.length)
                        if n.type.endswith("tie-l"):
                            t += "~"
                        note_body[clef] += t + " "


            
            
            
            ks = self.midifile.time_sig.key_sig.lower()
            if ks[-1] == "m":
                keysig = ks[:-1]+" \\minor"
            else:
                keysig = ks + " \\major"
            print("working keysig : ", keysig)
            #keysig = self.key_sigs[self.midifile.time_sig.key_sig_sharps]
            #if self.midifile.time_sig.key_sig_is_major:
            #    keysig += " \\major"
            #else:
            #    keysig += " \\minor"

            body = ""
            current_bar = p.i * style.bars_per_page+1
            if has_notes[0]:
                body += staff_template % ("treble", keysig, self.midifile.time_sig.numerator,self.midifile.time_sig.denominator, current_bar, note_body[0])
            if has_notes[1]:
                body +=staff_template % ("bass", keysig, self.midifile.time_sig.numerator,self.midifile.time_sig.denominator, current_bar, note_body[1])
            body = lily_template % (body) 

            opfn = self.make_cache_file_name(p.i)
            p.ly_name = os.path.basename(opfn)
            f = open(opfn+".ly", "w")
            f.write(body)
            f.close()

        


            dirname = os.path.dirname(self.make_cache_file_name(self.pages[0].i))
            FNULL = open(os.devnull, 'w')
            popencmd = [style.lilypond_path, '--png']
            popencmd.append(p.ly_name)
            if print_debug_msgs:
                process = subprocess.Popen(popencmd, cwd=dirname)
            else:
                process = subprocess.Popen(popencmd, cwd=dirname, stdout=FNULL, stderr=subprocess.PIPE)
            output, err = process.communicate()
            rc = process.returncode

            p.png_path = dirname + "/"+p.ly_name+".png"
            p.img = pygame.image.load(p.png_path)
            error = self.inspect_images(p.i)
            
            html_debug += "<br>pg %d<br>" % (p.i)
            html_debug += "<img src=" + p.png_path + "><br>"
            html_debug += error + "<br><br>"


        dirname = os.path.dirname(self.make_cache_file_name(0))
        f = open(dirname+"/index.html","w")
        f.write(html_debug)
        f.close()
        

    def make_cache_file_name(self, i):
        gn = re.sub("[^a-zA-Z0-9]","_",self.midifile.name)
        gn += "%d_%d" % (style.kbd_lowest_note, style.kbd_highest_note)
        fn = cache_path + gn + "/"
        if not os.path.exists(fn):
            os.makedirs(fn)
        fn += str(i).zfill(2)
        return fn


    def inspect_images(self, page_i):
        error = ""
        p = self.pages[page_i]
        dim = p.img.get_rect()

        step = 1
        max_notes_per_page = 64 * 4
        x_quantize = int(dim.w/max_notes_per_page)
            
        note_heads = []

        min_overlap = 10
        meldx = 4
        meldy = 4
        meld =3 

        def stash(x,y):
            head_rect  = pygame.Rect(x-1,y-1,meldx,meldy)
            alli = head_rect.collidelistall(note_heads)
            al = [note_heads[i] for i in alli]
            print("list is %d long - intersect with %d" % (len(note_heads), len(al)))
            for i in al:
                head_rect.union_ip(i)
                note_heads.remove(i)
            note_heads.append(head_rect)




                    


        #double check for other non colliders
        
#
#            i = x_rect.collidelist(note_xs)
#            if i==-1:
#                note_xs.append(x_rect)
#            else:
#                n = note_xs[i]
#                n.union_ip(x_rect)




        color_freq = {}
        for x in range(0,dim.w,step):
            for y in range(0,dim.h,step):
                v = p.img.get_at((x,y))
                if v[0] != v[1]: # not black or white!
                    c = min(v) #colour em in with correct alpha
                    p.img.set_at((x,y), pygame.Color(c,c,c))
                    #print(v)
                #if not (v[0] < 100 and v[1] < 100 and v[2] > 100):
                    stash(x,y)




        note_xs = []
        for n in note_heads:
            xs = pygame.Rect(n.x,0,n.w,6)
            print("Adding ", xs, xs.x, xs.y)
            done = False
            for o in note_xs:
                if not ( o.x > xs.x+xs.w-min_overlap or o.x+o.w < xs.x+min_overlap ):
                    o.union_ip(xs)
                    print("Adding - Merged")
                    done = True
                    break
            if done == False:
                print("Adding - actually")
                note_xs.append(xs)




        #note_xs = [n for n in note_xs if n.width>meld*3]

        if print_debug_msgs:
            for n in note_heads:
                pygame.draw.rect(p.img, (0,random.randint(0,250), random.randint(0,250)), n, 1)
            x = 1
            for n in note_xs:
                x += 10
#            n.top+=x
                pygame.draw.rect(p.img, (0,000,200,100), n, 1)

        p.note_heads = note_heads
        p.note_xs = note_xs
        p.note_xs.sort(key=lambda x:x.x)
        pygame.image.save(p.img, p.png_path)

        with open(self.make_cache_file_name(page_i)+".csv",'w',newline='') as fd:
            writer = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(self.info_csv_header)
            for n in p.note_xs:
                row = [p.i, n.left, n.top, n.width, n.height]
                writer.writerow(row)

        #check each pages has the right number of note-group type events on it and send out a warning on the command line if not
        tots = []
        for clefnotes in p.notes:
            for n in clefnotes:
                if n.type.startswith("note"):
                    if n.time not in tots:
                        tots.append(n.time)

        if len(tots) != len(p.note_xs):
            er = "Error on page %d - there should be %d NOT %d" % (p.i, len(tots), len(p.note_xs))
            print(er)
            error += er

        p.loaded = True

        return error



