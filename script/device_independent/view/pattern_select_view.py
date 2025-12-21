from script.actions import PatternSelectedAction
from script.colour_utils import clamp_brightness
from script.colours import Colours
from script.constants import Pads, PatternSelectionMethod
from script.device_independent.util_view import View
from script.device_independent.view.active_pattern_bank import ActivePatternBank
from script.fl_constants import RefreshFlags


class PatternSelectView(View):
    min_pattern_colour_brightness = 100

    def __init__(self, action_dispatcher, fl, model, pad_led_writer):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.model = model
        self.pad_led_writer = pad_led_writer
        self.active_pattern_bank = ActivePatternBank(fl, model)

    def _on_show(self):
        self.update_leds()

    def _on_hide(self):
        self.turn_off_leds()

    @property
    def pad_index_to_pattern_index(self):
        patterns = self.active_pattern_bank.get_patterns()
        pads = [8, 9, 10, 11, 12, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7]
        return dict(zip(pads, patterns))

    def handle_PatternSelectBankChangedAction(self, action):
        self.update_leds()

    def handle_PadPressAction(self, action):
        if action.pad in self.pad_index_to_pattern_index:
            self.fl.select_pattern(self.pad_index_to_pattern_index[action.pad])
            self.action_dispatcher.dispatch(PatternSelectedAction(method=PatternSelectionMethod.Explicit))

    def handle_OnRefreshAction(self, action):
        flags_to_act_on = RefreshFlags.Pattern.value | RefreshFlags.PerformanceLayout.value
        if action.flags & flags_to_act_on:
            self.update_leds()

    def idle_pattern_colour(self, pattern_index):
        return clamp_brightness(self.fl.get_pattern_colour(pattern_index), minimum=self.min_pattern_colour_brightness)

    def update_leds(self):
        self.turn_off_leds()
        for pad, pattern in self.pad_index_to_pattern_index.items():
            self.pad_led_writer.set_pad_colour(pad, self.colour_for_pattern(pattern))

    def colour_for_pattern(self, pattern):
        if pattern == self.fl.get_selected_pattern_index():
            return Colours.pattern_selected
        if self.fl.is_pattern_default(pattern):
            return Colours.off
        return self.idle_pattern_colour(pattern)

    def turn_off_leds(self):
        for pad in range(Pads.Num.value):
            self.pad_led_writer.set_pad_colour(pad, Colours.off)
