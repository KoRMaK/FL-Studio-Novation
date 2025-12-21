class ScreenWriterExample:
    """Screen Writer Example

    The Screen Writer class enables the script to display text on the screen(s) on the hardware.
    """

    def __init__(self, sender):
        """
        Args:
            sender: Used to send screen update messages to the hardware
        """

    def display_parameter(self, pot_index, name, value):
        """Set and temporarily display the parameter name and value associated with a pot/knob/encoder.

        Args:
            pot_index:  Pot/knob/encoder index to associate name with
            name:       Name to associate with pot/knob/encoder
            value:      Value to associate with pot/knob/encoder
        """

    def display_parameter_name(self, pot_index, name):
        """Set and temporarily display the parameter name associated with a pot/knob/encoder.

        Args:
            pot_index:  Pot/knob/encoder index to associate name with
            name:       Name to associate with pot/knob/encoder
        """

    def display_parameter_value(self, pot_index, value):
        """Set and temporarily display the parameter value associated with a pot/knob/encoder.

        Args:
            pot_index:  Pot/knob/encoder index to associate value with
            value:      Value to associate with pot/knob/encoder
        """

    def display_notification(self, primary_text="", secondary_text=""):
        """Temporarily display a notification.

        Args:
            primary_text:   Heading text for notification
            secondary_text: Detail text for notification
        """
