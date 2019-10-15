About Meowzok
==========

Meowzok is a game that may help you learn to play piano & read music. 

I've tried to learn to sight read before but found I'd just learn the tune
and then stop looking at the dots. This program creates games from the 
midi files randomly making sheet music using all the right notes but in 
the wrong order

The engraving is done by Lilypond and so it looks like real actual sheet music. 
I've used other programs that just display 5 lines and some dots floating about
but I wanted a program that displays all the clefs/accidentals/beams etc

Requirements
------------

* Python 3.6
* pygame
* python-rtmidi  (needs asound.h and jack.h)
* mido 
* lilypond

on ubuntu/debian

    sudo apt-get install lilypond libasound2-dev libjack python3-pip

    sudo pip3 install pygame python-rtmidi mido

* you will also need a physical 88 key midi keyboard - smaller keyboards and a virtual keyboard are on the todo list

Running
-------

Meowzak can be run directly from this source tree directory. Just type:

 * `bin/meowzak`

Alternatively, you can install Meowzak system-wide by running:

 * `python3 setup.py install`


