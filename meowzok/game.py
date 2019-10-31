import random
import time
import csv   
import datetime
from meowzok.style import style
from meowzok.keyboard import Keyboard
from meowzok.util import *
from meowzok.midifile import *


class GameGlobs:
    def __init__(self):
        self.lives = 10
        self.time_inc = 15
        self.bars_per_page = 4

game_globs = GameGlobs()

class Score:
    def __init__(self):
        self.bpm = 0
        self.errors = 0
        self.played_notes = 0
        self.avaliable_notes = 0

    def printit(self):
        print("score ", self.bpm, self.errors, self.played_notes, self.grade())

    def __gt__(self, other): 
        return self.grade()>other.grade()

    def percent_correct(self):
        if self.played_notes < self.errors:
            return 0
        if self.played_notes == 0:
            return 100
        return int(((self.played_notes - self.errors) / self.played_notes)*100)

    def percent_played(self):
        if self.avaliable_notes == 0:
            return 0
        return int(((self.played_notes/self.avaliable_notes))*100)

    def grade(self):
        return self.bpm * self.percent_correct() * self.percent_played() / 10000




class Player:
    def __init__(self):
        self.total_score = 0
        self.lives = game_globs.lives
        self.level = 0
        self.score = Score()

    def reset_for_level(self):
        self.lives = game_globs.lives
        self.score = Score()

