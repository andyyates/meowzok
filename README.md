About Meowzok
==========

Meowzok is a game that may help you learn to play piano & read music. 

This program creates games from midi files, either randomly making sheet music 
using all the right notes in the wrong order, or testing your speed at 
playing various parts of the music. 

After playing piece of music a score is calculated from the BPM you played at
and the number of bum notes you hit. The scores are recorded so you can beat 
your hi scores and give yourself a pat on the back. Well done

The engraving is done by Lilypond and so it looks like real actual sheet music. 
it's got clefs and accidentals and those beams and them rests in various lengths. 
It's not a complete midi to sheet music converter, but it works for most simple midi files

Requirements
------------

This is a pre-pre-alpha release. For now, it's using the mido library and that has a 
dependency on python-rtmidi 

* Python 3.6
* pygame
* python-rtmidi  (needs asound.h and jack.h)
* mido 
* lilypond

On ubuntu/debian

    sudo apt-get install lilypond libasound2-dev libjack python3-pip

    sudo pip3 install pygame python-rtmidi mido

* you will also need a physical 88 key midi keyboard - smaller keyboards and a virtual keyboard are on me todo list

Running
-------

Meowzok can be run directly from this source tree directory. Just type:

 * `bin/meowzok`

Alternatively, you can install Meowzok system-wide by running:

 * `python3 setup.py install`


