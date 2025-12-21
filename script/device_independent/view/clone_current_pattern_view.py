from script.actions import PatternSelectedAction
from script.constants import PatternSelectionMethod
from script.device_independent.util_view import SingleButtonView, View


class CloneCurrentPatternView(View):
    def __init__(self, action_dispatcher, product_defs, fl, button_led_writer):
        super().__init__(action_dispatcher)
        self.product_defs = product_defs
        self.fl = fl
        self.button_led_writer = button_led_writer
        self.button_view = SingleButtonView(button_led_writer, product_defs, button_function="CloneCurrentPattern")

    def _on_show(self):
        self.button_view.show()

    def _on_hide(self):
        self.button_view.hide()

    def handle_ButtonPressedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("CloneCurrentPattern"):
            self.button_view.set_pressed()
            self.fl.clone_selected_pattern()
            self.action_dispatcher.dispatch(PatternSelectedAction(method=PatternSelectionMethod.ThroughClone))

    def handle_ButtonReleasedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("CloneCurrentPattern"):
            self.button_view.set_not_pressed()