class Game:
    def __init__(self,levels):
        self.__active_notes = []
        self.done_notes = []
        self.levels = levels
        self.player = Player()
        self.__setup_level()
        self.__rebuild_dots()
        self.dead_count = 0
        self.last_drawn_level = -1
        self.last_drawn_page = -1
        self.page_i = 0
        self.notes_down = None
        self.keyboard = Keyboard()
        self.load_high_score()

    def write_high_score_file(self):
        with open(high_scores_filename(),'a') as fd:
            writer = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            row = []
            row.append(self.levels[self.player.level].name)
            row.append(datetime.datetime.now().isoformat())
            row.append(self.player.score.bpm)
            row.append(self.player.score.errors)
            row.append(self.player.score.played_notes)
            row.append(self.player.score.avaliable_notes)
            writer.writerow(row)

    def load_high_score(self):
        lvlname = self.levels[self.player.level].name
        self.high_score = Score()
        if os.path.exists(high_scores_filename()):
            with open(high_scores_filename(), 'r') as fd:
                csv_reader = csv.reader(fd, delimiter=',')
                for row in csv_reader:
                    if len(row) == 6:
                        if row[0] == lvlname:
                            score = Score()
                            try:
                                score.bpm = float(row[2])
                            except:
                                print("Error loading bpm ", row[2])
                            try:
                                score.errors = int(row[3])
                            except:
                                print("Error loading error count ", row[3])
                            try:
                                score.played_notes = int(row[4])
                            except:
                                print("Error loading played_notes count ", row[3])
                            try:
                                score.avaliable_notes = int(row[5])
                            except:
                                print("Error loading avaliable_notes count ", row[3])

                            print("loaded score, check its best")
                            score.printit()
                            self.high_score.printit()
                            self.high_score = max(self.high_score, score)

    

    def retry_level(self):
        self.player.reset_for_level()
        self.__setup_level()

    def next_level(self):
        self.player.reset_for_level()
        if len(self.levels) > self.player.level+1:
            self.player.level += 1
            self.__setup_level()
            self.__rebuild_dots()
            return True
        else:
            return False

    def __setup_level(self):
        self.__active_notes = self.levels[self.player.level].notes
        self.time_sig = self.levels[self.player.level].time_sig
        self.player.score.avaliable_notes = 0
        for nl in self.__active_notes:
            for n in nl:
                n.fail = -1
                self.player.score.avaliable_notes += 1
        self.active_i = 0
        self.win = 0
        self.alive = True
        self.__time = -1000
        self.__prev_error_note = -1
        self.timer_first_note_down = -1
        self.timer_last_note_down = -1
        self.last_drawn_level = -1
        self.last_drawn_page = -1
        self.page_i = 0
        

    def __rebuild_dots(self):
        lvl = self.levels[self.player.level]
        w,h = style.screensize
        self.stave_position = pygame.Rect(0,int(h/4),w,int(h/2))
        self.dot_drawer = game_globs.dot_class(game_name = lvl.name, midi_file_path=lvl.midi_file_path, bars_per_page = game_globs.bars_per_page, notes=lvl.notes, time_sig=lvl.time_sig, size=self.stave_position)
        self.dot_surface = pygame.Surface((self.stave_position.w,self.stave_position.h))
        self.dot_surface.convert()



    def pop_active(self):
        r = self.__active_notes[self.active_i]
        self.active_i += 1
        return r

    def next_active_note(self):
        if self.active_i >= len(self.__active_notes):
            return None
        r = self.__active_notes[self.active_i]
        self.keyboard.right_keys = []
        for n in r:
            self.keyboard.right_keys.append(n.nn)
        return r



    def draw(self, surface):

        if self.last_drawn_level != self.player.level or self.last_drawn_page != self.page_i:
            self.notes_down = None
            self.dot_drawer.draw_music(self.dot_surface, self.page_i)
        self.last_drawn_level = self.player.level
        self.last_drawn_page = self.page_i

        surface.fill(style.main_bg)
        dim = surface.get_rect()
        surface.blit(self.dot_surface, (self.stave_position))
        
        isbad = False
        self.dot_drawer.blob_note(surface, self.active_i, None, (50,50,50), self.stave_position)
        if self.notes_down:
            acti, notes = self.notes_down
            for n in notes:
                if hasattr(n,'bad') and n.bad:
                    isbad = True
                    self.dot_drawer.blob_note(surface, acti, n, (200,0,0), offset=self.stave_position)
                else:
                    self.dot_drawer.blob_note(surface, acti, n, (0,200,0), offset=self.stave_position)
                    self.notes_down = None

        self.dot_drawer.draw_time_line(surface, self.stave_position, self.page_i, self.__time)

        if self.alive:
            title = style.font.render(self.levels[self.player.level].name, 1, style.title_fg)
        else:
            if self.win:
                title = style.font.render(self.levels[self.player.level].name + " COMPLETE!", 1, style.title_fg)
            else:
                title = style.font.render("GAME OVER", 1, style.title_fg)
        textpos = title.get_rect()
        textpos.left = textpos.height
        textpos.top = 0
        surface.blit(title, textpos)

        self.menu_items_rects = []
        msg = "\u2190"
        text = style.font.render(msg, 2, (0,0,0))
        cp = text.get_rect()
        cp.left = 0
        cp.top = 0
        surface.blit(text, cp)
        self.menu_items_rects.append([cp, "goto_main"])





        msg = "HI bpm:%3.2f  bum notes:%d  played:%d%%" % (self.high_score.bpm, self.high_score.errors, self.high_score.percent_played())
        text = style.font.render(msg, 1, style.bpm)
        textpos = text.get_rect()
        textpos.right = dim.width
        textpos.top = 0
        surface.blit(text, textpos)


        pad = int(dim.w / 10)
        
        h = textpos.height*2
        if style.show_helper_keyboard:# and ( style.speed == 0 or isbad ):
            y = dim.height-h
            self.keyboard.draw(surface, pygame.Rect(0, y, dim.width,h))
        else:
            y = dim.height

        msg = "bpm:%3.2f  bum notes:%d  played:%d%%" % (self.player.score.bpm, self.player.score.errors, self.player.score.percent_played())
        text = style.font.render(msg, 1, style.bpm)
        textpos = text.get_rect()
        textpos.right = dim.width
        textpos.bottom = y
        surface.blit(text, textpos)

        msg = "\u2665"*self.player.lives
        text = style.font.render(msg, 1, style.bpm)
        textpos = text.get_rect()
        textpos.left = 0
        textpos.bottom = y
        surface.blit(text, textpos)







    def advance(self):
        rv = None

        if self.alive :
            self.__time += game_globs.time_inc * style.speed / 2
            if self.next_active_note() == None:
                self.timer_last_note_down = pygame.time.get_ticks()
                self.win = 1
                self.alive = False
                return self.return_end_of_level()

            if self.next_active_note()[0].time < self.__time:
                print("die", self.__time)
                #if self.never_die == False:
                self.win = 0
                self.alive = False


        else:
            self.dead_count += 1
            if self.dead_count > 60:
                self.dead_count = 0
                return self.return_end_of_level()



    def return_end_of_level(self):
        if self.win == 1:
            return "LevelComplete"
        else:
            return "LevelFail"


    def key_down(self, key):
        if key == pygame.K_LEFT:
            return "goto_main"
        else:
            return key

    def mouse_down(self, pos):
        items = [x for x in self.menu_items_rects if x[0].contains(pos)]
        if len(items) > 0:
            return items[0][1]

    def note_down(self, nn, notes_down):
        if self.__prev_error_note in notes_down:
            ignore_error = 1
        else:
            self.__prev_error_note = -1
            ignore_error = 0

        if self.alive == False:
            return self.return_end_of_level()

        if self.timer_first_note_down == -1:
            self.timer_first_note_down = pygame.time.get_ticks()

        self.keyboard.wrong_keys = notes_down

        rv = 0
        if self.next_active_note():
            notes_scripted = [o.nn for o in self.next_active_note()]

            if all (n in notes_scripted for n in notes_down):
                rv = self.next_active_note()
                if all (n in notes_down for n in notes_scripted):
                    self.notes_down = (self.active_i, rv)
                    self.pop_active()
                    for n in rv:
                        if n.fail == -1:
                            n.fail = 0
                        n.bad = 0
                        self.player.score.played_notes += 1
                    total_ticks = pygame.time.get_ticks() - self.timer_first_note_down
                    total_beats = rv[0].time / self.time_sig.ticks_per_beat * (4 / self.time_sig.denominator)
                    if total_ticks > 0:
                        self.player.score.bpm = total_beats / total_ticks * 60000

                    nl = self.next_active_note()
                    if nl:
                        quantizer = int(self.time_sig.ticks_per_beat / 32)
                        time = round(nl[0].time/quantizer,0)*quantizer
                        if time >= (self.page_i+1)*self.time_sig.get_bar_len()*game_globs.bars_per_page:
                            self.page_i += 1

                    return rv
                else:
                    return 1
            elif ignore_error == False:
                self.__prev_error_note = nn
                nl = self.next_active_note()

                for n in nl:
                    if n.fail == -1:
                        n.fail = 1
                    else:
                        n.fail += 1

                t = []
                for n in notes_down:
                    blb = Note()
                    blb.nn = n
                    near = min(self.next_active_note(), key=lambda x: abs(n-x.nn))
                    blb.clef = near.clef
                    blb.x = near.x
                    blb.bad = 1
                    t.append(blb)
                    self.player.score.errors += 1
                self.notes_down = (self.active_i, t)



                if style.speed != 0:
                    self.player.lives -= 1
                if self.player.lives < 0 :
                    self.win = 0
                    self.alive = 0

                return 0
        return 1

            


