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



from meowzok import lilydots
lilydots.use_threading = False
lilydots.debug_always_load_cache = False
lilydots.print_debug_msgs = True
#mf = midifile.MKMidiFile("/home/pj/midi/songs/hark-the-herald-angels-sing.mid")
mf = midifile.MKMidiFile("/home/pj/midi/songs/ABBA-DancingQueen.mid")
#mf = midifile.MKMidiFile("/home/pj/midi/songs/frankly_muse.mid")
mf.cacheable = False
l = lilydots.LilyDots(mf)


