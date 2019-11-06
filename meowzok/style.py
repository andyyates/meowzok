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
        self.menu_item_bg = (240,240,240)
        self.menu_item_fg = (0,0,240)
        self.midi_dir = os.path.join(main_dir+"/../midi/exercises/hanon")
        self.midi_in_port = None
        self.midi_out_port = None
        self.midi_through = None
        self.screensize = (640,480)
        self.show_helper_keyboard = False
        self.speed = 0
        self.stave_bg = (255,255,255)
        self.stave_fg = (0,0,0)
        self.time_inc = 15
        self.time_line = (0,200,200)
        self.title_fg = (0,0,0)
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
        print("RESIZE STYLEee", w,h)
        self.screensize = (w,h)
        fs = int(h/30)
        self.font = pygame.font.SysFont("dejavusansmono", fs)

    def save(self):
        print("save config to ", self.config_file_path)
        with open(self.config_file_path, 'w') as fd:
            writer = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["midi_in_port", self.midi_in_port]) 
            writer.writerow(["midi_out_port", self.midi_out_port]) 
            writer.writerow(["midi_dir", self.midi_dir]) 
            if self.show_helper_keyboard:
                writer.writerow(["show_helper_keyboard", "True"])
            else:
                writer.writerow(["show_helper_keyboard", "False"])
            writer.writerow(["speed", self.speed]) 
            if self.fullscreen:
                writer.writerow(["fullscreen", "True"])
            else:
                writer.writerow(["fullscreen", "False"])
            if self.crash_piano:
                writer.writerow(["crash_piano", "True"])
            else:
                writer.writerow(["crash_piano", "False"])

    def load(self):
        if os.path.exists(self.config_file_path):
            print("load config from ", self.config_file_path)
            with open(self.config_file_path, 'r') as fd:
                csv_reader = csv.reader(fd, delimiter=',')
                for row in csv_reader:
                    print("load row", row)
                    k,v = row
                    try:
                        if k=="midi_in_port":
                            self.midi_in_port = v
                        elif k=="midi_out_port":
                            self.midi_out_port = v
                        elif k=="midi_dir":
                            self.midi_dir = v
                        elif k=="show_helper_keyboard":
                            self.show_helper_keyboard = v == "True"
                        elif k=="crash_piano":
                            self.crash_piano = v == "True"
                        elif k=="speed":
                            self.speed = int(v)
                        elif k=="fullscreen":
                            self.fullscreen = v == "True"
                        else:
                            print("config value %s=%s means nothing to me" % (k,v))
                    except:
                        print("Fail loading config value ", k, v)



style = Stylei()


