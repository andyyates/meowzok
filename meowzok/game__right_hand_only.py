#!/usr/bin/python

from meowzok.game import *

class FilterGame(Game):
    def filter_notes(self, notes, rih):
        nnotes = []
        for nl in notes:
            grp = []
            for n in nl:
                if n.clef == rih:
                    grp.append(n)
            if len(grp)>0:
                nnotes.append(grp)
        return nnotes


class Game_RightHandOnly(FilterGame):
    def __init__(self, up, mf):
        mf.name = mf.orig_name + " right hand only"
        mf.active_notes = self.filter_notes(mf.notes, 0)
        super().__init__(up, mf)
        print("init ", mf.name)

class Game_LeftHandOnly(FilterGame):
    def __init__(self, up, mf):
        mf.name = mf.orig_name + " left hand only"
        mf.active_notes = self.filter_notes(mf.notes, 1)
        super().__init__(up, mf)
        print("init ", mf.name)

