import random
import time
import csv   
import datetime
import math
from meowzok.style import style
from meowzok.keyboard import Keyboard
from meowzok.util import *
from meowzok.midifile import *



class Score:
    def __init__(self):
        self.bpm = 0
        self.errors = 0
        self.played_notes = 0
        self.avaliable_notes = 0
        self.midifile = ""
        self.invalid = False
        self.game = ""

    def printit(self):
        print("score ", self.bpm, self.errors, self.played_notes, self.grade())

    def __gt__(self, other): 
        return self.grade()>other.grade()

    def percent_correct(self):
        if self.played_notes < self.errors:
            return 0
        if self.played_notes == 0:
            return 100
        if self.invalid:
            return 0
        return int(((self.played_notes - self.errors) / self.played_notes)*100)

    def percent_played(self):
        if self.avaliable_notes == 0:
            return 0
        if self.invalid:
            return 0
        return int(((self.played_notes/self.avaliable_notes))*100)

    def grade(self):
        if self.invalid:
            return 0
        return self.bpm * self.percent_correct() * math.pow(self.percent_played(),3) / math.pow(100, 4)


def load_score(row):
    score = Score()
    if len(row) == 0:
        return None
    score.midifile = row[0]
    try:
        score.date = datetime.datetime.fromisoformat(row[1])
    except:
        print("Error converting date ", row[1])
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
        print("Error loading played_notes count ", row[4])
    try:
        score.avaliable_notes = int(row[5])
    except:
        print("Error loading avaliable_notes count ", row[5])
    try:
        score.game = row[6]
    except:
        print("no game info")
    return score

#def load_high_scores_for_menu():
#    scores = {}
#    if os.path.exists(high_scores_filename()):
#        with open(high_scores_filename(), 'r') as fd:
#            csv_reader = csv.reader(fd, delimiter=',')
#            name = row[0]

     

def load_high_scores_for_game(path, gamename):
    print("loading high scores")
    scores = []
    fn = os.path.basename(path)
    if os.path.exists(high_scores_filename()):
        with open(high_scores_filename(), 'r', newline='') as fd:
            csv_reader = csv.reader(fd, delimiter=',')
            for row in csv_reader:
                if len(row) > 6:
                    if row[0] == fn and row[6] == gamename:
                        score = load_score(row)
                        if score:
                            scores.append(score)
                else:
                    print("loading scores for game, csv row too short")
    scores.sort()
    scores.reverse()
    return scores



def load_high_scores():
    scores = []
    if os.path.exists(high_scores_filename()):
        with open(high_scores_filename(), 'r', newline='') as fd:
            csv_reader = csv.reader(fd, delimiter=',')
            for row in csv_reader:
                score = load_score(row)
                if score:
                    scores.append(score)
    scores.sort()
    scores.reverse()
    return scores


class Player:
    def __init__(self):
        self.lives = style.lives
        self.score = Score()

