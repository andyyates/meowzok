#!/usr/bin/python

from meowzok.game import *
import copy

class Game_RandomNotes(Game):
    def __init__(self, up, mf):

        mf.name = mf.orig_name + " random notes" 
        print (mf.name)

        nnotes = []
        t = 0
        while(len(nnotes)<16*4):
            nl = random.choice(mf.notes)
            if len(nnotes)>0:
                ok = True
                for n in nl:
                    if n.nn in [pn.nn for pn in nnotes[-1]]:
                        ok = False
                        break
                if ok == False:
                    continue
            grp = []
            for i in range(0,len(nl)):
                n = copy.deepcopy(nl[i])
                n.length_ticks = mf.time_sig.ticks_per_beat
                n.length_name = mf.time_sig.get_length_name(n.length_ticks)
                n.time = t
                grp.append(n)
            if len(grp)>0:
                nnotes.append(grp)
                t += mf.time_sig.ticks_per_beat

        mf.active_notes = nnotes
        super().__init__(up, mf, cacheable=False)
        print("init ", mf.name)


