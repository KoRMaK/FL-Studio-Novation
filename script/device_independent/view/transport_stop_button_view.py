from script.actions import TransportPlaybackStateChangedAction
from script.device_independent.util_view.view import View


class TransportStopButtonView(View):
    def __init__(self, action_dispatcher, fl, product_defs):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.product_defs = product_defs

    def handle_ButtonPressedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("TransportStop"):
            self.fl.transport_stop()
            self.action_dispatcher.dispatch(TransportPlaybackStateChangedAction())