class Game:
    def __init__(self, up, midifile, cacheable=True):
        self.eek = False
        midifile.cacheable = cacheable
        self.menu_up = up
        self.__active_notes = []
        self.done_notes = []
        self.midifile = midifile
        self.redrawme = True

        for nl in self.midifile.notes:
            for n in nl:
                while n.nn < style.kbd_lowest_note:
                    n.nn += 12
                while n.nn > style.kbd_highest_note:
                    n.nn -= 12
            
        self.player = Player()
        self.__setup_level()
        self.__rebuild_dots()
        self.dead_count = 0
        self.last_drawn_page = -1
        self.page_i = 0
        self.l_notes_down = []
        self.keyboard = Keyboard()
        self.high_scores = load_high_scores_for_game(self.midifile.path, type(self).__name__)
        if len(self.high_scores)>0:
            self.high_score = max(self.high_scores)
        else:
            self.high_score = Score()


    def write_high_score_file(self):
        if self.player.score.grade() == 0:
            return
        with open(high_scores_filename(),'a', newline='') as fd:
            writer = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            row = []
            row.append(os.path.basename(self.midifile.path))
            row.append(datetime.datetime.now().isoformat())
            row.append(self.player.score.bpm)
            row.append(self.player.score.errors)
            row.append(self.player.score.played_notes)
            row.append(self.player.score.avaliable_notes)
            row.append(type(self).__name__)
            writer.writerow(row)


    def __setup_level(self):
        self.__active_notes = self.midifile.active_notes
        self.player.score.avaliable_notes = 0
        for nl in self.__active_notes:
            for n in nl:
                n.fail = -1
        self.player.score.avaliable_notes = len(self.__active_notes)
        self.score_saved = False
        self.active_i = 0
        self.win = 0
        self.alive = True
        self.__time = -1000
        self.__prev_error_note = -1
        self.timer_first_note_down = -1
        self.timer_last_note_down = -1
        self.last_drawn_page = -1
        self.page_i = 0
        

    def resize(self):
        w,h = style.screensize
        self.stave_position = pygame.Rect(0,int(h/4),w,int(h/2))
        self.dot_surface = pygame.Surface((self.stave_position.w,self.stave_position.h))
        self.last_drawn_page = -1
        print("resize")
        self.redrawme = True

    def __rebuild_dots(self):
        self.resize()
        self.dot_drawer = style.dot_class(self.midifile)
        self.dot_surface.convert()
        self.last_drawn_page = -1


    def goto_page(self, time):
        page_size = self.midifile.time_sig.get_bar_len()*style.bars_per_page
        pno = int(time/page_size)
        if self.page_i != pno:
            self.page_i = pno
            print("goto page")
            self.redrawme = True

    def back_up_to_bar(self):
        if self.active_i < 0:
            self.active_i = 0
        t = self.next_active_note()[0].time
        t = int(t/self.midifile.time_sig.get_bar_len()) * self.midifile.time_sig.get_bar_len()
        while(self.active_i > 0 and self.__active_notes[self.active_i][0].time > t):
            self.active_i -= 1
        self.__time = t-self.midifile.time_sig.get_bar_len()
        self.goto_page(t)
        #self.active_i += 1
        print("backup")
        self.redrawme = True

    def fwd_a_bar(self):
        if self.active_i >= len(self.__active_notes):
            self.active_i = len(self.__active_notes)-1
        t = self.next_active_note()[0].time
        t = int(t/self.midifile.time_sig.get_bar_len()+1) * self.midifile.time_sig.get_bar_len()
        while(self.active_i < len(self.__active_notes)-1 and self.__active_notes[self.active_i][0].time < t):
            self.active_i += 1
            self.l_notes_down = []
        self.goto_page(t)
        print("fwd")
        self.redrawme = True



    def pop_active(self):
        r = self.__active_notes[self.active_i]
        self.active_i += 1
        self.l_notes_down = []
        print("pop act")
        self.redrawme = True
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
        #if self.eek:
        #    surface.fill(style.main_bg_eek)
        #else:

        #if self.redrawme == False:
        #    return
        self.redrawme = False

        surface.fill(style.main_bg)
        dim = surface.get_rect()

        if self.alive:
            if self.last_drawn_page != self.page_i:
                self.l_notes_down = []
                self.dot_drawer.draw_music(self.dot_surface, self.page_i)
            self.last_drawn_page = self.page_i

            surface.blit(self.dot_surface, (self.stave_position))
            
            self.dot_drawer.blob_note(surface, self.active_i, None, self.stave_position)
            if len(self.l_notes_down)>0:
                r = self.stave_position
                for acti, n in self.l_notes_down:
                    self.dot_drawer.blob_note(surface, acti, n, offset=r)

            if style.speed != 0:
                crash = self.dot_drawer.draw_time_line(surface, self.stave_position, self.page_i, self.__time, self.active_i)
                if crash:
                    self.alive = False

            title = style.font.render(self.midifile.name, 1, style.title_fg)
            textpos = title.get_rect()
            textpos.left = textpos.height
            textpos.top = 0
            surface.blit(title, textpos)

            msg = "HI bpm:%3.2f  accuracy:%d%%  played:%d%%" % (self.high_score.bpm, self.high_score.percent_correct(), self.high_score.percent_played())
            text = style.font.render(msg, 1, style.bpm)
            textpos = text.get_rect()
            textpos.right = dim.width
            textpos.top = 0
            surface.blit(text, textpos)


            pad = int(dim.w / 10)
            
            h = textpos.height*2
            if style.show_helper_keyboard == "Never":
                y = dim.height
            else:
                if style.show_helper_keyboard == "PlayedKeys":
                    self.keyboard.right_keys = []
                y = dim.height-h
                self.keyboard.draw(surface, pygame.Rect(0, y, dim.width,h))

            msg = "bpm:%3.2f  accuracy:%d%%  played:%d%%" % (self.player.score.bpm, self.player.score.percent_correct(), self.player.score.percent_played())
            text = style.font.render(msg, 1, style.bpm)
            textpos = text.get_rect()
            textpos.right = dim.width
            textpos.bottom = y
            surface.blit(text, textpos)

