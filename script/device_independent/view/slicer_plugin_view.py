from script.colours import Colours
from script.constants import Pads
from script.device_independent.util_view.view import View
from script.fl_constants import RefreshFlags, SlicexNoteRange


class SlicerPluginView(View):
    note_offset_for_pad = [4, 5, 6, 7, 8, 9, 10, 11, -4, -3, -2, -1, 0, 1, 2, 3]
    note_offset_per_page = len(note_offset_for_pad)

    def __init__(self, action_dispatcher, pad_led_writer, fl, model, *, available_colour):
        super().__init__(action_dispatcher)
        self.action_dispatcher = action_dispatcher
        self.pad_led_writer = pad_led_writer
        self.fl = fl
        self.model = model
        self.available_colour = available_colour

    @property
    def _note_offset_for_page(self):
        return self.model.slice_x_active_bank * self.note_offset_per_page

    def _note_is_in_range(self, note):
        return SlicexNoteRange.Min <= note <= SlicexNoteRange.Max and self.fl.plugin.get_note_name(
            self.fl.selected_channel(), note
        )

    def _pad_note_is_in_range(self, pad):
        return self._note_is_in_range(self._note_for_pad(pad))

    def _set_all_pads(self, display):
        for pad, colour in enumerate(display):
            self.pad_led_writer.set_pad_colour(pad, colour)

    def _on_show(self):
        self._update_idle_colours()
        self._set_all_pads(self.idle_colours)

    def _on_hide(self):
        self._turn_off_leds()

    def handle_SlicerPluginBankAction(self, action):
        self._update_idle_colours()
        self._set_all_pads(self.idle_colours)

    def handle_OnRefreshAction(self, action):
        if action.flags & RefreshFlags.PluginNames.value:
            self._update_idle_colours()
            self._set_all_pads(self.idle_colours)

    def _note_for_pad(self, pad):
        return self._note_offset_for_page + self.note_offset_for_pad[pad]

    def handle_PadPressAction(self, action):
        note = self._note_for_pad(action.pad)
        if not self._note_is_in_range(note):
            return
        self.fl.send_note_on(note, action.velocity)
        self.pad_led_writer.set_pad_colour(action.pad, Colours.instrument_pad_pressed)

    def handle_PadReleaseAction(self, action):
        note = self._note_for_pad(action.pad)
        if not self._note_is_in_range(note):
            return
        self.fl.send_note_off(note)
        self.pad_led_writer.set_pad_colour(action.pad, self.idle_colours[action.pad])

    def _update_idle_colours(self):
        self.idle_colours = [
            self.available_colour if self._pad_note_is_in_range(pad) else Colours.off for pad in range(Pads.Num.value)
        ]

    def _turn_off_leds(self):
        self._set_all_pads([Colours.off] * Pads.Num.value)
