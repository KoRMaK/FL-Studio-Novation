# name=Novation FLkey 49 MIDI
# supportedHardwareIds=00 20 29 3E 01 00 00
# url=https://forum.image-line.com/viewtopic.php?f=1914&t=277142
from script.fl import FL
from script.midi_bypass import MidiBypass

fl = FL()
midi_bypass = MidiBypass(fl)


def OnPitchBend(eventData):
    midi_bypass.on_pitch_bend(eventData)
