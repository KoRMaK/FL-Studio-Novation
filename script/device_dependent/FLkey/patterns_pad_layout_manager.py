from script.device_independent.view import (
    ChannelBankNamesHighlightView,
    ChannelBankView,
    PatternSelectBankView,
    PatternSelectView,
)
from util.mapped_pad_led_writer import MappedPadLedWriter


class PatternsPadLayoutManager:
    def __init__(
        self,
        action_dispatcher,
        product_defs,
        fl,
        model,
        pad_led_writer,
        button_led_writer,
        fl_window_manager,
    ):
        self.fl_window_manager = fl_window_manager

        patterns_pad_led_writer = MappedPadLedWriter(
            pad_led_writer, product_defs.Constants.NotesForPadLayout.value[product_defs.PadLayout.Patterns]
        )

        self.views = {
            ChannelBankView(action_dispatcher, button_led_writer, fl, product_defs, model),
            ChannelBankNamesHighlightView(action_dispatcher, fl, model),
            PatternSelectView(action_dispatcher, fl, model, patterns_pad_led_writer),
            PatternSelectBankView(action_dispatcher, button_led_writer, fl, product_defs, model),
        }

    def show(self):
        for view in self.views:
            view.show()

    def hide(self):
        for view in self.views:
            view.hide()
