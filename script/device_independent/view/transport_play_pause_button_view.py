from script.actions import TransportPlaybackStateChangedAction
from script.colours import Colours
from script.device_independent.util_view.view import View
from script.fl_constants import RefreshFlags


class TransportPlayPauseButtonView(View):
    def __init__(self, action_dispatcher, button_led_writer, fl, product_defs):
        super().__init__(action_dispatcher)
        self.button_led_writer = button_led_writer
        self.fl = fl
        self.product_defs = product_defs

    def _on_show(self):
        self.update_led()

    def _on_hide(self):
        self.turn_off_led()

    def handle_ButtonPressedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("TransportTogglePlayPause"):
            self.fl.transport_toggle_playing()
            self.action_dispatcher.dispatch(TransportPlaybackStateChangedAction())

    def handle_OnRefreshAction(self, action):
        if action.flags & RefreshFlags.TransportStatus.value:
            self.update_led()

    def update_led(self):
        playing = self.fl.transport_is_playing()
        self.button_led_writer.set_button_colour(
            self.product_defs.FunctionToButton.get("TransportTogglePlayPause"),
            Colours.button_toggle_on if playing else Colours.off,
        )

    def turn_off_led(self):
        self.button_led_writer.set_button_colour(
            self.product_defs.FunctionToButton.get("TransportTogglePlayPause"), Colours.off
        )
