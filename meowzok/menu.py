from meowzok.game import *
from meowzok.util import *
from meowzok.midifile import *
from meowzok.style import style
from meowzok import midiio
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
            items_on_page = int(dim.height/tp.height)-1

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
        self.menu = []
        self.add_menu_item("play song", [Game, [self, MKMidiFile(path), True]])
        for g in games:
            title = " ".join(re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', g[0])).split()[1:])
            self.add_menu_item(title, [g[1], [self, MKMidiFile(path)]])


class MidiNoteMenu(Menu):
    def __init__(self, up, title, setting_key, current_value):
        super().__init__(up)
        self.title = "settings > " + title
        for i in range(0,128):
            self.add_menu_item(title=str(i), action=[self.menu_up.set, [setting_key, i]], nn=i)

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
            if os.path.isdir(self.value + "/" + f):
                self.add_menu_item(title=f, action=[self.change_dir, [f]])
            else:
                self.add_menu_item(title=f, action=[self.menu_up.set, [self.setting_key, self.value]])

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
        self.title = "settings"
        self.menu = []
        self.add_menu_item(title="Midi In  : %s " % (style.midi_in_port), action=[OptionsMenu, [self, "Midi In",midiio.get_midi_input_port_names(), "midi_in", style.midi_in_port]])
        self.add_menu_item(title="Midi Out : %s " % (style.midi_out_port), action=[OptionsMenu, [self, "Midi Out",midiio.get_midi_output_port_names(), "midi_out", style.midi_out_port]])
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


        if style.midi_through:
            s = "True"
        else:
            s = "False"
        self.add_menu_item(title="midi through: %s " % (s), action=[OptionsMenu, [self, "midi_through",["True","False"], "midi_through", s]])


        if style.crash_piano:
            s = "True"
        else:
            s = "False"
        self.add_menu_item(title="crash piano: %s " % (s), action=[OptionsMenu, [self, 'crash_piano', ["True","False"], "crash_piano", s]])

        self.add_menu_item(title="kbd - lowest note: %s " % style.kbd_lowest_note, action=[MidiNoteMenu, [self, 'kbd - lowest note', "kbd_lowest_note", style.kbd_lowest_note]])
        self.add_menu_item(title="kbd - highest note: %s " % style.kbd_highest_note, action=[MidiNoteMenu, [self, 'kbd - highest note', "kbd_highest_note", style.kbd_highest_note]])


    def draw(self, surface):
        if style.changed_in_main == True:
            style.changed_in_main = False
            self.__rebuild_menu()
        super().draw(surface)

class QuitMenu(Menu):
    def __init__(self,main_menu):
        super().__init__(None)
        self.title = "Exit ?"
        self.add_menu_item(title="no", action=main_menu)
        self.add_menu_item(title="yes", action="quit")

#class HighScoreMenu(Menu):
#    def __init__(self, up)
#        super().__init__(up)
#        self.title = "High scores"

class MainMenu(Menu):
    def __init__(self):
        quitm = QuitMenu(self)
        self.dir = style.midi_dir
        super().__init__(quitm)
        self.title = "Meowzok"
        self.file_i = 0
        self.page = 0
        self.rebuild_menu()

    def rebuild_menu(self):
        self.menu = []
        self.current_path = style.midi_dir

        self.add_menu_item(title=">..", action=[self.change_dir, [".."]])
        if os.path.exists(self.dir):
            for f in sorted(os.listdir(self.dir)):
                if os.path.isdir(self.dir+"/"+f):
                    self.add_menu_item(title=">"+f, action=[self.change_dir, [f]])
            for f in sorted(os.listdir(self.dir)):
                if not os.path.isdir(self.dir+"/"+f):
                    if f.endswith(".mid"):
                        path = self.dir+"/"+f
                        name = re.sub("[^A-Za-z0-9]"," ",f)#.replace(".mid",""))
                        self.add_menu_item(title=" "+name, action=[GameSelect, [self, path]])

        self.add_menu_item(title="",action="")
        self.add_menu_item(title="settings",action=[SettingsMenu, [self]])

    def draw(self,surface):
        if self.current_path != style.midi_dir:
            self.rebuild_menu()
        super().draw(surface)


    def change_dir(self, f):
        print("CHange dir ", self.dir, f)
        self.dir = os.path.realpath(os.path.join(self.dir+"/", f))
        print("Value ", self.dir)
        self.rebuild_menu()
        self.menu_selection = 0
        if self.dir != style.midi_dir:
            self.messages = [self.dir]
        else:
            self.messages = []
        return self


    def key_down(self, key):
        if key == pygame.K_LEFT:
            if self.dir != style.midi_dir:
                if len(self.dir) > len(style.midi_dir):
                    self.change_dir("..")
                    return None
                else:
                    self.change_dir(style.midi_dir)
                    return None
        return super().key_down(key)




















class B:
    def __init__(self ):
        self.cs = MainMenu()

    def change_menu(self, numenu):
        self.cs = numenu
        if hasattr(numenu, 'on_open'):
            numenu.on_open()

    def __act(self,r):
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
            return self.__act( self.cs.key_down(key))
        return key

    def mouse_down(self, pos):
        rect = [pos[0],pos[1],1,1]
        if hasattr(self.cs, 'mouse_down'):
            return self.__act( self.cs.mouse_down(rect) )

    def advance(self):
        return self.__act( self.cs.advance() )

    def note_down(self,nn, notes_down):
        return self.__act( self.cs.note_down(nn, notes_down) )

    def draw(self, surface ):
        self.cs.draw(surface )


