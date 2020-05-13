#!/usr/bin/python3


import statistics 
import csv
import os
from meowzok import mido
import copy


class TimeSig:
    def __init__(self,numerator, denominator):
        self.numerator = numerator
        self.denominator = denominator
        self.ticks_per_beat = 480
        self.note_length_names = {
                1:  "1",
                3/2:"1.",
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
                3/128:"64.",
        }

        # this just makes a mess of most simple midi files so probably left out
        #        7/4:"1..",
        #        7/8:"2..",
        #        7/16:"4..",
        #        7/32:"8..",
        #        7/64:"16..",
        #        7/128:"32..",
        #        7/256:"64.."

        self.key_sig = "C"
        #self.key_sig_is_major = 1

    def quantize_time(self, time):
        q = 1/64*self.ticks_per_beat*4
        t = round(time / q , 0) * q
        return t

    def get_biggest_valid_length(self, length_ticks):
        #print("Len ticks", length_ticks)
        if length_ticks == 0:
            raise("Error - biggest valid length of zero is zero")
        fraction_len = length_ticks/(self.ticks_per_beat*4)
        for l in reversed(sorted(self.note_length_names.keys())):
            #print( fraction_len, l)
            if l <= fraction_len:
                return l*self.ticks_per_beat*4
        raise("Error - couldn't find a big enough value")

    def smallest_length(self):
        return sorted(self.note_length_names.keys())[0] * self.ticks_per_beat*4

    def is_valid_length(self, length_ticks):
        if length_ticks == 0:
            return False
        fraction_len = length_ticks/(self.ticks_per_beat*4)
        return fraction_len in self.note_length_names.keys()

    def quantize_length(self, length_ticks):
        if length_ticks == 0:
            print("Length IS ZERO!")
            raise Exception('length is zero!')
        fraction_len = length_ticks/(self.ticks_per_beat*4)
        length = min(self.note_length_names.keys(),  key=lambda x:abs(x-fraction_len))
        return length*self.ticks_per_beat*4

    def get_length_name(self, length_ticks):
        if length_ticks == 0:
            print("Length IS ZERO!")
            raise Exception('spam', 'eggs')
        fraction_len = length_ticks/(self.ticks_per_beat*4)
        #length = min(self.note_length_names.keys(),  key=lambda x:abs(x-fraction_len))
        if fraction_len not in self.note_length_names.keys():
            raise Exception("I can't handle a note with length of ", length_ticks, "/" , self.ticks_per_beat*4, " ")
        return self.note_length_names[fraction_len]

    def get_bar_len(self):
        return int(self.numerator * (self.ticks_per_beat * (4 / self.denominator)))

class Note:
    def __init__(self, nn=64, time=None, clef=0, length_ticks=None, length_name=None):
        self.x, self.y = (0,0)
        self.nn = nn
        self.time = time
        self.clef = clef
        self.yd = 0
        self.consumed = 0
        self.sprite = None
        self.length_ticks = length_ticks
        self.length_name = length_name

    def note_name(self):
        return 'c,c#,d,d#,e,f,f#,g,g#,a,a#,b'.split(",")[self.nn%12]

    def __eq__(self, other): 
        if not isinstance(other, Note):
            return NotImplemented
        return self.nn == other.nn and self.clef == other.clef



class MKMidiFile():

  
    def __make_config_file_name(self, filename):
        return filename[:-4]+".csv"

    def __load_config_file(self, filename):
        fn = self.__make_config_file_name(filename)
        if not os.path.exists(fn):
            #print("No config file at ", fn)
            return

        with open(fn, newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for lin,row in enumerate(csv_reader):
                if len(row) != len(self.config_csv_header):
                    print("csv header does not match len=%d should be len=%d" % (len(row), len(self.config_csv_header)))
                else:
                    if lin == 0:
                        for i,v in enumerate(self.config_csv_header):
                            if row[i] != v:
                                print("csv header does not match %d %s!=%s" % (i, row[i], v))
                                return False
                    else:
                        k = row[0]
                        v = row[1]
                        pass
                        #
                        #if k == "key_sig_sharps":
                        #    try:
                        #        self.time_sig.key_sig_sharps = int(v)
                        #    except:
                        #        print("Could not convert %s to int" % v)
                        #elif k == "key_sig_is_major":
                        #    try:
                        #        selt.time_sig.key_sig_is_major = bool(v)
                        #    except:
                        #        print("Could not convert %s to bool" %v)
                        #else:
                        #    print("Unknown row in " + fn)

    def __save_config_file(self, filename):
        fn = self.__make_config_file_name(filename)
        with open(fn,'w',newline='') as fd:
            writer = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(self.config_csv_header)


        
    def __init__(self, path):
        tmp_notes = []
        self.config_csv_header = ["setting","value"]
        self.time_sig = TimeSig(4,4)
        self.path = path
        self.orig_name = self.name = os.path.basename(path).replace(".mid","")

        print ("loading ", path)
        mid = mido.MidiFile(path)

        time_sig = None

        self.time_sig.ticks_per_beat = mid.ticks_per_beat
        notes_on = []
        #copy all notes into a single list
        #turn all note relative values into absolute values 
        #calculate note lengths

        for trk in mid.tracks:
            time = 0
            for msg in trk:
                time += msg.time
                if msg.type == "time_signature":
                    time_sig = msg
                    self.time_sig.numerator = time_sig.numerator
                    self.time_sig.denominator = time_sig.denominator
                elif msg.type == "note_on" and msg.velocity > 0:
                    n = Note()
                    n.nn = msg.note
                    n.channel = msg.channel
                    n.clef = msg.channel % 2
                    n.time = time
                    n.length_name = "unset"
                    tmp_notes.append(n)
                    notes_on.append(n)
                elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                    killem = [n for n in notes_on if n.nn == msg.note and n.channel == msg.channel]
                    for n in killem:
                        notes_on.remove(n)
                        l = time - n.time
                        if l == 0:
                            print(msg)
                            print("Note len zero at ", time, n.time, " note dropped")
                        else:
                            n.length = self.time_sig.quantize_length(l)
                            n.time = self.time_sig.quantize_time(n.time)
                            #n.length_ticks = self.time_sig.quantize_length(l)
                            #n.time = self.time_sig.quantize_time(n.time)
                            #n.length_name = self.time_sig.get_length_name(n.length_ticks)
                elif msg.type == "key_signature":
                    self.time_sig.key_sig = msg.key

        tmp_notes.sort(key = lambda x: x.time)

        #split into upto 8 levels
        self.notes = [[] for x in range(0,8)]
        for n in tmp_notes:
            level = int(n.channel / 2)
            level_list = self.notes[level]
            if len(level_list) == 0:
                level_list.append([n])
            else:
                tail = level_list[-1]
                if tail[0].time == n.time:
                    tail.append(n)
                else:
                    level_list.append([n])

        #flip bass & treble if it makes sense
        for level in self.notes:
            a = [0,0]
            for i in range(0,2):
                lst = [n.nn for sub in level for n in sub if n.clef == i]
                if len(lst)>0:
                    a[i] = statistics.mean(lst)
                    a[i] = min([71,50], key=lambda x:abs(x-a[i]))
                else:
                    a[i] = 99999

            if (a[0] == 99999 and a[1] == 71) or (a[1] == 99999 and a[0] == 50) or (a[0] == 50 and a[1] == 71): 
                print("Flip") 
                for nl in level:
                    for n in nl:
                        n.clef = 1 - n.clef

        #get rid of midi-channels 2+
        self.notes = self.notes[0]
        self.active_notes = self.notes

        self.__load_config_file(path)



