#!/usr/bin/python
import sys
import time
import os

sys.settrace

if __name__=="__main__":
    #https://stackoverflow.com/questions/8299270/ultimate-answer-to-relative-python-imports
    sys.path.append("..")
    foo_dir = os.path.dirname(os.path.join(os.getcwd(), __file__))
    sys.path.append(os.path.normpath(os.path.join(foo_dir, '..', '..')))
    import meowzok.meowzokapp as app
    import meowzok.menu as menu
    import meowzok.game as game
    import meowzok.style as style
    import meowzok.midifile as midifile
    import meowzok.lilydots as lilydots
else:
    from .meowzok import meowzokapp as app
    from .meowzok import menu as menu


import unittest
grunning = True
#for f in os.listdir(style.style.midi_dir):
#    gtestmidifile = style.style.midi_dir+"/"+f
#    print ("using ", gtestmidifile, " as test midi file")
#    break

#lilydots.debug_always_load_cache = False
lilydots.debug_never_load_cache = True
lilydots.print_debug_msgs = True


gtestmidifile = style.style.midi_dir + "/songs/hark-the-herald-angels-sing.mid"
#gtestmidifile = style.style.midi_dir+"/RondoAllaTurca.mid"
#gtestmidifile = style.style.midi_dir+"/songs/boccherini_minuet.mid"
gtestmidifile = style.style.midi_dir+"/songs/i-want-to-sing-in-opera.mid"
##gtestmidifile = style.style.midi_dir+"/Tetris.mid"
#gtestmidifile = style.style.midi_dir+"/songs/boccherini_minuet.mid"
#gtestmidifile = style.style.midi_dir+"/songs/russian-spy.mid"



class TestScreen(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.init_display()

    def setUp(self):
        self.b = menu.B()
        main = menu.MainMenu()
    
    @classmethod
    def tearDownClass(self):
        app.cleanup()

    def gameSelect(self):
        self.b.cs = menu.GameSelect(None, gtestmidifile)
        app.running = grunning
        app.main_loop(self.b)

    def levelFail(self):
        self.midifile = midifile.MKMidiFile(gtestmidifile)
        self.game = game.Game(main, self.midifile)
        self.b.cs = self.game
        self.game.alive = False
        self.game.win = False
        app.running = True
        app.main_loop(self.b)

    def levelComplete(self):
        self.midifile = midifile.MKMidiFile(gtestmidifile)
        self.game = game.Game(main, self.midifile)
        self.b.cs = self.game
        self.game.alive = False
        self.game.win = True
        app.running = True
        app.main_loop(self.b)

    def mainMenu(self):
        self.b.cs = menu.MainMenu()
        app.running = grunning
        app.main_loop(self.b)

    def midiMenu(self):
        self.b.cs = menu.MidiMenu(None)
        app.running = grunning
        app.main_loop(self.b)

    def pathPicker(self):
        self.b.cs = menu.PathPicker(None)
        app.running = grunning
        app.main_loop(self.b)

    def settingsMenu(self):
        self.b.cs = menu.SettingsMenu(None)
        app.running = grunning
        app.main_loop(self.b)

    def game(self):
        self.midifile = midifile.MKMidiFile(gtestmidifile)
        self.game = game.Game(None, self.midifile)
        self.game.active_i = 0
        self.game.page_i = 0
        self.b.cs = self.game
        self.b.cs.menu_up = "quit"
        app.running = grunning
        app.main_loop(self.b)

    def highscoremenu(self):
        self.b.cs = menu.HighScoreMenu(None)
        app.running = grunning
        app.main_loop(self.b)

def suite():
    suite = unittest.TestSuite()
    #suite.addTest(TestScreen("gameSelect"))
    #suite.addTest(TestScreen("mainMenu"))
    #suite.addTest(TestScreen("midiMenu"))
    #suite.addTest(TestScreen("levelComplete"))
    #suite.addTest(TestScreen("levelFail"))
    #suite.addTest(TestScreen("settingsMenu"))
    suite.addTest(TestScreen("game"))
    #suite.addTest(TestScreen("highscoremenu"))
    return suite

if __name__ == "__main__":

#import argparse
#
#    parser = argparse.ArgumentParser(description='Test meowzok')
#
#    parser.add_argument('test', metavar='N', type=int, nargs='+',
#                        help='an integer for the accumulator')
#    parser.add_argument('--sum', dest='accumulate', action='store_const',
#                        const=sum, default=max,
#                        help='sum the integers (default: find the max)')
#
#    args = parser.parse_args()
#    print args.accumulate(args.integers)


    s = suite()
    runner = unittest.TextTestRunner()
    runner.run(s)



