About Meowzok
==========

Meowzok is a game that may help you learn to play piano, read music,
imporove your life / waste your time. 

Meowzok reads midi files using the brilliant mido library
Meowzok displays sheet music engraved by the awesome Lilypond program
Meowzok checks what keys you hit on your keyboard
Meowzok gives you a score and keeps track of your hi-scores

Meld is licensed under the GPL v3 


Requirements
------------

* Python 3.6
* pygame
* libasound2-dev     (python-rtmidi needs asoundlib.h)
* python-rtmidi  
* mido 
* lilypond

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


