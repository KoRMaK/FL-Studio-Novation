from script.device_independent.util_view.view import View

try:
    import channels
    import general
    import midi
    import ui
except ImportError:
    pass


class AnalogLabPresetButtonView(View):
    """
    Handles preset navigation for Arturia Analog Lab V using MIDI CC messages.
    - CC #28 for Previous Preset
    - CC #29 for Next Preset

    Works with both Launchkey (MixerBankLeft/Right) and FLkey (SelectPreviousPreset/SelectNextPreset).
    """

    ANALOG_LAB_PLUGIN_NAMES = ["Analog Lab", "Analog Lab V"]
    CC_PRESET_PREVIOUS = 28
    CC_PRESET_NEXT = 29

    def __init__(self, action_dispatcher, fl, product_defs):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.product_defs = product_defs

        # Determine which button mapping to use based on product
        self.prev_button_key = None
        self.next_button_key = None

        #print("inside analog button preset")

        # Check if this is a Launchkey (has MixerBankLeft/Right)
        if self.product_defs.FunctionToButton.get("ChannelPluginPageLeft") is not None:
            self.prev_button_key = "ChannelPluginPageLeft"
            self.next_button_key = "ChannelPluginPageRight"
        # Check if this is FLkey (has SelectPreviousPreset/SelectNextPreset)
        elif self.product_defs.FunctionToButton.get("SelectPreviousPreset") is not None:
            self.prev_button_key = "SelectPreviousPreset"
            self.next_button_key = "SelectNextPreset"

        #print(self.next_button_key)

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
        #print("analog lab handle_ButtonPressedAction")
        # Only handle if Analog Lab is selected and buttons are configured
        if not self._is_analog_lab_selected() or self.prev_button_key is None:
            return

        # print("onto action buttons")
        # print(action.button)
        # print(dir(action))
        # print(self.product_defs.FunctionToButton.get("PageLeft"))
        # print(self.prev_button_key)
        # print(self.product_defs.FunctionToButton.get(self.prev_button_key))
        # Handle Previous Preset button
        if action.button == self.product_defs.FunctionToButton.get(self.prev_button_key):
          # self._send_cc_to_selected_channel(self.CC_PRESET_PREVIOUS, 127)
          ui.up()
          # print("up preset was clicked")


        # Handle Next Preset button
        elif action.button == self.product_defs.FunctionToButton.get(self.next_button_key):
          # self._send_cc_to_selected_channel(self.CC_PRESET_NEXT, 127)
          ui.down()
          # print("up preset was clicked")
