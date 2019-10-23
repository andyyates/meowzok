from meowzok.game import *
from meowzok.util import *
from meowzok.midifile import *
from meowzok.style import style
import re
import importlib


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
        self.menu_top_item = 0
        self.menu_selection = 0
        self.menu = []
        self.title = "NO TITLE"

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
            msg = "\u2192"
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
        tp = self.__draw_text(surface,self.title,x,y,(0,0,0))
        y += tp.height
        self.menu_items_rects = []

        if hasattr(self,"menu_up"):
            msg = "\u2190"
            text = style.font.render(msg, 2, (0,0,0))
            cp = text.get_rect()
            cp.left = 0
            cp.top = 0
            surface.blit(text, cp)
            self.menu_items_rects.append([cp, self.menu_up])


        for m in self.messages:
            tp = self.__draw_text(surface,m,x,y,(0,0,0))
            y += tp.height

        if self.game == None:
            items_on_page = int(dim.height/tp.height)

            if self.menu_selection >= items_on_page+self.menu_top_item:
                self.menu_top_item +=1
            elif self.menu_selection < self.menu_top_item and self.menu_top_item>0:
                self.menu_top_item -=1

            for o in self.menu[self.menu_top_item:]:
                tp = self.__draw_text(surface, o.title, tp.height,y, (0,0,200), o.i == self.menu_selection)
                y += tp.height
                if y > dim.height:
                    break
                self.menu_items_rects.append([tp, o.action])
        pygame.draw.rect(surface, style.menu_item_bg, (0,y,dim.width,dim.height-y))

                
    def note_down(self, nn, notes_down):
        for m in self.menu:
            if m.nn == nn:
                return m.action
        
    def mouse_down(self, pos):
        items = [x for x in self.menu_items_rects if x[0].contains(pos)]
        #print(items)
        if len(items) > 0:
            return items[0][1]

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
        self.add_menu_item("plug the midi cable in!", action=lambda:gmainmenu)

main_dir = os.path.split(os.path.abspath(__file__))[0]
games = []
for f in os.listdir(main_dir):
    if f.startswith("game__") and f.endswith(".py"):
        print ("Importing ", f.replace(".py",""))
        mod = importlib.import_module("."+f.replace(".py",""), "meowzok")
        for n in dir(mod):
            if n.startswith("Game_"):
                print ("DIE", n)
                games.append([n, getattr(mod, n)])
                print ("loaded " , n, " from ", f)
    

class GameSelect(Menu):
    def __init__(self, up, path):
        super().__init__(up)
        filename = os.path.basename(path)
        self.title = filename.replace(".mid", "")
        self.midi_file = MKMidiFile(path)
        self.menu = []
        self.add_menu_item("play song", lambda : Game(self, self.midi_file))
        for g in games:
            self.add_menu_item(g[0], [g[1], [self, self.midi_file]])

    def advance(self):
        self.midi_file.name = self.midi_file.orig_name
        super().advance()

        #
        #self.add_menu_item("start with 3 notes", ['load_midi_file_game', 1, path])
        #self.add_menu_item("scales with all the notes", ['load_midi_file_game', 2, path])
        #self.add_menu_item("right hand only", ['load_midi_file_game', 3, path])
        #self.add_menu_item("left hand only", ['load_midi_file_game', 4, path])
        #self.add_menu_item("random notes right hand", ['load_midi_file_game', 5, path])
        #self.add_menu_item("random notes left hand", ['load_midi_file_game', 6, path])
        #self.add_menu_item("random notes both hands", ['load_midi_file_game', 7, path])
        #self.add_menu_item("listen song", ['listen_midi_file', path])


class OptionsMenu(Menu):
    def __init__(self, up, title, options, setting_key, current_value=None, message=None):
        super().__init__(up)
        self.title = "settings > " + title
        if message:
            self.messages = [message]
        for i,o in enumerate(options):
            self.add_menu_item(title=o, action=[self.menu_up.set,[setting_key,o]])
            if current_value == o:
                #print("Current value == ", current_value)
                self.menu_selection = i


class PathPicker(Menu):
    def __init__(self, up, title, pick_folders, setting_key, current_value):
        super().__init__(up)
        self.title = "settings > " + title
        self.value = current_value
        self.setting_key = setting_key
        self.rebuild_menu()

    def rebuild_menu(self):
        self.menu = []
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
            self.add_menu_item(title=f, action=[self.change_dir, [f]])

    def change_dir(self, f):
        print("CHange dir ", self.value, f)
        self.value = os.path.realpath(os.path.join(self.value+"/", f))
        print("Value ", self.value)
        self.rebuild_menu()
        self.menu_selection = 0
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
                style.show_helper_keyboard = set_value == "Yes"
            elif set_key == "fullscreen":
                style.fullscreen = set_value == "True"
                self.messages = ["restart to make change happen"]
            elif set_key == "set_speed":                
                style.speed = self.speeds.index(set_value)
            elif set_key == "set_midi_dir":
                style.midi_dir = set_value
            else:
                print("Unknown settings key ", set_key, "=", set_value)
            style.changed_in_menu = True
            style.save()
        self.__rebuild_menu()
        return self


    def __rebuild_menu(self):
        self.title = "settings"
        self.menu = []
        self.add_menu_item(title="Midi In  : %s " % (style.midi_in_port), action=[OptionsMenu, [self, "Midi In",get_midi_input_ports(), "midi_in", style.midi_in_port]])
        self.add_menu_item(title="Midi Out : %s " % (style.midi_out_port), action=[OptionsMenu, [self, "Midi Out",get_midi_output_ports(), "midi_out", style.midi_out_port]])
        if style.show_helper_keyboard:
            s = "Yes"
        else:
            s = "No"
        self.add_menu_item(title="Show Kbd : %s " % (s), action=[OptionsMenu, [self, "Show Kbd",["Yes","No"], "show_kbd", s]])

        spdname = self.speeds[style.speed]
        self.add_menu_item(title="Game speed:%s" % ( spdname ) , action=[OptionsMenu, [self, "Game speed", self.speeds, "set_speed", spdname]])
        self.add_menu_item(title="Midi files:%s" % (style.midi_dir), action=[PathPicker, [self, "Midi files:", True, "set_midi_dir", style.midi_dir]])

        if style.fullscreen:
            s = "True"
        else:
            s = "False"
        self.add_menu_item(title="Fullscreen: %s " % (s), action=[OptionsMenu, [self, "Fullscreen",["True","False"], "fullscreen", s]])




    def draw(self, surface):
        if style.changed_in_main == True:
            style.changed_in_main = False
            self.__rebuild_menu()
        super().draw(surface)




