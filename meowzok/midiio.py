import pygame
import pygame.midi

a = """

pygame.midi.get_count()
 pygame.midi.get_device_info()
    returns information about a midi device
    get_device_info(an_id) -> (interf, name, input, output, opened)
    get_device_info(an_id) -> None

    Gets the device info for a given id.
    Parameters:	an_id (int) -- id of the midi device being queried
    Returns:	if the id is out of range None is returned, otherwise a tuple of (interf, name, input, output, opened) i

"""

def _get_ports():
    op = []
    for i in range(0,pygame.midi.get_count()):
        nfo = pygame.midi.get_device_info(i)
        op.append( [nfo[0], nfo[1].decode("utf-8"), nfo[2], nfo[3] ] )
    return op

def get_first_input_device_id():
    for i,o in enumerate(_get_ports()):
        if o[2]:
            return i
    return None

def open_input(device_id):
    return pygame.midi.Input(device_id)

def get_first_output_device_id():
    for i,o in enumerate(_get_ports()):
        if o[3]:
            return i
    return None

def open_output(device_id):
    return pygame.midi.Output(device_id)

def get_midi_input_port_names():
    op = []
    for i,o in enumerate(_get_ports()):
        if o[2]:
            op.append(o[1])
    return op

def get_midi_output_port_names():
    op = []
    for i,o in enumerate(_get_ports()):
        if o[3]:
            op.append(o[1])
    return op

def get_device_name(device_id):
    return pygame.midi.get_device_info(device_id)[1].decode('utf-8')


def _get_device_id_by_name(name, is_input):
    #print("------------------------_")
    #print("get by name '%s' " % (name))
    for i,o in enumerate(_get_ports()):
        #print("device", i, o)
        if o[1] == name:
            #print("Nmae match")
            if is_input:
                #print("is input?")
                if o[2]:
                    #print("Is input")
                    return i
            else:
                #print("is output?")
                if o[3]:
                    #print("Is output")
                    return i

def get_input_device_id_by_name(name):
    return _get_device_id_by_name(name, True)

def get_output_device_id_by_name(name):
    return _get_device_id_by_name(name, False)

class MidiEvent:
    def __init__(self, t, d1, d2):
        self.command = t
        self.data1 = d1
        self.data2 = d2

def read_events(input_port):
    op = []
    for o in input_port.read(64):
        v = o[0][0] & 0xF0
        if v == 0x90:
            t = "note_on"
        elif v == 0x80:
            t = "note_off"
        else:
            t = "dunno"
        op.append(MidiEvent(t, o[0][1], o[0][2]))
    return op

