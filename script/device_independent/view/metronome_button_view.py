from script.actions import MetronomeStateChangedAction
from script.device_independent.util_view.view import View


class MetronomeButtonView(View):
    def __init__(self, action_dispatcher, fl, product_defs):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.product_defs = product_defs

    def handle_ButtonPressedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("ToggleMetronome"):
            self.fl.toggle_metronome()
            self.action_dispatcher.dispatch(MetronomeStateChangedAction())
