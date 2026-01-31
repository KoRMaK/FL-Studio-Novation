# name=Novation Launchkey MK3 MIDI
# url=https://forum.image-line.com/viewtopic.php?f=1914&t=277142
from script.fl import FL
from script.midi_bypass import MidiBypass

try:
    import channels
except ImportError:
    pass

fl = FL()
midi_bypass = MidiBypass(fl)

# Marker suffix used by DAW script to indicate selected channel
MARKER_SUFFIX = " | lk"
launchkey_selected_channel = None


def scan_for_marked_channel():
    """Scan all channels to find the one marked with ' | lk' suffix"""
    global launchkey_selected_channel

    try:
        channel_count = channels.channelCount()
        for channel_index in range(channel_count):
            channel_name = channels.getChannelName(channel_index)
            if channel_name.endswith(MARKER_SUFFIX):
                launchkey_selected_channel = channel_index
                return
        # No marked channel found
        launchkey_selected_channel = None
    except Exception:
        launchkey_selected_channel = None


def OnIdle():
    """Called periodically - scan for marked channel"""
    #scan_for_marked_channel()
    #print("lk idle")


def OnNoteOn(eventData):
    scan_for_marked_channel()
    midi_bypass.on_note_on(eventData, launchkey_selected_channel)
    
    # Uncomment to scan plugin parameters and find mod wheel:
    #midi_bypass.scan_plugin_parameters(launchkey_selected_channel)



def OnNoteOff(eventData):
    scan_for_marked_channel()
    midi_bypass.on_note_off(eventData, launchkey_selected_channel)


def OnPitchBend(eventData):
    scan_for_marked_channel()
    midi_bypass.on_pitch_bend(eventData, launchkey_selected_channel)


def OnControlChange(eventData):
    # CC#1 is mod wheel
    if eventData.data1 == 1:
        scan_for_marked_channel()

        midi_bypass.on_mod_wheel(eventData, launchkey_selected_channel)
