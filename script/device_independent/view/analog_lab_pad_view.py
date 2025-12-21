from script.colours import Colours
from script.colour_utils import scale_colour
from script.device_independent.util_view.view import View

try:
    import channels
    import general
    import midi
except ImportError:
    pass


class AnalogLabPadView(View):
    """
    Manages pad display and interaction when Analog Lab V is selected.
    - All pads are turned off except bottom-left pad (pad 0)
    - Bottom-left pad glows dim purple normally
    - When pressed, glows blue and sends MIDI CC for preset selection
    """

    ANALOG_LAB_PLUGIN_NAMES = ["Analog Lab", "Analog Lab V"]
    CC_SELECT_PRESET = 30  # TODO: Replace with actual CC number from user
    BOTTOM_LEFT_PAD = 0

    # Colors
    DIM_PURPLE = scale_colour((128, 0, 255), 0.15)  # Dim purple (15% brightness)
    BRIGHT_BLUE = (0, 128, 255)  # Bright blue

    def __init__(self, action_dispatcher, pad_led_writer, fl):
        super().__init__(action_dispatcher)
        self.pad_led_writer = pad_led_writer
        self.fl = fl
        self.is_active = False
        self.pad_pressed = False

    def _is_analog_lab_selected(self):
        """Check if Analog Lab V is the currently selected plugin"""
        selected_plugin = self.fl.get_selected_plugin()
        if selected_plugin is None:
            return False
        return any(name in selected_plugin for name in self.ANALOG_LAB_PLUGIN_NAMES)

    def _update_pad_display(self):
        """Update pad LEDs based on Analog Lab selection state"""
        if self._is_analog_lab_selected():
            if not self.is_active:
                # Activate Analog Lab pad mode
                self.is_active = True
                self._show_analog_lab_pads()
        else:
            if self.is_active:
                # Deactivate Analog Lab pad mode
                self.is_active = False
                self._hide_analog_lab_pads()

    def _show_analog_lab_pads(self):
        """Turn off all pads except bottom-left, which shows dim purple"""
        # Turn off all 16 pads
        for pad in range(16):
            if pad == self.BOTTOM_LEFT_PAD:
                self.pad_led_writer.set_pad_colour(pad, self.DIM_PURPLE)
            else:
                self.pad_led_writer.set_pad_colour(pad, Colours.off)

    def _hide_analog_lab_pads(self):
        """Turn off all pads when leaving Analog Lab mode"""
        for pad in range(16):
            self.pad_led_writer.set_pad_colour(pad, Colours.off)
        self.pad_pressed = False

    def _send_cc_to_selected_channel(self, cc_number, value=127):
        """Send a MIDI CC message to the selected channel"""
        selected_channel = self.fl.selected_channel()
        if selected_channel is None:
            return

        rec_event_parameter = cc_number + channels.getRecEventId(selected_channel)
        midi_value = int((value / 127.0) * midi.FromMIDI_Max)
        mask = midi.REC_MIDIController
        general.processRECEvent(rec_event_parameter, midi_value, mask)

    def _on_show(self):
        self._update_pad_display()

    def _on_hide(self):
        if self.is_active:
            self._hide_analog_lab_pads()

    def handle_OnRefreshAction(self, action):
        """Update pads when plugin selection changes"""
        self._update_pad_display()

    def handle_PadPressAction(self, action):
        """Handle pad press events"""
        if not self.is_active:
            return

        if action.pad == self.BOTTOM_LEFT_PAD:
            # Change to bright blue and send MIDI CC
            self.pad_led_writer.set_pad_colour(self.BOTTOM_LEFT_PAD, self.BRIGHT_BLUE)
            self._send_cc_to_selected_channel(self.CC_SELECT_PRESET, 127)
            self.pad_pressed = True

    def handle_PadReleaseAction(self, action):
        """Handle pad release events"""
        if not self.is_active:
            return

        if action.pad == self.BOTTOM_LEFT_PAD and self.pad_pressed:
            # Return to dim purple
            self.pad_led_writer.set_pad_colour(self.BOTTOM_LEFT_PAD, self.DIM_PURPLE)
            self.pad_pressed = False
