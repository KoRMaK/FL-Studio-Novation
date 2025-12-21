from script.actions import SlicerPluginBankAction
from script.constants import Notes, Pads
from script.device_independent.util_view.arrow_button_view import ArrowButtonView
from script.device_independent.util_view.view import View
from script.fl_constants import RefreshFlags


class SlicerPluginBankView(View):
    last_page = 8
    slicex_offset = 4

    def __init__(self, action_dispatcher, surface, fl, product_defs, model):
        super().__init__(action_dispatcher)
        self.arrow_button_view = ArrowButtonView(
            action_dispatcher,
            surface,
            product_defs,
            decrement_button="ChannelPluginPageLeft",
            increment_button="ChannelPluginPageRight",
            last_page=self.last_page,
            on_page_changed=self._on_page_changed,
        )
        self.action_dispatcher = action_dispatcher
        self.fl = fl
        self.model = model

    def _update_banking_range(self):
        max_note = Notes.Min.value
        min_note = Notes.Min.value
        for note in range(Notes.Max.value):
            if self.fl.plugin.get_note_name(self.fl.selected_channel(), note):
                min_note = note
                break
        for note in reversed(range(Notes.Max.value)):
            if self.fl.plugin.get_note_name(self.fl.selected_channel(), note):
                max_note = note
                break

        first_page = (min_note + self.slicex_offset) // Pads.Num.value
        last_page = (max_note + self.slicex_offset) // Pads.Num.value
        self.arrow_button_view.set_page_range(first_page, last_page, notify_on_page_change=True)

    def _on_show(self):
        self._update_banking_range()
        self.arrow_button_view.set_active_page(self.model.slice_x_active_bank)
        self.arrow_button_view.show()

    def _on_hide(self):
        self.arrow_button_view.hide()

    def _on_page_changed(self):
        self.model.slice_x_active_bank = self.arrow_button_view.active_page
        self.action_dispatcher.dispatch(SlicerPluginBankAction())

    def handle_OnRefreshAction(self, action):
        if action.flags & (RefreshFlags.ChannelSelection.value | RefreshFlags.PluginNames.value):
            self._update_banking_range()
            self._on_page_changed()
