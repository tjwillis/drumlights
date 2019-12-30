import pygame, pygame.midi

# midi input device
midi_input_name = 'USB Midi Cable MIDI 1'#'Tbox 2X2'
midi_noteon_statuses = [i for i in range(144,160)]
midi_noteoff_statuses = [i for i in range(128,144)]

# drum led count
NUM_LEDS_KICK = 30
NUM_LEDS_SNARE = 48
NUM_LEDS_TOM1 = 38
NUM_LEDS_TOM2 = 38
NUM_LEDS_TOM3 = 38
NUM_LEDS_HHAT = 14
NUM_LEDS_CRASH1 = 13
NUM_LEDS_CRASH2 = 14
NUM_LEDS_RIDE = 15

notenum_dict = {
    40:'SNARE_RIM',
    50:'TOM1_RIM',
    47:'TOM2_RIM',
    58:'TOM3_RIM',
    26:'HHAT_OPEN_RIM',
    22:'HHAT_CLOSED_RIM',
    55:'CRASH1_RIM',
    52:'RIDE_RIM',
    59:'CRASH2_RIM',
    
    36:'KICK_HEAD',
    38:'SNARE_HEAD',
    48:'TOM1_HEAD',
    45:'TOM2_HEAD',
    43:'TOM3_HEAD',
    46:'HHAT_OPEN_HEAD',
    42:'HHAT_CLOSED_HEAD',
    49:'CRASH1_HEAD',
    57:'RIDE_HEAD',
    51:'CRASH2_HEAD'
}

def get_midi_device_number(name):
    for device_number in range(pygame.midi.get_count()):
        device_info = pygame.midi.get_device_info(device_number)
        if device_info[1] == name and device_info[2] == 1:
            return device_number

def get_midi_input(name):
    return pygame.midi.Input(get_midi_device_number(name))

def foo(name,notenum):
    print('callback from {} ({})'.format(name,notenum))

class Event:
    def __init__(self,status,drum,velocity):
        self.status, self.drum, self.velocity = status, drum, velocity

    def __str__(self):
        return str(self.drum.name) + ' ' + str(self.status) + ' velocity=' + str(self.velocity)

class Drum:
    def __init__(self,name,notenum):
        self.name, self.notenum = name, notenum
        self.callback = lambda: foo(self.name,self.notenum)

class TD9:
    def __init__(self):
        self.drums = []
        for notenum in notenum_dict:
            self.drums.append(Drum(notenum_dict[notenum], notenum))

        self.events = []

        pygame.midi.init()
        self.midi_input = get_midi_input(midi_input_name)

    def get_drum_by_notenum(self, notenum):
        return next(drum for drum in self.drums if drum.notenum == notenum)

    def message_to_event(self, message):
        assert len(message) == 4, 'Message is not the correct format'
        status, drum, velocity = None, None, None

        if message[0] in midi_noteon_statuses: status = 'NOTE_ON'
        elif message[0] in midi_noteoff_statuses: status = 'NOTE_OFF'

        if message[1] in notenum_dict: drum = self.get_drum_by_notenum(message[1])
        else: drum = None
        
        velocity = message[2]

        return Event(status, drum, velocity)

    def get_event(self):
        return self.events.pop()

    def get_events(self):
        events = []
        while self.events:
            events.append(self.get_event())
        return events

    def process_events(self):
        while self.events:
            self.get_event().drum.callback()

    def read(self):
        if self.midi_input.poll():
            messages = self.midi_input.read(1000)

            for message in messages:
                self.events.append(self.message_to_event(message[0]))

        self.process_events()

    def watch(self):
        while True:
            self.read()

if __name__ == '__main__':
    td9 = TD9()
    td9.watch()