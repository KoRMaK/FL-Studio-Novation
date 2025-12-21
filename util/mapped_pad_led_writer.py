class MappedPadLedWriter:
    def __init__(self, pad_led_writer, pads):
        self.pad_led_writer = pad_led_writer
        self.pads = pads

    def set_pad_colour(self, pad, colour):
        self.pad_led_writer.set_pad_colour(self.pads[pad], colour)