#
#            msg = "\u2665"*self.player.lives
#            text = style.font.render(msg, 1, style.bpm)
#            textpos = text.get_rect()
#            textpos.left = 0
#            textpos.bottom = y
#            surface.blit(text, textpos)
#





        else:
            if self.win:
                title = style.font.render(self.midifile.name + " COMPLETE!", 1, style.title_fg)
            else:
                title = style.font.render(self.midifile.name + "GAME OVER", 1, style.title_fg)
            if self.score_saved == False:
                self.write_high_score_file()
                self.score_saved = True

            textpos = title.get_rect()
            self.yy = textpos.left = textpos.height
            textpos.top = 0
            surface.blit(title, textpos)

            self.yy += textpos.height
            n = style.font.render("      date                  bpm          accuracy   played  grade", 1, style.title_fg)
            tpn = n.get_rect()
            tpn.centerx = dim.centerx
            tpn.top = self.yy
            surface.blit(n, tpn)

            self.yy += textpos.height


            def print_score(s, rank):
                self.yy += textpos.height
                if hasattr(s, 'date'):
                    d = s.date.strftime("%d-%h-%y %H:%M")
                else:
                    if s.invalid:
                        d = "invalid>"
                    else:
                        d = "you>"
                bpm = "%3.2f" % (s.bpm)
                n = style.font.render("%4d  %15s      %6s          %3d%%     %3d%%      %3d " % (rank, d, bpm, s.percent_correct(), s.percent_played(), s.grade()), 1, style.title_fg)
                tpn = n.get_rect()
                tpn.centerx = dim.centerx
                tpn.top = self.yy
                surface.blit(n, tpn)

            score_printed = False
            rank = 1
            for s in self.high_scores:
                if rank < 11:
                    if score_printed == False and self.player.score.grade() > s.grade():
                        print_score(self.player.score, rank)
                        rank += 1
                        score_printed = True
                if rank < 11:
                    print_score(s, rank)
                if score_printed == True or self.player.score.grade() < s.grade():
                    rank += 1

            if score_printed == False:
                self.yy += textpos.height
                self.yy += textpos.height
                print_score(self.player.score, rank)





        self.menu_items_rects = []
        msg = "<"
        text = style.font.render(msg, 2, style.menu_item_fg)
        cp = text.get_rect()
        cp.left = 0
        cp.top = 0
        surface.blit(text, cp)
        self.menu_items_rects.append([cp, self.menu_up])




    def advance(self):
        rv = None
        if self.alive :
            self.__time += style.time_inc * style.speed / 10
            if self.next_active_note() == None:
                self.timer_last_note_down = pygame.time.get_ticks()
                self.win = 1
                self.alive = False
            elif self.next_active_note()[0].time < self.__time:
                #print("die", self.__time)
                self.win = 0
                self.alive = False
        else:
            self.dead_count += 1
            if self.dead_count > 60:
                self.dead_count = 0
                return self.return_end_of_level()



    def return_end_of_level(self):
        print("return eol")
        self.redrawme = True
        if self.win == 1:
            return "LevelComplete"
        else:
            return "LevelFail"


    def key_down(self, key):
        print("key down")
        self.redrawme = True
        if key == pygame.K_LEFT:
            self.player.score.invalid = True
            if self.alive == False or self.active_i == 0:
                return self.menu_up
            else:
                self.active_i -= 1
                self.back_up_to_bar()
        elif key == pygame.K_RIGHT:
            self.player.score.invalid = True
            self.fwd_a_bar()
        elif key == pygame.K_ESCAPE:
            return self.menu_up
        else:
            return key

    def mouse_down(self, pos):
        if hasattr(self, 'menu_items_rects'):
            items = [x for x in self.menu_items_rects if x[0].contains(pos)]
            if len(items) > 0:
                return items[0][1]

    def mouse_up(self, pos):
        pass

    def mouse_move(self, pos):
        pass

    def note_up(self, nn, notes_down):
        self.l_notes_down[:] = [n for n in self.l_notes_down if n[1].nn != nn]
        self.redrawme = True

    def note_down(self, nn, notes_down):
        self.redrawme = True
        if self.__prev_error_note in notes_down:
            ignore_error = 1
        else:
            self.__prev_error_note = -1
            ignore_error = 0

        if self.alive == False:
            return self.return_end_of_level()

        if self.timer_first_note_down == -1:
            self.timer_first_note_down = pygame.time.get_ticks()

        blb = Note()
        blb.nn = nn
        self.l_notes_down.append([self.active_i, blb])

        
        rv = 0
        if self.next_active_note():
            notes_scripted = [o.nn for o in self.next_active_note()]

            t = []
            
