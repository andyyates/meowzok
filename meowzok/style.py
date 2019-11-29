#!/usr/bin/python3
import pygame
import os
import csv

class Stylei:
    def __init__(self):
        main_dir = os.path.split(os.path.abspath(__file__))[0]+"/"
        self.bars_per_page = 4
        self.bg = (240,240,240)
        self.bpm = (0,0,0)
        self.changed_in_main = False
        self.changed_in_menu = False
        self.config_file_path = os.path.expanduser("~/.config/meowzok.conf")
        self.fullscreen = False
        self.crash_piano = False
        self.lives = 10
        self.main_bg = (255,255,255)
        self.scroll_bar_bg = (200,200,200)
        self.scroll_bar_fg = (100,100,100)
        self.menu_item_bg = (255,255,255)
        self.menu_item_fg = (0,0,240)
        self.midi_dir = os.path.join(main_dir+"/../midi/exercises/hanon")
        self.midi_in_port = None
        self.midi_out_port = None
        self.midi_through = None
        self.kbd_lowest_note = 0
        self.kbd_highest_note = 127
        self.lilypond_path = ""
        self.screensize = (640,480)
        self.show_helper_keyboard_options = ["Always","Never","PlayedKeys"]
        self.show_helper_keyboard = self.show_helper_keyboard_options[0]
        self.on_error_options = ["BackToBar","Stop"]
        self.on_error = self.on_error_options[0]
        self.speed = 0
        self.stave_bg = (255,255,255)
        self.stave_fg = (0,0,0)
        self.time_inc = 15
        self.time_line = (0,200,200)
        self.title_fg = (0,0,0)
        self.title_win = (0,200,0)
        self.load()


    def resize_full(self):
        print("resize full")
        modes = pygame.display.list_modes()
        for m in modes:
            self.resize(m[0],m[1])
            return

    def resize_big(self):
        #m = pygame.display.Info() (messes up when you have multiple screens)
        self.resize(1100, 550) #the default width of the lilypond output


    def resize(self, w,h):
        #print("RESIZE STYLEee", w,h)
        self.screensize = (w,h)
        fs = int(h/30)
        self.font = pygame.font.SysFont("dejavusansmono", fs)

    def save(self):
        print("save config to ", self.config_file_path)
        cfgdir = os.path.dirname(self.config_file_path)
        if not os.path.exists(cfgdir):
            os.makedirs(cfgdir)
        with open(self.config_file_path, 'w', newline='') as fd:
            writer = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["midi_in_port", self.midi_in_port]) 
            writer.writerow(["midi_out_port", self.midi_out_port]) 
            writer.writerow(["midi_through", self.midi_through]) 
            writer.writerow(["midi_dir", self.midi_dir]) 
            writer.writerow(["show_helper_keyboard", self.show_helper_keyboard])
            writer.writerow(["on_error", self.on_error])
            writer.writerow(["speed", self.speed]) 
            if self.fullscreen:
                writer.writerow(["fullscreen", "True"])
            else:
                writer.writerow(["fullscreen", "False"])
            if self.crash_piano:
                writer.writerow(["crash_piano", "True"])
            else:
                writer.writerow(["crash_piano", "False"])
            writer.writerow(["kbd_lowest_note", self.kbd_lowest_note])
            writer.writerow(["kbd_highest_note", self.kbd_highest_note])
            writer.writerow(["lilypond_path", self.lilypond_path])

    def load(self):
        if not os.path.exists(self.config_file_path):
            self.no_config_file = True
        else:
            self.no_config_file = False
            print("load config from ", self.config_file_path)
            with open(self.config_file_path, 'r', newline='') as fd:
                csv_reader = csv.reader(fd, delimiter=',')
                for row in csv_reader:
                    if len(row) != 2:
                        print("load config error - row empty")
                    else:
                        k,v = row
                        try:
                            if k=="midi_in_port":
                                self.midi_in_port = v
                            elif k=="midi_out_port":
                                self.midi_out_port = v
                            elif k=="midi_through":
                                self.midi_through = v == "True"
                            elif k=="midi_dir":
                                self.midi_dir = v
                            elif k=="show_helper_keyboard":
                                self.show_helper_keyboard = v 
                            elif k=="on_error":
                                self.on_error = v
                            elif k=="crash_piano":
                                self.crash_piano = v == "True"
                            elif k=="speed":
                                self.speed = int(v)
                            elif k=="fullscreen":
                                self.fullscreen = v == "True"
                            elif k=="kbd_highest_note":
                                self.kbd_highest_note = int(v)
                            elif k=="kbd_lowest_note":
                                self.kbd_lowest_note = int(v)
                            elif k=="lilypond_path":
                                self.lilypond_path = v
                            else:
                                print("config value %s=%s means nothing to me" % (k,v))
                        except:
                            print("Fail loading config value ", k, v)



style = Stylei()


