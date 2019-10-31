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
else:
    from .meowzok import meowzokapp as app
    from .meowzok import menu as menu

import unittest
grunning = False
for f in os.listdir(style.style.midi_dir):
    gtestmidifile = style.style.midi_dir+"/"+f
    break

class TestScreen(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.init_display()

    def setUp(self):
        self.b = menu.B()
        self.lvls = game.load_midi_file(gtestmidifile)
        self.game = game.Game(self.lvls)
    
    @classmethod
    def tearDownClass(self):
        app.cleanup()



    def gameSelect(self):
        self.b.cs = menu.GameSelect(None, "/foo/bar/baz")
        app.running = grunning
        app.main_loop(self.b)

#    def levelComplete(self):
#        self.b.cs = menu.LevelComplete(self.game)
#        app.running = grunning
#        app.main_loop(self.b)
#
#    def levelFail(self):
#        self.b.cs = menu.LevelFail(self.game)
#        app.running = grunning
#        app.main_loop(self.b)

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


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestScreen("gameSelect"))
    suite.addTest(TestScreen("mainMenu"))
    suite.addTest(TestScreen("midiMenu"))
    #suite.addTest(TestScreen("pathPicker"))
    suite.addTest(TestScreen("settingsMenu"))
    return suite

if __name__ == "__main__":
    s = suite()
    runner = unittest.TextTestRunner()
    runner.run(s)



