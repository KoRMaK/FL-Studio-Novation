from script.colours import Colours
from script.commands import ExitStepEditModeCommand
from script.constants import LedLightingType
from script.device_independent.util_view import View


class ExitStepEditLatchModeView(View):
    def __init__(self, action_dispatcher, command_dispatcher, button_led_writer, product_defs):
        super().__init__(action_dispatcher)
        self.command_dispatcher = command_dispatcher
        self.button_led_writer = button_led_writer
        self.product_defs = product_defs

    def _on_show(self):
        self.button_led_writer.set_button_colour(
            self.product_defs.FunctionToButton.get("ExitStepEditLatchMode"),
            Colours.exit_step_edit_latch_mode,
            lighting_type=LedLightingType.Pulsing,
        )

    def _on_hide(self):
        self.button_led_writer.set_button_colour(
            self.product_defs.FunctionToButton.get("ExitStepEditLatchMode"), Colours.off
        )

    def handle_ButtonPressedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("ExitStepEditLatchMode"):
            self.command_dispatcher.dispatch(ExitStepEditModeCommand())
