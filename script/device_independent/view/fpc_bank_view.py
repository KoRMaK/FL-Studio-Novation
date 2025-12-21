from script.actions import FpcBankAction
from script.device_independent.util_view.arrow_button_view import ArrowButtonView


class FpcBankView:
    def __init__(self, action_dispatcher, surface, product_defs, model):
        self.arrow_button_view = ArrowButtonView(
            action_dispatcher,
            surface,
            product_defs,
            increment_button="ChannelPluginPageRight",
            decrement_button="ChannelPluginPageLeft",
            last_page=1,
            on_page_changed=self._on_page_changed,
        )
        self.action_dispatcher = action_dispatcher
        self.model = model

    def show(self):
        self.arrow_button_view.set_active_page(self.model.fpc_active_bank)
        self.arrow_button_view.show()

    def hide(self):
        self.arrow_button_view.hide()

    def _on_page_changed(self):
        self.model.fpc_active_bank = self.arrow_button_view.active_page
        self.action_dispatcher.dispatch(FpcBankAction())
