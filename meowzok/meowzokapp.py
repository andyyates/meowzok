#!/usr/bin/env python3

from meowzok.menu import *
from meowzok.util import *
from meowzok.game import *
from pygame.locals import *
import mido
import os, pygame
import random
import sys
import time

#import SloppyDots as MKDots
#game_globs.dot_class = MKDots.SloppyDots
import meowzok.lilydots as Dots
game_globs.dot_class = Dots.LilyDots

clock = pygame.time.Clock()

midi_in = None
midi_out = None
screen = None
event_get = None
surface = None
running = True


def init_display():
    global midi_in
    global midi_out
    global screen
    global event_get
    global surface

    style.screensize = (1000,100)
    pygame.display.init()
    pygame.font.init()
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

    pn = get_midi_input_ports()
    if style.midi_in_port in pn:
        pn = style.midi_in_port
    else:
        pn = [x for x in pn if x.lower().find('through') == -1]
        if len(pn)>0:
            style.midi_in_port = pn = pn[0]
        else:
            pn = None
            ip = None
    if pn == None :
        midi_in = None
        ipport = None
    else:
        ipport = pn 
        print("Open midi in from ", pn)
        midi_in = mido.open_input(pn)



    pn = get_midi_output_ports()
    if style.midi_out_port in pn:
        pn = style.midi_out_port
    else:
        if not ipport in pn:
            pn = ip
            style.midi_out_port = pn
        else:
            pn = [x for x in pn if x.lower().find('through') == -1]
            pn = pn[0]
            style.midi_out_port = pn
    if (pn == None):
        midi_out = None
    else:
        print("Open midi out from ", pn)
        midi_out = mido.open_output(pn)

    if midi_out:
        midi_out.send(mido.Message(type="control_change", control=122, value=0))


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

        for msg in note_off_cue:
            midi_out.send(msg)
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
                if r == pygame.K_ESCAPE:
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

            if midi_in == None or style.midi_in_port != midi_in.name:
                old_in_name = None
                if midi_in:
                    old_in_name = midi_in.name+""
                    midi_in.close()
                try:
                    print("Open midi in from ", style.midi_in_port)
                    midi_in = mido.open_input(style.midi_in_port)
                except:
                    print("Error trying to open port ", style.midi_in_port)
                    if old_in_name:
                        style.midi_in_port = old_in_name
                        print("Attempt to re-open ", style.midi_in_port)
                        midi_in = mido.open_input(style.midi_in_port)

            if midi_out == None or style.midi_out_port != midi_out.name:
                old_out_name = None
                if midi_out:
                    old_out_name = midi_out.name+""
                    midi_out.send(mido.Message(type="control_change", control=122, value=127))
                    midi_out.close()
                try:
                    print("Open midi out from ", style.midi_out_port)
                    midi_out = mido.open_output(style.midi_out_port)
                except:
                    print("Error trying to open port ", style.midi_out_port)
                    if old_out_name:
                        style.midi_out_port = old_out_name
                        print("Attempt to re-open ", style.midi_out_port)
                        midi_out = mido.open_output(style.midi_out_port)
                if midi_out:
                    midi_out.send(mido.Message(type="control_change", control=122, value=0))

            style.changed_in_main = True
        
        if midi_in:
            msg = midi_in.poll()
            while(msg):
                if msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                    #print("NOTE off ", nn, msg.type)
                    nn = msg.note
                    process_note_off(nn)
                    midi_out.send(msg)
                elif msg.type == "note_on":
                    nn = msg.note
                    if not nn in notes_down:
                        notes_down.append(nn)
                        n1 = Note()
                        n2 = Note()
                        n1.nn = nn
                        n2.nn = nn
                        n1.clef = 0
                        n2.clef = 1
                        r = b.note_down(nn, notes_down)
                        if r == 0:
                            print("make a horrid noise")
                            for i in range(0,4):
                                nn = random.randint(44,127)
                                midi_out.send(mido.Message(type='note_on', note=nn, velocity=127))
                                note_off_cue.append(mido.Message(type='note_off', note=nn, velocity=127))
                        else:
                            midi_out.send(msg)
                            if hasattr(r,'pop'):
                                for n in r:
                                    process_note_off(n.nn)



                msg = midi_in.poll()
        else:
            time.sleep(1)
            pn = get_midi_input_ports()
            if pn != None and len(pn)>0:
                pn = pn[0]
                midi_in = mido.open_input(pn)
                b.cs = MainMenu()

        clock.tick(30)

        r = b.advance()
        #print (r)
        if hasattr(r, 'pop'):
            print("Messaging from advance :", r)
            for n in r:
                midi_out.send(mido.Message(type='note_on', note=n.nn, velocity=127))
                note_off_cue.append(mido.Message(type='note_off', note=n.nn, velocity=127))
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
        midi_out.send(mido.Message(type="control_change", control=122, value=127))
        midi_out.close()

    if midi_in:
        print("cleanup midi in")
        midi_in.close()

    print("cleanup display")
    pygame.display.quit()
    print("display closed")
    pygame.quit()
    print("toodles")


def run(argv):
    argc = len(sys.argv)
    if argc == 1:
        init_display()
        b = B()
        if midi_in == None:
            b.cs = MidiMenu()
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
            fl = os.listdir(style.midi_file_path)
            if argc > 2:
                init_display()
                lvls = load_midi_file(style.midi_file_path+"/"+sys.argv[2]+".mid")
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
