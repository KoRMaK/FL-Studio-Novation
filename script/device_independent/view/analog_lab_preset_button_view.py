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
    Handles preset navigation for Arturia plugins (Analog Lab V, SEM V3) using ui.up()/ui.down().

    Supports multiple button sets:
    - Launchkey: MixerBankLeft/Right
    - FLkey: ChannelPluginPageLeft/Right

    When an Arturia plugin is selected, these buttons navigate presets instead of their normal functions.
    """

    ARTURIA_STYLE_PLUGIN_NAMES = ["Analog Lab", "Analog Lab V", "SEM V3"]
    CC_PRESET_PREVIOUS = 28
    CC_PRESET_NEXT = 29

    def __init__(self, action_dispatcher, fl, product_defs, channel_selection_manager=None):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.product_defs = product_defs
        self.channel_selection_manager = channel_selection_manager

        # Track all button sets that can navigate presets (devices may have multiple sets)
        self.button_sets = []

        #print("inside analog button preset")

        # Check for FLkey-style plugin page buttons (ChannelPluginPageLeft/Right)
        if self.product_defs.FunctionToButton.get("ChannelPluginPageLeft") is not None:
            self.button_sets.append({
                "prev": "ChannelPluginPageLeft",
                "next": "ChannelPluginPageRight"
            })

        # Check for mixer bank buttons (MixerBankLeft/Right) - Launchkey
        if self.product_defs.FunctionToButton.get("MixerBankLeft") is not None:
            self.button_sets.append({
                "prev": "MixerBankLeft",
                "next": "MixerBankRight"
            })

    def _is_analog_lab_selected(self):
        """Check if an Arturia-style plugin is the currently selected plugin"""
        selected_plugin = self.fl.get_selected_plugin()
        if selected_plugin is None:
            return False
        return any(name in selected_plugin for name in self.ARTURIA_STYLE_PLUGIN_NAMES)

    def _send_cc_to_selected_channel(self, cc_number, value=127):
        """Send a MIDI CC message to the selected channel"""
        if self.channel_selection_manager:
            selected_channel = self.channel_selection_manager.get_active_channel()
        else:
            selected_channel = self.fl.selected_channel()

        if selected_channel is None:
            return

        rec_event_parameter = cc_number + channels.getRecEventId(selected_channel)
        midi_value = int((value / 127.0) * midi.FromMIDI_Max)
        mask = midi.REC_MIDIController
        general.processRECEvent(rec_event_parameter, midi_value, mask)

    def handle_ButtonPressedAction(self, action):
        # Only handle if Analog Lab is selected and we have button sets configured
        if not self._is_analog_lab_selected() or not self.button_sets:
            return

        # Focus the plugin window to ensure commands reach the Arturia plugin
        #self.fl.ui.focus_channel_plugin_window()

        # Check if any of our configured button sets match this action
        for button_set in self.button_sets:
            prev_button = self.product_defs.FunctionToButton.get(button_set["prev"])
            next_button = self.product_defs.FunctionToButton.get(button_set["next"])

            # debug here.
            if action.button == prev_button:
                self._send_cc_to_selected_channel(self.CC_PRESET_PREVIOUS, 127)
                ui.up()
                print(f"Arturia preset previous - button set: {button_set['prev']}")
                return
            elif action.button == next_button:
                ui.down()
                self._send_cc_to_selected_channel(self.CC_PRESET_NEXT, 127)
                print(f"Arturia preset next - button set: {button_set['next']}")
                return