class Level:
    def __init__(self, notes, level_name, time_sig, midi_file_path=os.path.join(main_dir, "MKGame.py")):
        self.notes = notes
        self.name = level_name
        self.time_sig = time_sig
        self.midi_file_path = midi_file_path
        time = 0
        for n in self.notes:
            if hasattr(n[0],'time'):
                time = n[0].time
            else:
                for ni in n:
                    ni.time = time
                time += n[0].length



def load_midi_file_game(filename, difficulty):
    print("Load midi file game", filename, difficulty)
    levels = []
    fn = os.path.basename(filename).replace(".mid","")
    path = os.path.join(style.midi_file_path+"/", filename)
    mf = MKMidiFile(path)
    random.seed(time.time())

    default_len = mf.time_sig.ticks_per_beat
    default_len_name = mf.time_sig.get_length_name(default_len)
    
    notes_flat = []
    for nl in mf.notes:
        for n in nl:
            notes_flat.append(n)
    if difficulty == 1:
        parts = []
        for c in range(0,2):
            scale_notes = list(set( [ n.nn for n in notes_flat if n.clef == c ] ))
            scale_notes.sort()
            for i in range(3,6):
                parts += [scale_notes[j:j+i] for j in range(0,len(scale_notes),i)]
            parts.sort(key = lambda x:i*1000 + sum([abs([71,50][c] - y) for y in x]))
            for level_no, p in enumerate(parts):
                if len(p) < 3:
                    continue
                scale = p.copy() 
                reverse =  p.copy()
                reverse.reverse()
                scale += reverse[1:] + scale.copy()[1:] + reverse.copy()[1:]
                for i in range(0,4):
                    random.shuffle(p)
                    scale += p.copy()
                levels.append(Level( [[Note(nn=n, clef=c, time=i*480, length_ticks=default_len, length_name=default_len_name)] for i,n in enumerate(scale)], "%s - Easy game %d" %( fn, level_no), mf.time_sig ))

    if difficulty <= 2:
        parts = []
        for c in range(0,2):
            scale_notes = list(set( [ n.nn for n in notes_flat if n.clef == c ] ))
            scale_notes.sort()
            p = scale_notes
            if len(p) < 3:
                continue
            scale = p.copy() 
            reverse = p[1:].copy()
            reverse.reverse()
            scale += reverse + scale.copy() + reverse.copy()
            for i in range(0,4):
                random.shuffle(p)
                scale += p.copy()
            levels.append(Level( [[Note(nn=n, clef=c, time=i*480, length_ticks=default_len, length_name=default_len_name)] for i,n in enumerate(scale)], "%s - Medium game - %s hand" %( fn, ["right","left"][c]), mf.time_sig ))

    if difficulty <= 4:
        parts = []
        #game 3 is right hand only
        if difficulty <= 3:
            rih = 0
        else:
            rih = 1
        for c in range(rih,2):
            notes = []
            for nl in mf.notes:
                grp = []
                for n in nl:
                    if n.clef == c:
                        grp.append(n)
                if len(grp)>0:
                    notes.append(grp)
            if len(notes) > 0:
                levels.append(Level(notes, "%s - %s hand" % (fn, ["right","left"][c]), mf.time_sig))
        
        

    uniq = []
    for nl in mf.notes:
        if not nl in uniq:
            uniq.append(nl)

    for dif in range(difficulty,8):
        notes = []
        t = 0
        loop_limit = 10000
        while len(notes) < 160 and loop_limit > 0:
            loop_limit -= 1
            if len(uniq) == 0:
                break
            nl = random.choice(uniq)
            if len(nl) == 0:
                continue
            mnl = []
            for j in range(1,4):
                n = random.choice(nl)
                if dif == 5:
                    if n.clef != 0:
                        continue
                elif dif == 6:
                    if n.clef != 1:
                        continue
                if not n.nn in [o.nn for o in mnl]:
                    n1 = Note()
                    n1.nn = n.nn
                    n1.clef = n.clef
                    n1.time = t
                    n1.length_ticks = default_len
                    n1.length_name = default_len_name
                    mnl.append(n1)
            if len(mnl)>0:
                notes.append(mnl)
                t += mf.time_sig.ticks_per_beat
        levels.append(Level(notes, "%s - random notes" % (fn), mf.time_sig))

    
    for l in levels:
        l.midi_file_path = path + "_no_cache"


    return levels









def load_midi_file(filename):
    path = os.path.join(style.midi_file_path+"/", filename)
    mf = MKMidiFile(path)
    fn = os.path.basename(filename).replace(".mid","")
    levels = [Level(mf.notes, fn, mf.time_sig, path)]
    return levels



