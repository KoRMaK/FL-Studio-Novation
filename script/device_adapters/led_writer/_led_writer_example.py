from script.colours import Colours
from script.constants import LedLightingType


class LedWriterExample:
    """Led Writer Example

    The Led Writer class enables the script to display colours on pads and buttons on the hardware.
    """

    def __init__(self, sender, product_defs):
        """
        Args:
            sender: Used to send messages to the hardware to update LED states
            product_defs: Used to determine message types
        """

    def set_pad_colour(self, pad, colour: (Colours.Item, int, tuple)):
        """Set the colour of a pad given a Colours enum representing either
        a colour palette index or the rgb components as a tuple.

        Args:
            pad:    Pad index to set the colour for
            colour: Colours enum representing a palette index or rgb tuple (8 bits per component)

        """

    def set_button_colour(self, button, colour, *, lighting_type=LedLightingType.Static):
        """Set the colour of a button given a colour table index

        Args:
            button:         Button index to set the colour for
            colour:         Colour table index
            lighting_type:   Way in which to light the led (static, pulsing)
        """

    def start_caching_led_updates(self):
        """Start caching led updates

        Indication to start caching led updates so they can be consolidated into a single
        message and sent when stop_caching_led_updates is called.

        Note:
            A Led Writer is not required to implement caching itself and can provide empty implementations
        """

    def stop_caching_led_updates(self):
        """Stop caching led updates

        Indication to stop caching led updates. Any updates that have been cached should be consolidated
        into a single message and sent.
        """
