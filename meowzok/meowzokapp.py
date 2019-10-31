#!/usr/bin/env python3

from meowzok.menu import *
from meowzok.util import *
from meowzok.game import *
from meowzok import midiio 

from pygame.locals import *
import os, pygame, pygame.midi

import random
import sys
import time

#import meowzok.sloppydots as MKDots
#style.dot_class = MKDots.SloppyDots
import meowzok.lilydots as Dots
style.dot_class = Dots.LilyDots

clock = pygame.time.Clock()

midi_in = None
midi_out = None
input_device_id = None
output_device_id = None
screen = None
event_get = None
surface = None
running = True

def debug(a):
    print(a)
    
def open_midi_ports():
    global midi_in
    global midi_out
    global input_device_id
    global output_device_id

    if midi_in:
        debug("Midi in open, close midi in")
        midi_in.close()
        midi_in = None
    if midi_out:
        debug("Midi out open, close midi out")
        midi_out.close()
        midi_out = None
    debug("getting input from settings")
    input_device_id = midiio.get_input_device_id_by_name(style.midi_in_port)
    if input_device_id == None:
        debug("no input device from settings, using first device")
        input_device_id = midiio.get_first_input_device_id()
    if input_device_id == None:
        debug("failed to get input device")
        midi_in = None
    else:
        debug("Open input device")
        midi_in = midiio.open_input(input_device_id)

    debug("get output from settings")
    output_device_id = midiio.get_output_device_id_by_name(style.midi_out_port)
    if output_device_id == None:
        debug("no output device from settings, use first device")
        output_device_id = midiio.get_first_output_device_id()
    if output_device_id == None:
        debug("no output device")
        midi_out = None
    else:
        debug("open output device")
        midi_out = midiio.open_output(output_device_id)


def init_display():
    global screen
    global event_get
    global surface

    style.screensize = (1000,100)
    pygame.display.init()
    pygame.font.init()
    pygame.midi.init()
    pygame.display.set_caption('Kill the music')

    if style.fullscreen:
        style.resize_full()
        screen = pygame.display.set_mode(style.screensize, pygame.FULLSCREEN)
    else:
        style.resize_big()
        screen = pygame.display.set_mode(style.screensize)

    dim = screen.get_rect()
    pygame.fastevent.init()
    pygame.key.set_repeat(150,10)
    event_get = pygame.fastevent.get


    surface = pygame.Surface(screen.get_size())
    surface.convert()
    surface.fill(style.main_bg)
    pygame.display.update()

notes_down = []


def process_note_off(nn):
    if not nn in notes_down:
        pass
    else:
        notes_down.remove(nn)

def main_loop(b):
    global midi_in
    global midi_out
    global screen
    global event_get
    global running

    note_off_cue = []

    while running:
        #print("Running")
        events = event_get()

        #surface.blit(layout.surface, (0,0))

        for nn in note_off_cue:
            midi_out.note_off(nn)
        note_off_cue.clear()
#        if(hasattr(b.cs, 'dot_drawer')):
#            if(hasattr(b.cs, 'active_notes')):
#                for n in display_notes:
#                    if n.consumed == 0:
#                        #n.x = b.cs.active_notes[0][0].x
#                        b.cs.dot_drawer.draw_note(n, surface, alt_sprite = layout.sprites.splat, alt_sprite_sharp = layout.sprites.splat_sharp)
#            else:
#                for n in display_notes:
#                    if n.consumed == 0:
#                        n.draw(surface, alt_sprite = layout.sprites.splat, alt_sprite_sharp = layout.sprites.splat_sharp)

        for e in events:
            if e.type in [QUIT]:
                print("-Quit")
                running = False
                print("Quit x")
            elif e.type in [KEYDOWN]:
                r = b.key_down(e.key)
                #print(r, r == None)
                if r == "quit":
                    print("quit")
                    running = False
                    print("quit e")
            #elif e.type in [pygame.midi.MIDIIN]:
            #    print (e)
            elif e.type in [MOUSEBUTTONDOWN]:
                b.mouse_down(e.pos)

        if running == False:
            break

        if style.changed_in_menu == True:
            style.changed_in_menu = False
            open_midi_ports()
            style.changed_in_main = True
        
        if midi_in:
            #print("Polling..")
            while(midi_in.poll()):
                print("Poll true")
                ii = 0
                for evt in midiio.read_events(midi_in):
                    ii += 1
                    print("Cycle events ", ii)
                    print (evt)
                    if evt.command == "note_off" or (evt.command == "note_on" and evt.data2 == 0):
                        print("NOTE off ", evt.data1)
                        nn = evt.data1
                        process_note_off(nn)
                        if style.midi_through and midi_out:
                            midi_out.note_off(nn)
                    elif evt.command == "note_on":
                        nn = evt.data1
                        if style.midi_through and midi_out:
                            midi_out.note_on(nn, evt.data2)
                        if not nn in notes_down:
                            notes_down.append(nn)
                            r = b.note_down(nn, notes_down)
                            if r == 0:
                                print("make a horrid noise")
                                for i in range(0,4):
                                    nn = random.randint(44,127)
                                    midi_out.note_on(nn, random.randint(90,120))
                                    note_off_cue.append(nn)
                            else:
                                if hasattr(r,'pop'):
                                    for n in r:
                                        process_note_off(n.nn)
        else:
            pass
            #time.sleep(1)
            #pn = midiio.get_first_input_device_id()
            #if pn != None:
            #    open_midi_ports()
            #    b.cs = MainMenu()

        clock.tick(30)

        b.advance()

        b.draw(surface)
        screen.blit(surface, (0, 0))
        pygame.display.update()

def cleanup():
            # convert them into pygame events.
#            midi_evs = pygame.midi.midis2events(midi_events, i.device_id)
#
#            for m_e in midi_evs:
#                event_post( m_e )
    print("start cleanup")

    #local on
    if midi_out:
        print("cleanup midi out")
        midi_out.close()

    if midi_in:
        print("cleanup midi in")
        midi_in.close()

    print("cleanup display")
    pygame.display.quit()
    print("display closed")
    pygame.midi.quit()
    print("midi closed")
    pygame.quit()
    print("toodles")


def run(argv):
    argc = len(sys.argv)
    if argc == 1:
        init_display()
        b = B()
        if midi_in == None:
            b.cs = MidiMenu(b.cs)
        main_loop(b)
        cleanup()
    elif argc > 1:
        if sys.argv[1] == "test":
            #fl = os.listdir("tests")
            if argc > 2:
                __import__("tests."+sys.argv[2])
                exit()
            else:
                for f in fl:
                    if f.startswith("__"):
                        continue
                    print("main.py test " + f.replace(".py",""))
        elif sys.argv[1] == "load":
            fl = os.listdir(style.midi_dir)
            if argc > 2:
                init_display()
                lvls = load_midi_file(style.midi_dir+"/"+sys.argv[2]+".mid")
                b = B()
                b.cs = Game(lvls)
                main_loop(b)
                cleanup()
            else:
                for f in fl:
                    if f.endswith(".mid"):
                        print("main.py load " + f.replace(".mid",""))
        else:
            init_display()
            b = B()
            b.cs = eval(sys.argv[1]+"()")
            main_loop(b)
            cleanup()

    else:
        fl = os.listdir("tests")
        for f in fl:
            if f.startswith("__"):
                continue
            print("main.py test " + f.replace(".py",""))


if __name__ == "__main__":
    run(sys.argv)
