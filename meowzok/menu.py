from meowzok.game import *
from meowzok.util import *
from meowzok.midifile import *
from meowzok.style import style
from meowzok import midiio
import re
import importlib
import textwrap


class MenuItem():
    def __init__(self, i, title, action):
        self.title = title
        self.action = action
        self.i = i

class  Menu:
    def __init__(self, up):
        self.menu_up = up
        self.messages = []
        self.message_i = 0
        self.game = None
        self.menu_items_rects = []
        self.clear_screen = True
        self.menu_selection = 0
        self.menu = []
        self.title = "NO TITLE"
        self.scroll_top = 0
        self.scroll_bar = None
        self.scroll_bar_handle = None
        self.scroll_scale = 0
        self.scroll_step = 10
        self.in_scroll = False

    
    def add_menu_item(self, title, action, nn=None):
        m=MenuItem(len(self.menu), title, action)
        m.nn = nn
        self.menu.append(m)
    
    def advance(self):
        pass

    def __draw_text(self,surface, txt, x, y,color,selected=None):

        text = style.font.render(txt, 2, color)
        textpos = text.get_rect()
        textpos.left = x+textpos.height
        textpos.top = y

        # background
        dim = surface.get_rect()
        pygame.draw.rect(surface, style.menu_item_bg, (0,textpos.top,dim.width,textpos.height))
        surface.blit(text, textpos)

        if selected:
            msg = ">"
            text = style.font.render(msg, 2, color)
            cp = text.get_rect()
            cp.left = x
            cp.top = y
            surface.blit(text, cp)

        return textpos



    def draw(self, surface):
        if self.clear_screen:
            self.clear_screen = False
            surface.fill(style.main_bg)

        dim = surface.get_rect()


        x,y = 0,0
        tp = self.__draw_text(surface,"  "+self.title,x,y,(0,0,0))
        font_height = tp.height
        y += font_height 
        tp = self.__draw_text(surface," ",x,y,(0,0,0))
        y += font_height 
        self.menu_items_rects = []

        def scry(y):
            return y-self.scroll_top

        def visible(y):
            ty = scry(y)
            return ty >= 0 and ty < dim.h

        if (hasattr(self,"menu_up") and self.menu_up != self) or (hasattr(self,"has_up") and self.has_up()):
            msg = "  <"
            text = style.font.render(msg, 2, style.menu_item_fg)
            cp = text.get_rect()
            cp.left = 0
            cp.top = 0
            surface.blit(text, cp)
            if hasattr(self,'has_up') and self.has_up():
                self.menu_items_rects.append([cp, self.up_dir])
            else:
                self.menu_items_rects.append([cp, self.menu_up])

        for m in self.messages:
            if len(m)>50:
                for l in textwrap.wrap(m, 77):
                    if visible(y):
                        tp = self.__draw_text(surface,l,x,scry(y),(0,0,0))
                    y += font_height
            else:
                if visible(y):
                    tp = self.__draw_text(surface,m,x,scry(y),(0,0,0))
                y += font_height

        if self.game == None:
            for o in self.menu:
                if visible(y):
                    tp = self.__draw_text(surface, o.title, font_height, scry(y), style.menu_item_fg, o.i == self.menu_selection)
                    self.menu_items_rects.append([tp, o.action])
                y += font_height

        last = scry(y)
        if last < dim.height:
            pygame.draw.rect(surface, style.menu_item_bg, (0,last,dim.width,dim.height-last))

        self.scroll_bar = pygame.Rect(dim.w-tp.height, 0, tp.height, dim.h)
        self.scroll_step = font_height
        self.scroll_scale = (y+font_height-dim.height)/dim.height
        pygame.draw.rect(surface, style.scroll_bar_bg, self.scroll_bar)
        if self.scroll_scale > 0:
            handle_top = min(self.scroll_top / self.scroll_scale, dim.h-tp.height)
            self.scroll_bar_handle = pygame.Rect(dim.w-tp.height, handle_top, tp.height, tp.height)
            pygame.draw.rect(surface, style.scroll_bar_fg, self.scroll_bar_handle)
                
    def note_down(self, nn, notes_down):
        for m in self.menu:
            if m.nn == nn:
                return m.action
        
    def mouse_down(self, pos):
        if self.scroll_scale>0 and self.scroll_bar_handle.contains(pos):
            self.in_scroll = True
            return None
        else:
            items = [x for x in self.menu_items_rects if x[0].contains(pos)]
            if len(items) > 0:
                return items[0][1]

    def mouse_up(self, pos):
        if self.scroll_scale > 0:
            self.in_scroll = False

    def mouse_move(self, pos):
        if self.scroll_scale > 0 and self.in_scroll:
            r = pygame.Rect(pos)
            np = r.y * self.scroll_scale
            self.scroll_top = self.scroll_step*int(np/self.scroll_step)


    def key_down(self, key):
        if key == pygame.K_DOWN:
            if self.menu_selection < len(self.menu)-1:
                self.menu_selection+=1
        elif key == pygame.K_UP:
            if self.menu_selection>0:
                self.menu_selection-=1
        elif key == pygame.K_RIGHT or key == pygame.K_RETURN:
            if self.menu_selection > -1 and self.menu_selection < len(self.menu):
                return self.menu[self.menu_selection].action
        elif key == pygame.K_LEFT or key == pygame.K_ESCAPE:
            if hasattr(self, "menu_up") and self.menu_up != None:
                return self.menu_up
            else:
                return "quit"
        else:
            return key

