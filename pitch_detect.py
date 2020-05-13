#!/usr/bin/env python3

import sys
import signal
import os
import jack
import threading
import numpy as np
import statistics
from aubio import source, pitch

if sys.version_info < (3, 0):
    signal.signal(signal.SIGINT, signal.SIG_DFL)

client = jack.Client("pitcher")
if client.status.server_started:
    print("JACK server started")
if client.status.name_not_unique:
    print("unique name {0!r} assigned".format(client.name))

event = threading.Event()




#pitch detect





win_s = 4096 
hop_s = client.blocksize  
samplerate = client.samplerate
tolerance = 1.1
pitch_o = pitch("yin", win_s, hop_s, samplerate)
pitch_o.set_unit("midi")
pitch_o.set_tolerance(tolerance)

#pitches = []
#confidences = []


silence_time = 0
noise_time = 0







def get_name(pitch):
    octave = pitch // 12
    name = (pitch % 12) * 2
    return "%s %s" % (octave, "C C#D D#E F F#G G#A A# B"[name:name+2])



avg_nn = []

@client.set_process_callback

def process(frames):
    global silence_time
    global noise_time
    assert frames == client.blocksize
    #for i, o in zip(client.inports, client.outports):
    #    o.get_buffer()[:] = i.get_buffer()
    samples = client.inports[0].get_array()
    pitch = pitch_o(samples)
    #pitch = int(round(pitch))
    confidence = pitch_o.get_confidence()
    if confidence < 0.5: pitch = 0.
    #print(pitch)
    pitch = int(pitch)
    if pitch != 0:
        noise_time += 1
        silence_time = 0
        avg_nn.append(pitch)
    else:
        noise_time = 0
        silence_time += 1

    if noise_time > 100 or silence_time > 10 and len(avg_nn) > 10:
        nn = round(statistics.mean(avg_nn))
        print("AVG:")
        print(nn)
        print(get_name(nn))
        avg_nn.clear()

    datain = []

#    pitches += [pitch]
#    confidences += [confidence]
#    total_frames += read
#    if read < hop_s: break





@client.set_shutdown_callback
def shutdown(status, reason):
    print("JACK shutdown!")
    print("status:", status)
    print("reason:", reason)
    event.set()


client.inports.register("input")

with client:
    client.connect("system:capture_8", "pitcher:input")

    print("Press Ctrl+C to stop")
    try:
        event.wait()
    except KeyboardInterrupt:
        print("\nInterrupted by user")

