#!/usr/bin/python3

import MKMidiFile as mf

ts = mf.TimeSig(4,4)

times = {
                1:  "1",
                1.5:"1.",
                1/2:"2",
                3/4:"2.",
                1/4:"4",
                3/8:"4.",
                1/8:"8",
                3/16:"8.",
                1/16:"16",
                3/32:"16.",
                1/32:"32",
                3/64:"32.",
                1/64:"64",
                3/128:"64."
                }

for k,v in times.items():
    l = k * ts.ticks_per_beat*4
    rv = ts.get_length_name(l)
    if rv != v:
        print("error getting length %f was returned as %s (should have been %s)" % (k, rv, v))
    else:
        print("OK", k, l , " === ", rv)

