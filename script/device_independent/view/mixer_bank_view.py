from script.commands import RequestDisableMixerBankingCommand, RequestEnableMixerBankingCommand
from script.device_independent.view.mixer_bank_button_view import MixerBankButtonView
from script.device_independent.view.mixer_bank_highlight_view import MixerBankHighlightView


class MixerBankView:
    def __init__(self, action_dispatcher, command_dispatcher, button_led_writer, fl, product_defs, model):
        self.command_dispatcher = command_dispatcher
        self.number_of_times_banking_enabled = 0

        self.views = {
            MixerBankButtonView(action_dispatcher, button_led_writer, fl, product_defs, model),
            MixerBankHighlightView(action_dispatcher, fl, model),
        }

    def show(self):
        self.command_dispatcher.register(self, RequestEnableMixerBankingCommand)
        self.command_dispatcher.register(self, RequestDisableMixerBankingCommand)

    def hide(self):
        self.command_dispatcher.unregister(self, RequestDisableMixerBankingCommand)
        self.command_dispatcher.unregister(self, RequestEnableMixerBankingCommand)

    def handle_RequestEnableMixerBankingCommand(self, command):
        if self.number_of_times_banking_enabled == 0:
            for view in self.views:
                view.show()

        self.number_of_times_banking_enabled = self.number_of_times_banking_enabled + 1

    def handle_RequestDisableMixerBankingCommand(self, command):
        self.number_of_times_banking_enabled = self.number_of_times_banking_enabled - 1

        if self.number_of_times_banking_enabled == 0:
            for view in self.views:
                view.hide()
