from script.actions import DefaultOctaveChangedAction
from script.device_independent.util_view.arrow_button_view import ArrowButtonView


class DefaultBankView:
    def __init__(self, action_dispatcher, surface, product_defs, model):
        self.arrow_button_view = ArrowButtonView(
            action_dispatcher,
            surface,
            product_defs,
            decrement_button="ChannelPluginOctaveDown",
            increment_button="ChannelPluginOctaveUp",
            last_page=10,
            on_page_changed=self._on_page_changed,
        )
        self.action_dispatcher = action_dispatcher
        self.model = model

    def show(self):
        self.arrow_button_view.set_active_page(self.model.default_instrument_layout.octave)
        self.arrow_button_view.show()

    def hide(self):
        self.arrow_button_view.hide()

    def _on_page_changed(self):
        self.model.default_instrument_layout.octave = self.arrow_button_view.active_page
        self.action_dispatcher.dispatch(DefaultOctaveChangedAction())
