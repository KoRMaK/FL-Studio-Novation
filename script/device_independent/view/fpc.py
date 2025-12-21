from script.colours import Colours
from script.constants import Pads
from script.device_independent.util_view.view import View
from script.fl_constants import RefreshFlags


class Fpc(View):
    num_fpc_pads_per_bank = 16
    num_fpc_pads = num_fpc_pads_per_bank * 2
    colour_component_min = 20

    pad_to_fpc_pad = [4, 5, 6, 7, 12, 13, 14, 15, 0, 1, 2, 3, 8, 9, 10, 11]
    pad_to_fpc_pad.extend([fpc_pad + 16 for fpc_pad in pad_to_fpc_pad])

    def __init__(self, action_dispatcher, pad_led_writer, fl, model):
        super().__init__(action_dispatcher)
        self.action_dispatcher = action_dispatcher
        self.fl = fl
        self.pad_led_writer = pad_led_writer
        self.model = model

        self.note_for_pad = [None] * 16
        self.colour_for_pad = [None] * self.num_fpc_pads_per_bank

    def _on_show(self):
        self._update_notes_for_pads()
        self._update_colours_for_pads()

    def _on_hide(self):
        self._turn_off_leds()

    def handle_PadPressAction(self, action):
        self.fl.send_note_on(self.note_for_pad[action.pad], action.velocity)
        self.pad_led_writer.set_pad_colour(action.pad, Colours.button_pressed)

    def handle_PadReleaseAction(self, action):
        self.fl.send_note_off(self.note_for_pad[action.pad])
        self.pad_led_writer.set_pad_colour(action.pad, self.colour_for_pad[action.pad])

    def handle_FpcBankAction(self, action):
        self._update_notes_for_pads()
        self._update_colours_for_pads()

    def handle_OnRefreshAction(self, action):
        if action.flags & RefreshFlags.PluginNames.value:
            self._update_notes_for_pads()
        if action.flags & RefreshFlags.PluginColours.value:
            self._update_colours_for_pads()

    def _update_notes_for_pads(self):
        for pad in range(Pads.Num.value):
            self.note_for_pad[pad] = self._get_note_for_pad(pad)

    def _get_note_for_pad(self, pad):
        bank_offset = self.model.fpc_active_bank * Pads.Num.value
        fpc_pad = self.pad_to_fpc_pad[pad + bank_offset]
        return self.fl.plugin.get_midi_note_for_pad(self.fl.selected_channel(), fpc_pad)

    def _update_colours_for_pads(self):
        for pad in range(Pads.Num.value):
            self.colour_for_pad[pad] = self._get_colour_for_pad(pad)
        self._set_all_pads(self.colour_for_pad)

    def _get_colour_for_pad(self, pad):
        bank_offset = self.model.fpc_active_bank * Pads.Num.value
        fpc_pad = self.pad_to_fpc_pad[pad + bank_offset]
        r, g, b = self.fl.plugin.get_colour(self.fl.selected_channel(), fpc_pad)
        return (max(self.colour_component_min, r), max(self.colour_component_min, g), max(self.colour_component_min, b))

    def _set_all_pads(self, display):
        for pad, colour in enumerate(display):
            self.pad_led_writer.set_pad_colour(pad, colour)

    def _turn_off_leds(self):
        self._set_all_pads([Colours.off] * Pads.Num.value)
