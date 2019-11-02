#!/usr/bin/python

from meowzok.game import *
import copy

def get_note_with_matchin_nn(nn, notes):
    for nl in notes:
        for n in nl:
            if n.nn == nn:
                return n

class Game_Scale(Game):
    def __init__(self, up, mf):

        mf.name = mf.orig_name + " scale"
        print (mf.name)

        nnlist = []
        for nl in mf.notes:
            for n in nl:
                if n.nn not in nnlist:
                    nnlist.append(n.nn)

        nnlist.sort()

        nnotes = []
        i = 0
        i_d = 1
        t = 0
        while(len(nnotes)<16*8):
            n = copy.deepcopy(get_note_with_matchin_nn(nnlist[i], mf.notes))
            n.length_ticks = mf.time_sig.ticks_per_beat
            n.length_name = mf.time_sig.get_length_name(n.length_ticks)
            n.time = t
            nnotes.append([n])
            t += mf.time_sig.ticks_per_beat
            i += i_d
            if i < 0 or i >= len(nnlist):
                i_d *= -1
                i += i_d


        mf.active_notes = nnotes
        super().__init__(up, mf, cacheable=True)
        print("init ", mf.name)