#            for n in notes_down:
#                blb = Note()
#                blb.nn = n
#                near = min(self.next_active_note(), key=lambda x: abs(n-x.nn))
#                blb.clef = near.clef
#                blb.x = near.x
#                blb.bad = n not in notes_scripted
#                t.append(blb)
#                self.player.score.errors += 1
#            self.l_notes_down = (self.active_i, t)


            if all (n in notes_scripted for n in notes_down):
                rv = self.next_active_note()
                self.eek = False
                if all (n in notes_down for n in notes_scripted):
                    #self.l_notes_down = (self.active_i, rv)
                    self.pop_active()
                    for n in rv:
                        if n.fail == -1:
                            n.fail = 0
                        #prevent a high score from playing the same section over and over
                        self.player.score.played_notes = max(self.player.score.played_notes, self.active_i)
                        n.bad = 0
                    total_ticks = pygame.time.get_ticks() - self.timer_first_note_down
                    total_beats = rv[0].time / self.midifile.time_sig.ticks_per_beat * (4 / self.midifile.time_sig.denominator)
                    if total_ticks > 0:
                        self.player.score.bpm = total_beats / total_ticks * 60000

                    nl = self.next_active_note()
                    if nl:
                        quantizer = int(self.midifile.time_sig.ticks_per_beat / 32)
                        time = round(nl[0].time/quantizer,0)*quantizer
                        self.goto_page(time)

                    return rv
                else:
                    return 1
            elif ignore_error == False:
                self.eek = True
                self.__prev_error_note = nn
                nl = self.next_active_note()

                for n in nl:
                    if n.fail == -1:
                        n.fail = 1
                    else:
                        n.fail += 1


                if style.speed != 0:
                    self.player.lives -= 1
                if self.player.lives < 0 :
                    self.win = 0
                    self.alive = 0

                if style.on_error == "BackToBar":
                    self.back_up_to_bar()
                return 0
        return 1

