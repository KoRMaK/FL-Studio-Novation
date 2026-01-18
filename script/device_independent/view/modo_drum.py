from script.colours import Colours
from script.constants import Pads
from script.device_independent.util_view.view import View
from script.fl_constants import RefreshFlags


class ModoDrum(View):
    """
    Custom view for MODO DRUM with configurable pad-to-MIDI-note mapping.

    Unlike FPC which queries the plugin for MIDI notes, this view uses a direct
    pad-to-note mapping that can be customized for different drum kits.
    """

    colour_component_min = 20

    def __init__(self, action_dispatcher, pad_led_writer, fl, model, pad_to_note_mapping=None, pad_color_mapping=None, channel_selection_manager=None):
        """
        Initialize MODO DRUM view with custom pad mapping.

        Args:
            action_dispatcher: Action dispatcher for event handling
            pad_led_writer: LED writer for pad colors
            fl: FL Studio API wrapper
            model: Application model
            pad_to_note_mapping: List/dict mapping pad index to MIDI note number
                                If None, uses default chromatic mapping starting at C1 (36)
            pad_color_mapping: Dict mapping pad index to (R, G, B) tuple
                              If None, tries to read from plugin or uses default orange
            channel_selection_manager: Optional channel selection manager for independent channel selection
        """
        super().__init__(action_dispatcher)
        self.action_dispatcher = action_dispatcher
        self.fl = fl
        self.pad_led_writer = pad_led_writer
        self.model = model
        self.channel_selection_manager = channel_selection_manager

        # Set up pad-to-note mapping
        if pad_to_note_mapping is None:
            # Default: chromatic mapping starting at C1 (MIDI note 36)
            # Arranged in FPC-style layout
            self.pad_to_note_mapping = [
                40, 41, 42, 43,  # Row 1
                48, 49, 50, 51,  # Row 2
                36, 37, 38, 39,  # Row 3
                44, 45, 46, 47   # Row 4
            ]
        elif isinstance(pad_to_note_mapping, dict):
            # Convert dict to list if needed
            self.pad_to_note_mapping = [pad_to_note_mapping.get(i, 36) for i in range(16)]
        else:
            # Use provided list directly
            self.pad_to_note_mapping = list(pad_to_note_mapping)

        # Ensure we have at least 16 mappings
        while len(self.pad_to_note_mapping) < 16:
            self.pad_to_note_mapping.append(36)

        # Set up color mapping
        self.pad_color_mapping = pad_color_mapping

        self.note_for_pad = [None] * 16
        self.colour_for_pad = [None] * 16
        self.supports_banking = len(self.pad_to_note_mapping) > 16

    def _get_selected_channel(self):
        """Get the selected channel, using channel_selection_manager if available"""
        if self.channel_selection_manager:
            return self.channel_selection_manager.get_active_channel()
        return self.fl.selected_channel()

    def _on_show(self):
        print("modo drum page")
        self._update_notes_for_pads()
        self._update_colours_for_pads()

    def _on_hide(self):
        self._turn_off_leds()

    def handle_PadPressAction(self, action):
        note = self.note_for_pad[action.pad]
        if note is not None:
            self.fl.send_note_on(note, action.velocity, group_channel=self._get_selected_channel())
            self.pad_led_writer.set_pad_colour(action.pad, Colours.button_pressed)

    def handle_PadReleaseAction(self, action):
        note = self.note_for_pad[action.pad]
        if note is not None:
            self.fl.send_note_off(note, group_channel=self._get_selected_channel())
            self.pad_led_writer.set_pad_colour(action.pad, self.colour_for_pad[action.pad])

    def handle_FpcBankAction(self, action):
        """Handle bank changes if mapping supports multiple banks"""
        if self.supports_banking:
            self._update_notes_for_pads()
            self._update_colours_for_pads()

    def handle_OnRefreshAction(self, action):
        if action.flags & RefreshFlags.PluginNames.value:
            self._update_notes_for_pads()
        if action.flags & RefreshFlags.PluginColours.value:
            self._update_colours_for_pads()

    def _update_notes_for_pads(self):
        """Update MIDI notes for each pad based on custom mapping"""
        bank_offset = 0
        if self.supports_banking:
            bank_offset = self.model.fpc_active_bank * Pads.Num.value

        for pad in range(Pads.Num.value):
            mapping_index = pad + bank_offset
            if mapping_index < len(self.pad_to_note_mapping):
                self.note_for_pad[pad] = self.pad_to_note_mapping[mapping_index]
            else:
                self.note_for_pad[pad] = None

    def _update_colours_for_pads(self):
        """Update pad colors - try to get from plugin, fallback to default"""
        for pad in range(Pads.Num.value):
            self.colour_for_pad[pad] = self._get_colour_for_pad(pad)
        self._set_all_pads(self.colour_for_pad)

    def _get_colour_for_pad(self, pad):
        """Get color for pad - uses static mapping, plugin query, or fallback"""
        # First, check if we have a static color mapping
        if self.pad_color_mapping is not None:
            color = self.pad_color_mapping.get(pad)
            if color is not None:
                r, g, b = color
                return (
                    max(self.colour_component_min, r),
                    max(self.colour_component_min, g),
                    max(self.colour_component_min, b)
                )

        # Second, try to get color from plugin using the MIDI note
        try:
            note = self.note_for_pad[pad]
            if note is not None:
                r, g, b = self.fl.plugin.get_colour(self._get_selected_channel(), note)
                return (
                    max(self.colour_component_min, r),
                    max(self.colour_component_min, g),
                    max(self.colour_component_min, b)
                )
        except:
            pass

        # Fallback to orange color (drum color)
        return Colours.fpc_orange.value

    def _set_all_pads(self, display):
        for pad, colour in enumerate(display):
            self.pad_led_writer.set_pad_colour(pad, colour)

    def _turn_off_leds(self):
        self._set_all_pads([Colours.off] * Pads.Num.value)