#
#class LevelFail(Menu):
#    def __init__(self, game):
#        super().__init__()
#        self.game = game
#        self.game.write_high_score_file()
#        self.title = "GAME OVER"
#        self.messages = [
#                "bpm       : %3.2f" % (self.game.player.score.bpm), 
#                "bum notes : %d" % (self.game.player.score.errors),
#                "played    : %d%%" % (self.game.player.score.percent_played()),
#                "grade     : %d" % (self.game.player.score.grade())
#                ]
#
#        self.add_menu_item(nn=77, title="Retry %s" % game.levels[game.player.level].name, action="retry_level")
#        self.menu_up = [GameSelect, [self.game.levels[0].midi_file_path]]
#
#
#class LevelComplete(Menu):
#    def __init__(self, game):
#        super().__init__()
#        self.game = game
#        self.game.write_high_score_file()
#        self.menu = []
#        self.menu_up = [GameSelect, [self.game.levels[0].midi_file_path]]
#        self.title = 'Complete'
#        self.messages = [
#                "bpm       : %3.2f" % (self.game.player.score.bpm), 
#                "bum notes : %d" % (self.game.player.score.errors),
#                "played    : %d%%" % (self.game.player.score.percent_played()),
#                "grade     : %d" % (self.game.player.score.grade())
#                ]
#        if len(game.levels) > game.player.level+1:
#            self.add_menu_item(nn=77, title="%s" % (game.levels[game.player.level+1].name), action="next_level")
#        else:
#            self.add_menu_item(nn=77, title="play again %s" % game.levels[game.player.level].name, action="retry_level")
#

class MainMenu(Menu):
    def __init__(self):
        super().__init__(None)
        self.title = "Meowzok"
        self.file_i = 0
        self.page = 0
        self.__rebuild_menu()

    def __rebuild_menu(self):
        self.menu = []
        self.current_path = style.midi_dir
        if os.path.exists(style.midi_dir):
            a = [ x for x in sorted(os.listdir(style.midi_dir)) if x.endswith('.mid')]
            for p in a:
                path = style.midi_dir+"/"+p
                name = re.sub("[^A-Za-z0-9]"," ",p.replace(".mid",""))
                self.add_menu_item(title=name, action=[GameSelect, [self, path]])

        self.add_menu_item(title="",action="")
        self.add_menu_item(title="settings",action=[SettingsMenu, [self]])

    def draw(self,surface):
        if self.current_path != style.midi_dir:
            self.__rebuild_menu()
        super().draw(surface)


class B:
    def __init__(self ):
        self.cs = MainMenu()


    def __act(self,r):
        if hasattr(self.cs, 'act'):
            r = self.cs.act(r)
        if r == None:
            return
#        if r == "LevelComplete":
#            self.cs = LevelComplete(self.cs)
#            return
#        elif r == "LevelFail":
#            self.cs = LevelFail(self.cs)
#            return
#        elif r == "retry_level":
#            if hasattr(self.cs.game, 'excersize'):
#                ex = self.cs.game.excersize
#                p = self.cs.game.player
#                lvls = load_midi_file_game(difficulty = ex[1], filename = ex[2])
#                self.cs.game = Game(lvls)
#                self.cs.game.excersize = ex
#                self.cs.game.player = p
#            self.cs.game.retry_level()
#            self.cs = self.cs.game
#        elif r == "next_level":
#            if (self.cs.game.next_level()):
#                self.cs = self.cs.game
#            else:
#                self.cs = gmainmenu
#            return
        elif hasattr(r, 'menu'):
            self.cs = r
            return None
        elif callable(r):
            self.cs = r()
        elif hasattr(r, 'pop'):
#            if r[0] == "load_midi_file":
#                lvls = load_midi_file(r[1])
#                self.cs = Game(lvls)
#                return
#            if r[0] == "load_midi_file_game":
#                lvls = load_midi_file_game(difficulty= r[1], filename= r[2])
#                self.cs = Game(lvls)
#                self.cs.excersize = r.copy()
#                return
            if callable(r[0]):
                self.cs = r[0](*r[1])
            else:
                print ("Unknonw menu action ", r)

        print("return B act r == ", r)
        return r


    def key_down(self, key):
        if hasattr(self.cs, 'key_down'):
            return self.__act( self.cs.key_down(key))
        return key

    def mouse_down(self, pos):
        rect = [pos[0],pos[1],1,1]
        if hasattr(self.cs, 'mouse_down'):
            return self.__act( self.cs.mouse_down(rect) )

    def advance(self):
        return self.__act( self.cs.advance() )

    def note_down(self,nn, notes_down):
        print(self.cs.note_down)
        return self.__act( self.cs.note_down(nn, notes_down) )

    def draw(self, surface ):
        self.cs.draw(surface )


