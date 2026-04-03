# name=Novation FLkey Mini MIDI
# supportedHardwareIds=00 20 29 3B 01 00 00
# url=https://forum.image-line.com/viewtopic.php?f=1914&t=277142
from script.fl import FL
from script.midi_bypass import MidiBypass

fl = FL()
midi_bypass = MidiBypass(fl)


def OnPitchBend(eventData):
    midi_bypass.on_pitch_bend(eventData)


def OnControlChange(eventData):
    # CC#1 is mod wheel
    if eventData.data1 == 1:
        # Uncomment to scan plugin parameters and find mod wheel:
        # midi_bypass.scan_plugin_parameters()

        midi_bypass.on_mod_wheel(eventData)
