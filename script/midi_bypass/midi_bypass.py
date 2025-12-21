import util.math


class MidiBypass:
    def __init__(self, fl):
        self.fl = fl

    def on_pitch_bend(self, eventData):
        eventData.handled = True

        if not self.fl.is_any_channel_selected():
            return

        value = eventData.data1 | eventData.data2 << 7
        normalised_pitch = util.math.normalise(value=value, lower_bound=0, upper_bound=1 << 14)
        self.fl.channel.set_pitch(normalised_pitch)
