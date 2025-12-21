from script.colour_utils import clamp_brightness
from script.colours import Colours
from script.constants import Pads
from script.device_independent.util_view.view import View
from script.fl_constants import RefreshFlags


class Default(View):
    colour_off = Colours.off.value
    colour_pressed = Colours.pad_pressed.value

    semitones_per_octave = 12
    maximum_note = 131

    maximum_not_pressed_brightness = 200

    def __init__(self, action_dispatcher, pad_led_writer, fl, model):
        super().__init__(action_dispatcher)
        self.action_dispatcher = action_dispatcher
        self.fl = fl
        self.model = model
        self.active_note_for_pad = {}
        self.pad_for_active_note = {}
        self.pad_led_writer = pad_led_writer
        self.colour_primary = Colours.off
        self.colour_secondary = Colours.off

    def _get_primary_and_secondary_colour(self):
        r, g, b = clamp_brightness(self.fl.get_channel_colour(), maximum=self.maximum_not_pressed_brightness)
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
        self.fl.send_note_on(note, velocity)

    def _send_note_off(self, note):
        self.pad_for_active_note.pop(note)
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

    def _update_all_leds(self):
        for pad in range(Pads.Num.value):
            colour = self._colour_for_pad(pad)
            self.pad_led_writer.set_pad_colour(pad, colour)

    def _turn_off_all_leds(self):
        for pad in range(Pads.Num.value):
            self.pad_led_writer.set_pad_colour(pad, Colours.off)

    def handle_PadPressAction(self, action):
        note = self._note_value_for_pad(action.pad)
        if not self._note_is_valid(note):
            return

        self._send_note_on_for_pad(action.pad, note, action.velocity)
        self._update_all_leds()

    def handle_PadReleaseAction(self, action):
        note_for_pad = self.active_note_for_pad.pop(action.pad, None)
        if note_for_pad is not None:
            if self._pad_is_responsible_for_note_off(action.pad, note_for_pad):
                self._send_note_off(note_for_pad)
                self._update_all_leds()

    def handle_DefaultInstrumentLayoutMappingChangedAction(self, action):
        self._update_all_leds()
