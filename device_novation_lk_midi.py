# name=Novation Launchkey MK3 MIDI
# url=https://forum.image-line.com/viewtopic.php?f=1914&t=277142
from script.fl import FL
from script.midi_bypass import MidiBypass

fl = FL()
midi_bypass = MidiBypass(fl)


# def OnNoteOn(eventData):
#     midi_bypass.on_note_on(eventData)


# def OnNoteOff(eventData):
#     midi_bypass.on_note_off(eventData)


# def OnPitchBend(eventData):
#     midi_bypass.on_pitch_bend(eventData)