class MidiMenu(Menu):
    def __init__(self, up):
        super().__init__(up)
        self.title = "No input!"
        self.messages = ['Plug in the midi cable', 'the one connected to the piano', 'this computer has no connection to your piano', 'a usb cable maybe?']

main_dir = os.path.split(os.path.abspath(__file__))[0]
games = []
for f in os.listdir(main_dir):
    if f.startswith("game__") and f.endswith(".py"):
        mod = importlib.import_module("."+f.replace(".py",""), "meowzok")
        for n in dir(mod):
            if n.startswith("Game_"):
                games.append([n, getattr(mod, n)])
    

class GameSelect(Menu):

    def __init__(self, up, path):
        super().__init__(up)
        filename = os.path.basename(path)
        self.title = filename.replace(".mid", "")
        self.menu = []
        self.add_menu_item("play song", [self._run_game, [Game, path]])
        for g in games:
            title = " ".join(re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', g[0])).split()[1:])
            self.add_menu_item(title, [self._run_game, [g[1], path]])

    def _run_game(self, game, path):
        mf = MKMidiFile(path)
        return game(self, mf)


class MidiNoteMenu(Menu):
    def __init__(self, up, title, setting_key, current_value, message=None):
        super().__init__(up)
        if message:
            self.messages = [message, " "]
        self.title = "Settings > " + title
        for i in range(0,128):
            self.add_menu_item(title=str(i), action=[self.menu_up.set, [setting_key, i]], nn=i)

class OptionsMenu(Menu):
    def __init__(self, up, title, options, setting_key, current_value=None, message=None):
        super().__init__(up)
        self.title = "Settings > " + title
        if message:
            self.messages = [message," "]
        for i,o in enumerate(options):
            self.add_menu_item(title=o, action=[self.menu_up.set,[setting_key,o]])
            if current_value == o:
                self.menu_selection = i


class PathPicker(Menu):
    def __init__(self, up, title, pick_folders, setting_key, current_value, message=None):
        super().__init__(up)
        if message:
            self.messages = [message," "]
        self.title = "Settings > " + title
        self.value = current_value
        self.setting_key = setting_key
        self.rebuild_menu()

    def rebuild_menu(self):
        self.menu = []
        self.scroll_top = 0
        print("Scroll top = 0")
        while self.value and not os.path.exists(self.value):
            print("file not exist ", self.value)
            self.value = os.path.dirname(self.value)
            print("trying ", self.value)
        if not self.value:
            print("not anything")
            self.value = os.path.expanduser("~")
            print("Trying ", self.value)
        self.add_menu_item(title=".", action=[self.menu_up.set, [self.setting_key, self.value]])
        self.add_menu_item(title="..", action=[self.change_dir, [".."]])
        for i,f in enumerate(sorted(os.listdir(self.value))):
            if os.path.isdir(self.value + "/" + f):
                self.add_menu_item(title=f, action=[self.change_dir, [f]])
            else:
                self.add_menu_item(title=f, action=[self.menu_up.set, [self.setting_key, self.value]])

    def change_dir(self, f):
        self.value = os.path.realpath(os.path.join(self.value+"/", f))
        self.rebuild_menu()
        self.menu_selection = 0
        return self

    def has_up(self):
        return self.value != "/"

    def up_dir(self):
        change_dir("..")
        return self


class SettingsMenu(Menu):
    def __init__(self, up):
        super().__init__(up)
        self.speeds = ["very easy","quite easy","easish","still quite do-able","well its not that fast","average speed, not stupid","ridiculouse speed","impossible speed","ludicrous speed"]
        self.__rebuild_menu()


    def set(self, set_key=None, set_value=None):
        if set_key != None:
            if set_key == "midi_in":
                style.midi_in_port = set_value
            elif set_key == "midi_out":
                style.midi_out_port = set_value
            elif set_key == "show_kbd":
                if set_value in style.show_helper_keyboard_options:
                    style.show_helper_keyboard = set_value 
                else:
                    style.show_helper_keyboard = style.show_helper_keyboard_options[0]
            elif set_key == "on_error":
                if set_value in style.on_error_options:
                    style.on_error = set_value
                else:
                    style.on_error = style.on_error_options[0]
            elif set_key == "fullscreen":
                style.fullscreen = set_value == "True"
            elif set_key == "set_speed":                
                style.speed = self.speeds.index(set_value)
            elif set_key == "midi_through":
                style.midi_through = set_value == "True"
            elif set_key == "crash_piano":
                style.crash_piano = set_value == "True"
            elif set_key == "set_midi_dir":
                style.midi_dir = set_value
            elif set_key == "kbd_lowest_note":
                style.kbd_lowest_note = set_value
            elif set_key == "kbd_highest_note":
                style.kbd_highest_note = set_value
            
            else:
                print("Unknown settings key ", set_key, "=", set_value)
            style.changed_in_menu = True
            style.save()
        self.__rebuild_menu()
        return self


    def __rebuild_menu(self):
        self.title = "Settings"
        self.menu = []
        self.add_menu_item( title="midi in            : %s " % (style.midi_in_port), action=[OptionsMenu, [self, "Midi In",midiio.get_midi_input_port_names(), "midi_in", style.midi_in_port,"Select the port that the midi is coming in on, aka midi in"]])
        self.add_menu_item( title="midi out           : %s " % (style.midi_out_port), action=[OptionsMenu, [self, "Midi Out",midiio.get_midi_output_port_names(), "midi_out", style.midi_out_port,"Select a midi device that will make some noise for you - this program won't make any. If you have a real piano then you don't need this unless you want to hear a huge crash when you play a wrong note"]])
        self.add_menu_item( title="show Kbd           : %s " % (style.show_helper_keyboard), action=[OptionsMenu, [self, "Show Kbd",style.show_helper_keyboard_options, "show_kbd", style.show_helper_keyboard,"Displays a virtual keyboard at the bottom of the screen that displays the notes you should be playing, and the ones you are playing. It doesn't work like you can click it with a mouse or anything. that would be daft"]])

        self.add_menu_item( title="on error           : %s " % (style.on_error), action=[OptionsMenu, [self, "On error",style.on_error_options, "on_error", style.on_error,"When you play a wrong note - not that you ever would, but if you did, then do you want to just have another stab at that one note - or go back to the start of the bar where you screwed up? If your learning sight reading and trying to play piano without looking at the keys, probably best to have this as stop. If you want to play something from memory then it makes more sense to go back to the start of the bar"]])

        #spdname = self.speeds[style.speed]
        #self.add_menu_item( title="game speed         : %s" % ( spdname ) , action=[OptionsMenu, [self, "Game speed", self.speeds, "set_speed", spdname,"This is a redundant option, I'll probably take it out soon, but if you want to play against the machine, set this to anything but the first option and a nasty line will track across the music and you have to play faster than it to stay alive. Best just select the first option and be done with it"]])
        self.add_menu_item( title="midi files         : %s" % (style.midi_dir), action=[PathPicker, [self, "Midi files:", True, "set_midi_dir", style.midi_dir,"Where do you keep your midi files, i'm sure you have lots. Tell me where. Click the single dot to select the directory for use"]])

        if style.fullscreen:
            s = "True"
        else:
            s = "False"
        self.add_menu_item( title="fullscreen         : %s " % (s), action=[OptionsMenu, [self, "Fullscreen",["True","False"], "fullscreen", s,"Ronseal"]])


        if style.midi_through:
            s = "True"
        else:
            s = "False"
        self.add_menu_item( title="midi through       : %s " % (s), action=[OptionsMenu, [self, "midi_through",["True","False"], "midi_through", s,"If your using a real piano piano then set this as false - the delay in this python program is quite noticable if you are playing fast. If you only have a controller keyboard and would like this program to route the midi to it then by all means set it to true, but just don't try and play any fast things"]])


        if style.crash_piano:
            s = "True"
        else:
            s = "False"
        self.add_menu_item( title="crash piano        : %s " % (s), action=[OptionsMenu, [self, 'crash_piano', ["True","False"], "crash_piano", s,"Personal fav options here - if you play a wrong note then this option will crash the piano for you, sort of like and angry piano teacher crashing all the keys and shouting 'no no no this is not music this is shit'"]])

        self.add_menu_item( title="kbd - lowest note  : %s " % style.kbd_lowest_note, action=[MidiNoteMenu, [self, 'kbd - lowest note', "kbd_lowest_note", style.kbd_lowest_note,"Lowest note you have on your keyboard - if you selected a midi device earlier, then you should be able to just play the lowest note and we'll move on"]])
        self.add_menu_item( title="kbd - highest note : %s " % style.kbd_highest_note, action=[MidiNoteMenu, [self, 'kbd - highest note', "kbd_highest_note", style.kbd_highest_note,"Highest note you have on your keyboard - like i already said, if you have a piano, just play the top key and were all done ... enjoy"]])


    def draw(self, surface):
        if style.changed_in_main == True:
            style.changed_in_main = False
            self.__rebuild_menu()
        super().draw(surface)

class Wizzard(SettingsMenu):
    def __init__(self,up):
        super().__init__(up)
        self.item_no = -1

    def next_item(self):
        self.item_no += 1
        if self.item_no >= len(self.menu):
            return self.menu_up
        r = self.menu[self.item_no]
        return r.action[0](*r.action[1])

    def set(self,set_key,set_value):
        super().set(set_key, set_value)
        return self.next_item()





class QuitMenu(Menu):
    def __init__(self,main_menu):
        super().__init__(None)
        self.menu_up = self
        self.title = "Exit ?"
        self.add_menu_item(title="no", action=main_menu)
        self.add_menu_item(title="yes", action="quit")

class HighScoreMenu(Menu):
    def __init__(self, up):
        super().__init__(up)
        self.title = "High scores"
        self.messages = ["  %50s   %10s    %3s " % ("filename","last beat","grade")]
        self.messages.append("")

    def on_open(self):
        self.menu = []
        scores = load_high_scores()
        scores.sort()
        scores.reverse()
        scores_by_game = {}
        for s in scores:
            k = s.midifile+s.game
            if k not in scores_by_game.keys():
                scores_by_game[k] = s
        scores = [v for k,v in scores_by_game.items()]
        scores.sort(key=lambda s: s.date)
        today = datetime.datetime.now()
        for s in scores:
            if s.game == "Game_LeftHandOnly" or s.game == "Game_RightHandOnly":
                continue
            diff = today - s.date
            if diff.days == 0:
                d = "today"
            else:
                if diff.days == 1:
                    d = "1day"
                else:
                    d = "%d days" % (diff.days)
            bpm = "%3.2f" % (s.bpm)
            gn = s.game.replace("Game_","")
            if gn == "RandomNotes":
                gn = "Random"
            if gn == "Game":
                gn = ""
            fn = s.midifile.replace(".mid","").replace("-"," ")
            n = "%40s %10s  %10s    %3d " % (fn , gn, d, s.grade())

            self.add_menu_item(title=n, action=[self._run_game, [s.game, s.midifile]])

    def find(self, name, path):
        for root, dirs, files in os.walk(path):
            if name in files:
                return os.path.join(root, name)


    def _run_game(self, game_name, fn):
        game = Game
        for g in games:
            if g[0] == game_name:
                game = g[1]
        path = self.find(fn, style.midi_dir)
        if path == None:
            self.messages[1] = "Could not find that midifile in your midi dir. Have you changed midi dir recently or deleted that file?"
            return self
        else:
            mf = MKMidiFile(path)
            return game(self, mf)






class MainMenu(Menu):
    def __init__(self):
        quitm = QuitMenu(self)
        self.dir = self.midi_dir = style.midi_dir #note midi dir so we know when it gets changed in settings menu
        super().__init__(quitm)
        self.title = " Meowzok"
        self.file_i = 0
        self.page = 0
        self.rebuild_menu()


    def rebuild_menu(self):
        self.menu = []
        self.scroll_top = 0
        self.add_menu_item(title=" hi scores",action=[HighScoreMenu, [self]])

        self.add_menu_item(title="",action="")

        if len(self.dir) > len(style.midi_dir):
            self.add_menu_item(title=" ..", action=[self.change_dir, [".."]])
        if os.path.exists(self.dir):
            for f in sorted(os.listdir(self.dir)):
                if os.path.isdir(self.dir+"/"+f):
                    self.add_menu_item(title="+"+f, action=[self.change_dir, [f]])
            for f in sorted(os.listdir(self.dir)):
                if not os.path.isdir(self.dir+"/"+f):
                    if f.endswith(".mid"):
                        path = self.dir+"/"+f
                        name = re.sub("[^A-Za-z0-9]"," ",f)#.replace(".mid",""))
                        self.add_menu_item(title=" "+name, action=[GameSelect, [self, path]])

        self.add_menu_item(title="",action="")
        self.add_menu_item(title=" settings",action=[SettingsMenu, [self]])

    def draw(self,surface):
        if self.midi_dir != style.midi_dir:
            self.dir = self.midi_dir = style.midi_dir
            print("REBUILD MENU")
            self.rebuild_menu()
        super().draw(surface)


    def change_dir(self, f):
        self.dir = os.path.realpath(os.path.join(self.dir+"/", f))
        self.rebuild_menu()
        self.menu_selection = 0
        return self

    def has_up(self):
        return len(self.dir) > len(style.midi_dir)

    def up_dir(self):
        if self.has_up():
            self.change_dir("..")
        else:
            self.change_dir(style.midi_dir)
        return self

    def key_down(self, key):
        if key == pygame.K_LEFT:
            if self.dir != style.midi_dir:
                self.up_dir()
        return super().key_down(key)




















class B:
    def __init__(self ):
        self.cs = MainMenu()

    def change_menu(self, numenu):
        self.cs = numenu
        if hasattr(numenu, 'on_open'):
            numenu.on_open()

    def act(self,r):
        #if hasattr(self.cs, 'act'):
        #    r = self.cs.act(r)
        if r == None:
            return
        elif hasattr(r, 'menu'):
            self.change_menu(r)
            return None
        if callable(r):
            self.change_menu(r())
            return None
        elif hasattr(r, 'pop'):
            if callable(r[0]):
                self.change_menu(r[0](*r[1]))
                return None
        return r


    def key_down(self, key):
        if hasattr(self.cs, 'key_down'):
            return self.act( self.cs.key_down(key))
        return key

    def mouse_down(self, pos):
        rect = [pos[0],pos[1],1,1]
        return self.act( self.cs.mouse_down(rect) )

    def mouse_up(self, pos):
        rect = [pos[0],pos[1],1,1]
        return self.act( self.cs.mouse_up(rect))

    def mouse_move(self, pos):
        rect = [pos[0],pos[1],1,1]
        return self.act( self.cs.mouse_move(rect))

    def advance(self):
        return self.act( self.cs.advance() )

    def note_down(self,nn, notes_down):
        return self.act( self.cs.note_down(nn, notes_down) )

    def draw(self, surface ):
        self.cs.draw(surface )


