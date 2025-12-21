from script.actions import HideHighlightsAction, ShowHighlightsAction
from script.device_independent.util_view.view import View


class ShowHighlightsView(View):
    def __init__(self, action_dispatcher, product_defs, model):
        super().__init__(action_dispatcher)
        self.action_dispatcher = action_dispatcher
        self.product_defs = product_defs
        self.model = model

    def _set_show_all_highlights_state(self, highlight_active):
        self.model.show_all_highlights_active = highlight_active

    def handle_ButtonPressedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("ShowHighlights"):
            self._set_show_all_highlights_state(True)
            self.action_dispatcher.dispatch(ShowHighlightsAction())

    def handle_ButtonReleasedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("ShowHighlights"):
            self._set_show_all_highlights_state(False)
            self.action_dispatcher.dispatch(HideHighlightsAction())
