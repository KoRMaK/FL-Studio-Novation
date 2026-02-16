from script.colour_utils import clamp_brightness
from script.colours import Colours
from script.constants import Pads, Pots
from script.device_independent.util_view.view import View
from script.fl_constants import RefreshFlags
from script.plugin import plugin_parameter_mappings


class Default(View):
    colour_off = Colours.off.value
    colour_pressed = Colours.pad_pressed.value

    semitones_per_octave = 12
    maximum_note = 131

    maximum_not_pressed_brightness = 200
    ANALOG_LAB_PLUGIN_NAMES = ["Analog Lab", "Analog Lab V"]

    def __init__(self, action_dispatcher, pad_led_writer, fl, model, channel_selection_manager=None):
        super().__init__(action_dispatcher)
        self.action_dispatcher = action_dispatcher
        self.fl = fl
        self.model = model
        self.channel_selection_manager = channel_selection_manager
        self.active_note_for_pad = {}
        self.pad_for_active_note = {}
        self.pad_led_writer = pad_led_writer
        self.colour_primary = Colours.off
        self.colour_secondary = Colours.off
        self.pressed_page_indicator_pads = set()  # Track which page indicator pads are pressed

    def _is_analog_lab_selected(self):
        """Check if Analog Lab V is the currently selected plugin"""
        selected_plugin = self.fl.get_selected_plugin()
        if selected_plugin is None:
            return False
        return any(name in selected_plugin for name in self.ANALOG_LAB_PLUGIN_NAMES)

    def _get_primary_and_secondary_colour(self):
        if self.channel_selection_manager:
            active_channel = self.channel_selection_manager.get_active_channel()
        else:
            active_channel = None
        r, g, b = clamp_brightness(self.fl.get_channel_colour(group_channel=active_channel), maximum=self.maximum_not_pressed_brightness)
        dim_scaling_divisor = 3
        return (r, g, b), (r // dim_scaling_divisor, g // dim_scaling_divisor, b // dim_scaling_divisor)

    @classmethod
    def _note_is_valid(cls, note):
        if note is None:
            return False
        return 0 <= note <= cls.maximum_note

    def _note_value_for_pad(self, pad):
        if (note := self.model.default_instrument_layout.note_offset_for_pad.get(pad)) is not None:
            return self.model.default_instrument_layout.octave * self.semitones_per_octave + note.value
        return None

    def _colour_for_pad(self, pad):
        note = self._note_value_for_pad(pad)
        if not self._note_is_valid(note):
            return self.colour_off

        # Show pad as held if any pad with the same note is held
        is_held = self.pad_for_active_note.get(note) is not None
        if is_held:
            return self.colour_pressed
        if self.model.default_instrument_layout.note_offset_for_pad[pad].is_primary:
            return self.colour_primary
        return self.colour_secondary

    def _pad_is_responsible_for_note_off(self, pad, note):
        return self.pad_for_active_note.get(note) == pad

    def _send_note_on_for_pad(self, pad, note, velocity):
        self.active_note_for_pad[pad] = note
        self.pad_for_active_note[note] = pad
        # Send note to the independently selected channel if available
        if self.channel_selection_manager:
            group_channel = self.channel_selection_manager.get_active_channel()
            self.fl.send_note_on(note, velocity, group_channel=group_channel)
        else:
            self.fl.send_note_on(note, velocity)

    def _send_note_off(self, note):
        self.pad_for_active_note.pop(note)
        # Send note to the independently selected channel if available
        if self.channel_selection_manager:
            group_channel = self.channel_selection_manager.get_active_channel()
            self.fl.send_note_off(note, group_channel=group_channel)
        else:
            self.fl.send_note_off(note)

    def handle_DefaultOctaveChangedAction(self, action):
        self._update_all_leds()

    def handle_OnRefreshAction(self, action):
        # Update the display with a potential new channel color when another channel is selected or
        # when the color of a channel is changed
        if action.flags & (RefreshFlags.ChannelSelection.value | RefreshFlags.PerformanceLayout.value):
            old_colours = self.colour_primary, self.colour_secondary
            self.colour_primary, self.colour_secondary = self._get_primary_and_secondary_colour()
            if old_colours != (self.colour_primary, self.colour_secondary):
                self._update_all_leds()

    def _on_show(self):
        self.colour_primary, self.colour_secondary = self._get_primary_and_secondary_colour()
        self._update_all_leds()

    def _on_hide(self):
        self._turn_off_all_leds()

    def _calculate_num_pot_pages(self):
        """
        Calculate number of plugin parameter pages for the currently selected channel.
        Returns number of pages where each page contains up to 8 pot parameters.
        Includes an additional custom page (CC 4030+) for all plugins.
        Page indicators show on TOP row (pads 0-7).
        """
        if self.channel_selection_manager:
            channel = self.channel_selection_manager.get_active_channel()
        else:
            channel = self.fl.selected_channel()

        if channel is None:
            return 0

        plugin = self.fl.get_plugin_for_channel(channel)
        if plugin is None or plugin not in plugin_parameter_mappings:
            return 0

        all_parameters = plugin_parameter_mappings[plugin]
        if not all_parameters:
            return 0

        # Calculate pages based on 8 pots per page
        num_controls = Pots.Num.value
        num_pages = (len(all_parameters) + num_controls - 1) // num_controls

        # Add 2 for the hybrid page + custom page
        return num_pages + 2

    def _update_all_leds(self):
        # Skip if Analog Lab is selected (let AnalogLabPadView handle it)
        # if self._is_analog_lab_selected():
        #     return

        num_pages = self._calculate_num_pot_pages()

        # If plugin has pot pages, show ONLY page indicators (turn off instrument layout)
        if num_pages > 0:
            # Turn off all pads first
            for pad in range(Pads.Num.value):
                self.pad_led_writer.set_pad_colour(pad, Colours.off.value)

            # Get current active page
            current_page = self.model.plugin_parameter_active_page if self.model else 0

            # Light up page indicator pads on TOP row (pads 0-7)
            for pad in range(min(8, Pads.Num.value)):
                if pad < num_pages:
                    # The last two pages are custom (hybrid + custom CC) - use seafoam colors
                    is_custom_page = (pad >= num_pages - 2)

                    # Choose color based on state
                    if pad in self.pressed_page_indicator_pads:
                        # Pressed - show bright teal (custom) or teal/aqua (regular)
                        colour = Colours.custom_page_indicator_pressed.value if is_custom_page else Colours.plugin_page_indicator_pressed.value
                    elif pad == current_page:
                        # Active page - bright seafoam (custom) or brighter blue (regular)
                        colour = Colours.custom_page_indicator_active.value if is_custom_page else Colours.plugin_page_indicator_active.value
                    else:
                        # Inactive page - dim seafoam (custom) or normal blue (regular)
                        colour = Colours.custom_page_indicator.value if is_custom_page else Colours.plugin_page_indicator.value
                    self.pad_led_writer.set_pad_colour(pad, colour)
        else:
            # No pot pages - show normal instrument layout
            for pad in range(Pads.Num.value):
                colour = self._colour_for_pad(pad)
                self.pad_led_writer.set_pad_colour(pad, colour)

    def _turn_off_all_leds(self):
        for pad in range(Pads.Num.value):
            self.pad_led_writer.set_pad_colour(pad, Colours.off)

    def handle_PadPressAction(self, action):
        # Skip if Analog Lab is selected (let AnalogLabPadView handle it)
        # if self._is_analog_lab_selected():
        #     return

        num_pages = self._calculate_num_pot_pages()

        # If plugin has pot pages and this is a page indicator pad on TOP row (pads 0-7), switch page
        if num_pages > 0 and action.pad < 8 and action.pad < num_pages:
            # Mark pad as pressed for visual feedback (teal/aqua color)
            self.pressed_page_indicator_pads.add(action.pad)

            # Switch to the pressed page (pad 0 = page 0, pad 1 = page 1, etc.)
            if self.model:
                self.model.plugin_parameter_active_page = action.pad
                print(f"Default view: Switched to pot parameter page {action.pad}")
                # Dispatch an action to notify PluginParameterView to update
                from script.actions import PluginParameterPageChangedAction
                self.action_dispatcher.dispatch(PluginParameterPageChangedAction())

            # Update LEDs to show pressed state
            self._update_all_leds()
            return  # Don't send MIDI note

        # If no pot pages, use normal instrument layout
        if num_pages == 0:
            note = self._note_value_for_pad(action.pad)
            if not self._note_is_valid(note):
                return

            self._send_note_on_for_pad(action.pad, note, action.velocity)
            self._update_all_leds()

    def handle_PadReleaseAction(self, action):
        # Skip if Analog Lab is selected (let AnalogLabPadView handle it)
        # if self._is_analog_lab_selected():
        #     return

        num_pages = self._calculate_num_pot_pages()

        # If this is a page indicator pad, remove pressed state and update LEDs
        if num_pages > 0 and action.pad < 8:
            self.pressed_page_indicator_pads.discard(action.pad)
            self._update_all_leds()
            return

        # Normal instrument layout behavior
        note_for_pad = self.active_note_for_pad.pop(action.pad, None)
        if note_for_pad is not None:
            if self._pad_is_responsible_for_note_off(action.pad, note_for_pad):
                self._send_note_off(note_for_pad)
                self._update_all_leds()

    def handle_DefaultInstrumentLayoutMappingChangedAction(self, action):
        self._update_all_leds()
