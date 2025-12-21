from script.actions import PatternSelectedAction
from script.constants import PatternSelectionMethod
from script.device_independent.util_view import SingleButtonView, View
from script.fl_constants import FlConstants


class SelectNewPatternView(View):
    def __init__(self, action_dispatcher, product_defs, fl, button_led_writer):
        super().__init__(action_dispatcher)
        self.product_defs = product_defs
        self.fl = fl
        self.button_led_writer = button_led_writer
        self.button_view = SingleButtonView(button_led_writer, product_defs, button_function="SelectNewPattern")

    def _on_show(self):
        self.button_view.show()

    def _on_hide(self):
        self.button_view.hide()

    def handle_ButtonPressedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("SelectNewPattern"):
            self.button_view.set_pressed()
            self.select_first_empty_pattern()

    def handle_ButtonReleasedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("SelectNewPattern"):
            self.button_view.set_not_pressed()

    def select_first_empty_pattern(self):
        for pattern_index in range(FlConstants.FirstPatternIndex.value, self.fl.get_last_pattern_index() + 1):
            if self.fl.is_pattern_default(pattern_index):
                self.fl.select_pattern(pattern_index)
                self.action_dispatcher.dispatch(PatternSelectedAction(method=PatternSelectionMethod.ThroughNew))
                return
