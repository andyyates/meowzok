About Meowzok
==========

Meowzok is a game that may help you learn to play piano & read music

* Meowzok reads midi files using mido library
* Meowzok displays sheet music engraved by Lilypond program
* Meowzok checks what keys you hit on your midi keyboard
* Meowzok gives you a score and keeps track of your hi-scores
* Meowzok is licensed the GPL v3 under


Requirements
------------

* Python 3.6
* pygame
* python-rtmidi  
* mido 
* lilypond
* a midi keyboard 

python-rtmidi needs libasound2-dev and libjack 

Running
-------

Meowzak can be run directly from this source tree directory. Just type:

 * `bin/meowzak`

Alternatively, you can install Meowzak system-wide by running:

 * `python3 setup.py install`

Developing
----------

lilydots module generates a bunch of images containing the musical dots and lines
theres are cached in ~/.cache/meowzok/name-of-midi-file by default 


