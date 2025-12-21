from script.colours import Colours
from script.constants import MixerSoloMuteMode
from script.device_independent.util_view import View


class MixerSoloMuteToggleView(View):
    def __init__(self, action_dispatcher, product_defs, model, button_led_writer):
        super().__init__(action_dispatcher)
        self.action_dispatcher = action_dispatcher
        self.product_defs = product_defs
        self.model = model
        self.button_led_writer = button_led_writer

    def _on_show(self):
        self.update_led()

    def _on_hide(self):
        self.turn_off_led()

    def handle_MixerSoloMuteModeChangedAction(self, action):
        self.update_led()

    def calculate_button_colour(self):
        if self.model.mixer_solo_mute_mode == MixerSoloMuteMode.Solo:
            return Colours.button_toggle_on
        return Colours.off

    def update_led(self):
        button = self.product_defs.FunctionToButton.get("ToggleSoloMode")
        colour = self.calculate_button_colour()
        self.button_led_writer.set_button_colour(button, colour)

    def turn_off_led(self):
        button = self.product_defs.FunctionToButton.get("ToggleSoloMode")
        self.button_led_writer.set_button_colour(button, Colours.off)
