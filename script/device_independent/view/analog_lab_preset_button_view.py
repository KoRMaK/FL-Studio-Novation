from script.device_independent.util_view.view import View

try:
    import channels
    import general
    import midi
except ImportError:
    pass


class AnalogLabPresetButtonView(View):
    """
    Handles preset navigation for Arturia Analog Lab V using MIDI CC messages.
    - CC #28 for Previous Preset
    - CC #29 for Next Preset
    """

    ANALOG_LAB_PLUGIN_NAMES = ["Analog Lab", "Analog Lab V"]
    CC_PRESET_PREVIOUS = 28
    CC_PRESET_NEXT = 29

    def __init__(self, action_dispatcher, fl, product_defs):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.product_defs = product_defs

    def _is_analog_lab_selected(self):
        """Check if Analog Lab V is the currently selected plugin"""
        selected_plugin = self.fl.get_selected_plugin()
        if selected_plugin is None:
            return False
        return any(name in selected_plugin for name in self.ANALOG_LAB_PLUGIN_NAMES)

    def _send_cc_to_selected_channel(self, cc_number, value=127):
        """Send a MIDI CC message to the selected channel"""
        selected_channel = self.fl.selected_channel()
        if selected_channel is None:
            return

        rec_event_parameter = cc_number + channels.getRecEventId(selected_channel)
        midi_value = int((value / 127.0) * midi.FromMIDI_Max)
        mask = midi.REC_MIDIController
        general.processRECEvent(rec_event_parameter, midi_value, mask)

    def handle_ButtonPressedAction(self, action):
        # Only handle if Analog Lab is selected
        if not self._is_analog_lab_selected():
            return

        # Handle Previous Preset (Left button)
        if action.button == self.product_defs.FunctionToButton.get("MixerBankLeft"):
            self._send_cc_to_selected_channel(self.CC_PRESET_PREVIOUS, 127)

        # Handle Next Preset (Right button)
        elif action.button == self.product_defs.FunctionToButton.get("MixerBankRight"):
            self._send_cc_to_selected_channel(self.CC_PRESET_NEXT, 127)
