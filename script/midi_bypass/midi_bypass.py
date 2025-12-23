import util.math


class MidiBypass:
    def __init__(self, fl):
        self.fl = fl

    def _get_target_channel(self, launchkey_selected_channel):
        """
        Get the target channel for MIDI routing.
        Uses launchkey_selected_channel if available, otherwise FL Studio UI selection.
        """
        if launchkey_selected_channel is not None:
            return launchkey_selected_channel
        return self.fl.selected_channel()

    def on_note_on(self, eventData, launchkey_selected_channel=None):
        """Handle MIDI note on events and route to Launchkey's selected channel"""
        eventData.handled = True

        target_channel = self._get_target_channel(launchkey_selected_channel)
        if target_channel is None:
            return

        note = eventData.data1
        velocity = eventData.data2

        self.fl.send_note_on(note, velocity, group_channel=target_channel)

    def on_note_off(self, eventData, launchkey_selected_channel=None):
        """Handle MIDI note off events and route to Launchkey's selected channel"""
        eventData.handled = True

        target_channel = self._get_target_channel(launchkey_selected_channel)
        if target_channel is None:
            return

        note = eventData.data1

        self.fl.send_note_off(note, group_channel=target_channel)

    def on_pitch_bend(self, eventData, launchkey_selected_channel=None):
        eventData.handled = True

        target_channel = self._get_target_channel(launchkey_selected_channel)
        if target_channel is None:
            return

        value = eventData.data1 | eventData.data2 << 7
        normalised_pitch = util.math.normalise(value=value, lower_bound=0, upper_bound=1 << 14)
        self.fl.channel.set_pitch(normalised_pitch, group_channel=target_channel)
